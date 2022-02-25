#!/usr/bin/env python3
import os
import grpc
import json
import logging
import argparse
import services.routine_pb2 as routine_pb2
import services.routine_pb2_grpc as routine_pb2_grpc 

def test_wdl():
    return '/Users/James/work/routines/playground/WDL/3b_bam_chrom_counter/3a_bam_chrom_counter.wdl' 

def test_input():
    return '/Users/James/work/routines/playground/WDL/3b_bam_chrom_counter/3b_bam_chrom_counter.json'

class API: 

    def __init__(self, hostname, port):

        host = ':'.join([hostname, str(port)])
        self.host = host 

    def submit(self, wdl:str, input_file:str, data_dir:str=None):

        job = routine_pb2.Job(wdl=wdl, input=input_file, data_dir=data_dir)
        with grpc.insecure_channel(self.host) as channel: 
            stub = routine_pb2_grpc.RoutineStub(channel)

            logging.info("connecting to host: {}".format(self.host))
            result = stub.Execute(job)

            logging.info("Submit: result={}".format(result))

        return result

def main():

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument('wdl')
    parser.add_argument('input_json')
    parser.add_argument('-d', '--data_dir')
    parser.add_argument('-s', '--host', default='localhost')
    parser.add_argument('-p', '--port', default='50051')
    parser.add_argument('--loglevel', default='INFO')
    args = parser.parse_args()

    api = API(hostname=args.host, port=int(args.port))   
    
    wdl = os.path.abspath(args.wdl)
    input_json = os.path.abspath(args.input_json)
    result = api.submit(wdl, input_json)   

    #logging.info(f"job completed: {result}")
    print(f"job completed: {result}")

if __name__ == "__main__":
    main()

