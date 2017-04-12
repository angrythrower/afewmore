#!/usr/bin/env python

import subprocess
import sys
import json

import os
import signal
import time

from collections import deque

# print processing message
def log(line):
    if DEBUG:
        print "DEBUG: " + str(round(float(time.time() - START_TIME), 3)) + "s - " + str(line)

# print error message and exit program with errorcode 1
def elog(line):
    sys.stderr.write(line + "\n")
    sys.exit(1)

def execute(cmd, timeout=None):

    try:
        pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, preexec_fn=os.setsid) 
        output, error = pro.communicate()

        if timeout is not None:
            time.sleep(timeout)
            log("kill command: \n\t{0}".format(cmd))
            os.killpg(pro.pid, signal.SIGTERM)
            return (output, error)

        if output:
            # log("successfully executed command: \n\t{0}".format(cmd))
            return (output, None)
        if error:
            log("error occurred when excuting command: \n\t{0}".format(cmd)) 
            return (None, error)
        return ("", None)

    except OSError, oserror:
        return (None, oserror)

def host_parser(dir):
    pass

def analyse_original_instance(instance_id, copy_dir):
    pass

def analyse_created_instance(created, target_dir):
    pass

def dup_instance(origin_instance, num):
    pass
    
def scp(origin, targets, dir="/data"):
    pass

def start(instance_id, copy_dir, num_new_ins):
    pass

if __name__ == "__main__":
    pass




