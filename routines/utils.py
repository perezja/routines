import contextlib
import logging
import os

from WDL import Document, Workflow, SourcePosition, ReadSourceResult, Walker, Env, Value, Type, Error, values_from_json, values_to_json, parse_tasks
from WDL.CLI import runner_input as runner_input_local, runner_input_help, runner_input_value, make_read_source, validate_input_path
from WDL.runtime.config import Loader as config_loader 
from WDL.Tree import _load_async

from typing import List, Optional, Callable, Dict, Any, Awaitable, Union

@contextlib.contextmanager
def cd(cd_path):
    saved_path = os.getcwd()
    os.chdir(cd_path)
    yield
    os.chdir(saved_path)

# from WDL.CLI: copied to supply async event loop from main loop in WorkflowController grpc server 
def runner_input(
    event_loop,
    doc,
    inputs,
    input_file,
    empty,
    none,
    task=None,
    check_required=True,
    downloadable=None,
    root="/",
):
    """
    - Determine the target workflow/task
    - Check types of supplied inputs
    - Check all required inputs are supplied
    - Return inputs as Env.Bindings[Value.Base]
    """

    # resolve target
    target = None
    if task:
        target = next((t for t in doc.tasks if t.name == task), None)
        if not target:
            raise Error.InputError(f"no such task {task} in document")
    elif doc.workflow:
        target = doc.workflow
    elif len(doc.tasks) == 1:
        target = doc.tasks[0]
    elif len(doc.tasks) > 1:
        raise Error.InputError(
            "specify --task for WDL document with multiple tasks and no workflow"
        )
    else:
        raise Error.InputError("Empty WDL document")
    assert target

    # build up an values env of the provided inputs
    available_inputs = target.available_inputs
    input_env = runner_input_json_file(
        event_loop,
        available_inputs,
        (target.name if isinstance(target, Workflow) else ""),
        input_file,
        downloadable,
        root,
    )
    json_keys = set(b.name for b in input_env)

    # set explicitly empty arrays or strings
    for empty_name in empty or []:
        try:
            decl = available_inputs[empty_name]
        except KeyError:
            runner_input_help(target)
            raise Error.InputError(f"No such input to {target.name}: {empty_name}")
        if isinstance(decl.type, Type.Array):
            if decl.type.nonempty:
                raise Error.InputError(
                    f"Cannot set input {str(decl.type)} {decl.name} to empty array"
                )
            input_env = input_env.bind(empty_name, Value.Array(decl.type.item_type, []), decl)
        elif isinstance(decl.type, Type.String):
            input_env = input_env.bind(empty_name, Value.String(""), decl)
        else:
            msg = f"Cannot set {str(decl.type)} {decl.name} to empty array or string"
            if decl.type.optional:
                msg += "; perhaps you want --none " + decl.name
            raise Error.InputError(msg)

    # set explicitly None values
    for none_name in none or []:
        try:
            decl = available_inputs[none_name]
        except KeyError:
            runner_input_help(target)
            raise Error.InputError(f"No such input to {target.name}: {none_name}")
        if not decl.type.optional:
            raise Error.InputError(
                f"Cannot set non-optional input {str(decl.type)} {decl.name} to None"
            )
        input_env = input_env.bind(none_name, Value.Null(), decl)

    # preprocess command-line inputs: merge adjacent elements ("x=", "y") into ("x=y"), allowing
    # shell filename completion on y
    inputs = list(inputs)
    i = 0
    while i < len(inputs):
        len_i = len(inputs[i])
        if len_i > 1 and inputs[i].find("=") == len_i - 1 and i + 1 < len(inputs):
            inputs[i] = inputs[i] + inputs[i + 1]
            del inputs[i + 1]
        i += 1

    # add in command-line inputs
    for one_input in inputs:
        # parse [namespace], name, and value
        buf = one_input.split("=", 1)
        if not one_input or not one_input[0].isalpha() or len(buf) != 2 or not buf[0]:
            runner_input_help(target)
            raise Error.InputError("Invalid input name=value pair: " + one_input)
        name, s_value = buf

        # find corresponding input declaration
        decl = available_inputs.get(name)

        if not decl:
            # allow arbitrary runtime overrides
            nmparts = name.split(".")
            runtime_idx = next((i for i, term in enumerate(nmparts) if term in ("runtime",)), -1)
            if runtime_idx >= 0 and len(nmparts) > (runtime_idx + 1):
                decl = available_inputs.get(".".join(nmparts[:runtime_idx] + ["_runtime"]))

        if not decl:
            runner_input_help(target)
            raise Error.InputError(f"No such input to {target.name}: {buf[0]}")

        # create a Value based on the expected type
        v = runner_input_value(s_value, decl.type, downloadable, root)

        # insert value into input_env
        existing = input_env.get(name)
        if existing and name not in json_keys:
            if isinstance(v, Value.Array):
                assert isinstance(existing, Value.Array) and v.type.coerces(existing.type)
                existing.value.extend(v.value)
            else:
                runner_input_help(target)
                raise Error.InputError(f"non-array input {buf[0]} duplicated")
        else:
            input_env = input_env.bind(name, v, decl)
            json_keys.discard(name)  # command-line overrides JSON input

    # check for missing inputs
    if check_required:
        missing_inputs = values_to_json(target.required_inputs.subtract(input_env))
        if missing_inputs:
            runner_input_help(target)
            raise Error.InputError(
                f"missing required inputs for {target.name}: {', '.join(missing_inputs.keys())}"
            )

    # make a pass over the Env to create a dict for Cromwell-style input JSON
    return (
        target,
        input_env,
        values_to_json(input_env, namespace=(target.name if isinstance(target, Workflow) else "")),
    )


