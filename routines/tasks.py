import logging

from WDL import values_to_json 
from WDL.runtime.task import run_local_task, _eval_task_inputs, InputStdLib 
from WDL.runtime import task_container

from utils import unmarshall_task, unmarshall_input, load_config

from cluster import app 

def _eval_command(logger, cfg, task, inputs, run_id = None, run_dir = None, logger_prefix = None,
    _run_id_stack = None, _cache = None, _plugins = None,):
    container =  task_container.new(cfg, logger, run_id, run_dir)
    container_env=_eval_task_inputs(logger, task, inputs, container) 
    stdlib = InputStdLib(task.effective_wdl_version, logger, container)
    cmd = task.command.eval(container_env, stdlib).value

@app.task
def run_task( 
    task_str,
    task_digest,
    task_inputs,
    run_id = None,
    run_dir = None,
    logger_prefix = None,
    _run_id_stack = None,
    _cache = None,
    _plugins = None,
): 	

    cfg = load_config()

    task = unmarshall_task(task_str, task_digest)
    input_env = unmarshall_input(task, task_inputs)

    sub_args = (cfg, task, input_env)
    sub_kwargs = {
        "run_id": run_id,
        "run_dir": run_dir,
        "logger_prefix": logger_prefix,
        "_run_id_stack": _run_id_stack,
        "_cache": _cache,
    }
    #_eval_command(logger, *sub_args, **sub_kwargs)
    
    output_dir, output_env = run_local_task(*sub_args, **sub_kwargs)
    output_json = values_to_json(output_env, namespace=task.name)
    output = (output_dir, output_json)

    return output
 
