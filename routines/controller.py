#!/usr/bin/env python3.8

import os
import grpc
import pickle
import json
import logging
import asyncio 

from WDL import values_to_json 
from WDL.Value import digest_env
import WDL.runtime.workflow as runtime 

from services import routine_pb2, routine_pb2_grpc
from state import StateMachine
from utils import cd, load_wdl, load_input

class StateCache:
    slots = ("_dir")

    def __init__(self, cache_dir):
        if not os.path.exists(cache_dir):
            logging.info(f"created cache dir: {cache_dir}")
            os.makedirs(cache_dir)

        self._dir = cache_dir

    def __getitem__(self, state: runtime.StateMachine):

        cache_path = self._cache_path(state)
        if os.path.exists(cache_path):
            with cd(cache_path):
                return pickle.loads('state.pkl')

    def __call__(self, state: runtime.StateMachine):
        self._store(state)

    def _store(self, state: runtime.StateMachine):
        cache_path = self._cache_path(state)
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
            with cd(cache_path):
                pickle.dump(state, 'state.pkl') 

        else:
            print("cache exists: {cache_key}")

    def _cache_path(state: runtime.StateMachine):
        return os.path.join(self._dir,
                f"{state.workflow.name}/{state.workflow.digest}/{digest_env(state.inputs)}")

class WorkflowController(routine_pb2_grpc.RoutineServicer):

    def __init__(self, async_loop, cfg):
        if not os.path.exists(cfg.app_dir):
            os.makedirs(cfg.app_dir)
        
        cache_dir = os.path.join(cfg.app_dir, 'cache')
        self.run_dir = os.path.join(cfg.app_dir, 'runs')

        self.cache = StateCache(cache_dir)
        self.async_loop = async_loop

    def _Execute(self, job, context):

        print("{}: received job {}".format(self.__class__.__name__, job))

        doc = load_wdl(self.async_loop, job.wdl)
        input_env = load_input(self.async_loop, doc, job.input)
        sm = StateMachine(doc, input_env, self.run_dir) 

        out=str(values_to_json(input_env).items())
        status = routine_pb2.Status(msg="success", code=0)

        return routine_pb2.Result(status=status, outdir=out)

    def Execute(self, job, context):

        logging.info("{}: received job {}".format(self.__class__.__name__, job))

        doc = load_wdl(self.async_loop, job.wdl)
        input_env = load_input(self.async_loop, doc, job.input, job.data_dir)
        sm = StateMachine(doc, input_env, self.run_dir) 
        
        err = sm.run_state()
        if err:
            status = routine_pb2.Status(msg=err, code=1)
            return routine_pb2.Result(status=status)

        output_json = values_to_json(sm.state.outputs)
        status = routine_pb2.Status(msg="success", code=0)

        return routine_pb2.Result(status=status, outdir=json.dumps(output_json))

# to support asynchronous loading of the WDL document using WDL.Tree._load
# https://stackoverflow.com/questions/38387443/how-to-implement-a-async-grpc-python-server/63020796#63020796
async def serve(obj):

    server = grpc.aio.server()
    routine_pb2_grpc.add_RoutineServicer_to_server(
    	obj, server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)

    logging.info(f"{obj.__class__.__name__} listening on {listen_addr}")
    print(f"{obj.__class__.__name__} listening on {listen_addr}")

    await server.start()
    await server.wait_for_termination()

def run(loop, cfg):

    wc = WorkflowController(loop, cfg)
    asyncio.run(serve(wc))

if __name__ == "__main__":

    logging.basicConfig()

    from collections import namedtuple
    config = namedtuple('config', ['app_dir']) 

    if "ROUTINES_APP_DIR" not in os.environ: 
        os.environ["ROUTINES_APP_DIR"] = "/tmp/routines"
    cfg = config(app_dir=os.environ.get("ROUTINES_APP_DIR"))

    loop = asyncio.get_event_loop()
    run(loop, cfg)