def runner_input_json_file(event_loop, available_inputs, namespace, input_file, downloadable, root):
    """
    Load user-supplied inputs JSON file, if any
    """
    ans = Env.Bindings()

    if input_file:
        input_file = input_file.strip()
    if input_file:
        import yaml  # delayed heavy import

        input_json = None
        if input_file[0] == "{":
            input_json = input_file
        elif input_file == "-":
            input_json = sys.stdin.read()
        else:
            input_json = (
                event_loop.run_until_complete(make_read_source(False)(input_file, [], None)).source_text
            )
        input_json = yaml.safe_load(input_json)
        if not isinstance(input_json, dict):
            raise Error.InputError("check JSON input; expected top-level object")
        try:
            ans = values_from_json(input_json, available_inputs, namespace=namespace)
        except Error.InputError as exn:
            raise Error.InputError("check JSON input; " + exn.args[0])

        ans = Value.rewrite_env_paths(
            ans,
            lambda v: validate_input_path(
                v.value, isinstance(v, Value.Directory), downloadable, root
            ),
        )

    return ans

def load_config():
    return config_loader(logging.getLogger(__name__))

def load_wdl(
    event_loop, 
    uri: str,
    path: Optional[List[str]] = None,
    check_quant: bool = True,
    read_source: Optional[
        Callable[[str, List[str], Optional[Document]], Awaitable[ReadSourceResult]]
    ] = None,
    import_max_depth: int = 10,
    importer: Optional[Document] = None,
) -> Document:
 	# asyncio.get_event_loop()
	
    doc = event_loop.run_until_complete(
        _load_async(
            uri,
            path=path,
            importer=importer,
            check_quant=check_quant,
            read_source=read_source,
            import_max_depth=import_max_depth,
        )
    )
    Walker.SetParents()(doc)
    return doc

def load_input_local(doc, input_file, data_path=None):

    input_file = os.path.abspath(input_file)
    if not data_path:
        # assume data in same location as JSON input file
        data_path=os.path.dirname(input_file)
        print("using data_path={}".format(data_path))

    with cd(data_path):

        inputs = runner_input_local(doc=doc, inputs=[], input_file=input_file, empty=[], none=[])                                                                                          
    return inputs[1]


def load_input(event_loop, doc, input_file, data_path=None):

    input_file = os.path.abspath(input_file)
    if not data_path:
        # assume data in same location as JSON input file
        data_path=os.path.dirname(input_file)

    with cd(data_path):

        inputs = runner_input(event_loop, doc=doc, inputs=[], input_file=input_file, empty=[], none=[])                                                                                          
    return inputs[1]

def extract_source(sp: SourcePosition):
    txt = list() 
    with open(sp.uri, 'rt') as fp:
        i=0
        while i<sp.line-1:
            fp.readline(); i=i+1
        txt.append(fp.readline()[sp.column-1:])
        while i<sp.end_line-1:
            txt.append(fp.readline()); i=i+1
        txt.append(fp.readline()[:sp.end_column])

    return(' '.join(txt))            

def unmarshall_input(task, input_json, downloadable=None, root="/"):

    if not isinstance(input_json, dict):
        raise Error.InputError("check JSON input; expected top-level object")
    try:
        ans = values_from_json(input_json, task.available_inputs, namespace=task.name)
    except WDL.Error.InputError as exn:
        raise WDL.Error.InputError("check JSON input; " + exn.args[0])

    ans = Value.rewrite_env_paths(
        ans,
        lambda v: validate_input_path(
            v.value, isinstance(v, Value.Directory), downloadable, root
        ),
    )

    return ans

def unmarshall_task(task_str, task_digest):

    tasks = parse_tasks(task_str)
    assert len(tasks) == 1; task = tasks[0]
    task.typecheck()
    task._digest = task_digest

    return task




