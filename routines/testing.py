from utils import load_input_local
from client import test_input, test_wdl
from WDL import load
from state import StateMachine 
import logging
import os

logging.basicConfig()

def _test_wdl():
    return "/mnt/routines/example/3a_bam_chrom_counter.wdl"
def _test_input():
    return "/mnt/routines/example/3b_bam_chrom_counter.json"

def _load_state_machine(wdl, input_file, run_dir, data_path=None):

    doc = load(wdl)
    print("{}: {}".format(doc.__class__.__name__, doc.__dict__))
    input_env=load_input_local(doc, input_file, data_path)

    sm = StateMachine(doc, input_env, run_dir) 
    return sm
