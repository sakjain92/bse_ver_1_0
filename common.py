#!/usr/bin/python
import inspect
import logging
import os
import subprocess

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def log_setup():
    i=0
    if 'bse_last' in os.listdir("./"):
        subprocess.call(["rm","-rf","bse_last"])
        while(1):
            if 'bse_out_'+str(i) in os.listdir("./"):
                i=i+1
            else:
                break
    subprocess.call(["mkdir","bse_out_"+str(i)])
    subprocess.call(["ln","-s","bse_out_"+str(i),"bse_last"])
    LOG_PATH = "./"+"bse_last"
    LOG_FILENAME="bse.log"
    logging.basicConfig(filename=LOG_FILENAME,pathname=LOG_PATH,
                    level=logging.DEBUG,
                    )
    logging.info("Starting Log")

def log_close():
    subprocess.call(["mv","bse.log","./bse_last"])

log=logging #Log can be changed so overide debug/info/error functions

    
