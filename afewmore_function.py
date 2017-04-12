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
    pass

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




