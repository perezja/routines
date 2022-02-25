#!/usr/bin/env python3

import os
import json
import logging

from WDL import Document, Tree, Env, Expr, values_to_json, values_from_json 
from WDL._util import provision_run_dir
from WDL.runtime import cache as _cache
from WDL.runtime.workflow import StateMachine as _StateMachine, _StdLib

from tasks import run_task
from utils import cd, load_config, extract_source

def _stdlib(doc, cfg, state, cache=_cache.CallCache):
    return _StdLib(doc.workflow.effective_wdl_version, cfg, state, cache) 

def _state_machine(doc, input_env, run_dir): 
    logger_id = 'wdl.w:'+doc.workflow.name
    run_dir = provision_run_dir(doc.workflow.name, run_dir)
    print('using run_dir: {}'.format(run_dir))
    sm = _StateMachine(logger_id, run_dir, doc.workflow, input_env) 

    return sm

class StateMachine:

    def __init__(self, doc: Document, input_env: Env.Bindings, run_dir):

        self.cfg = load_config()

        self.input_env = input_env
        self.doc = doc

        self.state = _state_machine(doc, input_env, run_dir)    
        self.stdlib = _stdlib(doc, self.cfg, self.state)

    def reload(self):
        self.state = _state_machine(self.doc, self.input_env)

    def walk(self):
        for name, job in self.state.jobs.items():
            print('Job {}: {}'.format(name, job))
            if isinstance(job.node, WDL.Tree.Scatter):
                self.state._do_job(self.cfg, self.stdlib, job)

    def get_state(self):

        return "running: {}, waiting: {}, finished: {}".format(self.state.running, self.state.waiting, self.state.finished)

    def show_env(self, bindings):
        env = list()
        for i in bindings:
            env.append("arg: {}, val: {}".format(i._name, i._value))
        return ";".join(env)

    def show_cmd(self, callee):
        def show_cmd_parts(cmd):
            for i, part in enumerate(cmd.parts):
                if isinstance(part, Expr.Placeholder):
                    print("Part {}: {}".format(i, part.__dict__))
                    print("    expr {}: {}".format(part.expr, part.expr.__dict__))

    def run_state(self):
        self.get_state()

        call_futures = {}
        run_id_stack = []

        while self.state.outputs is None:
            next_call = self.state.step(self.cfg, self.stdlib)

            while next_call:
                call_dir = os.path.join(self.state.run_dir, next_call.id)
                if os.path.exists(call_dir):
                    logger.warning(
                        _("call subdirectory already exists, conflict likely", dir=call_dir)
                    )

                task_str = extract_source(next_call.callee.pos)
                task_digest = next_call.callee.digest
                task_inputs = values_to_json(next_call.inputs, namespace=next_call.callee.name)

                sub_args = (task_str, task_digest, task_inputs)

                sub_kwargs = {
                    "run_id": next_call.id,
                    "run_dir": os.path.join(call_dir, "."),
                    "logger_prefix": [self.state.logger_id],
                    "_cache": None,
                    "_run_id_stack": run_id_stack,
                }

                future = run_task.delay(*sub_args, **sub_kwargs)

                call_futures[future] = next_call.id

                next_call = self.state.step(self.cfg, self.stdlib)

            # no more calls to launch right now; wait for an outstanding call to finish
            future = next(iter(call_futures), None)
            if future:

                outdir, output_json = future.get()

                call_id = call_futures[future]
                task = self.state.jobs[call_id].node.callee

                output_env = values_from_json(output_json, task.effective_outputs, namespace=task.name)
                self.state.call_finished(call_id, output_env)

                call_futures.pop(future)

            else:
                assert self.state.outputs is not None

