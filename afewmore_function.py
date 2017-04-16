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

        if output or error.strip() == "error: unexpected filename: ..":
            # log("successfully executed command: \n\t{0}".format(cmd))
            return (output, None)
        if error :
            log("error occurred when excuting command: \n\t{0}".format(cmd)) 
            return (None, error)
        return ("", None)

    except OSError, oserror:
        return (None, oserror)


def analyse_original_instance(instance_id, copy_dir):

    log("analysing original instance: {0}".format(instance_id))

    origin = Instance(instance_id)
    while not origin.isReady():
        origin.isReady()

    # log("parsing host from: {0}".format(SSH_CONFIG_DIR))
    # for host in host_parser(SSH_CONFIG_DIR):
        # if host.pubIp == origin.pubIp or host.pubIp == origin.pubDns:
            # log("host found: {0}".format(host))
        # origin.setLoginUser(host.user)
        # origin.setIdFile(host.idFile)

    log('checking login username...')
    out, err = execute("ssh {0}@{1} 'echo cs615'".format(origin.uname, origin.pubDns))

    if err:
        log(err)
        elog("afewmore ERROR: cannot access instance: {0}".format(origin.insId))

    else:
        msg = out.split(' ')
        if msg[0].strip() != "cs615":
            log("login user is not {0}".format(origin.uname))
            loginUser = msg[5].strip('"')
            log("changing login user to {0}".format(loginUser))
            origin.setLoginUser(loginUser)

        else:
            log("login user is {0}".format(origin.uname))            

        # super user command: assume it is sudo
        SUPER_USER_COMMAND = 'sudo'
        # check if the instance have sudo command
        out, err = execute("ssh {0}@{1} 'which sudo'".format(origin.uname, origin.pubDns))
        if not out:
            SUPER_USER_COMMAND = ''   
        if origin.uname != 'root':
            # use chown to change the ownership of the entire copy_dir to loginUser
            log('changing dir ownership...')
            execute("ssh {0}@{1} '{2} chown -R {0} {3}'".format(origin.uname, origin.pubDns, SUPER_USER_COMMAND, copy_dir))
            # user chmod to change the mod of the entire copy_dir to -(d)rwx------
            log('changing dir mode...')
            execute("ssh {0}@{1} '{2} chmod -R 700 {3}'".format(origin.uname, origin.pubDns, SUPER_USER_COMMAND, copy_dir))
        # check copy_dir
        log("checking soruce directory...")
        out, err = execute("ssh {0}@{1} 'ls -l {2}'".format(origin.uname, origin.pubDns, copy_dir))
        if err:
            elog("afewmore ERROR: cannot access directory or no such file")
            print err

    return origin

def analyse_created_instance(created, target_dir):

    log('checking login username...')
    out, err = execute("ssh {0}@{1} 'echo cs615'".format(created.uname, created.pubDns))

    if err:
        log(err)
        elog("afewmore ERROR: cannot access instance: {0}".format(created.insId))

    else:
        msg = out.split(' ')
        if msg[0].strip() != "cs615":
            log("login user is not {0}".format(created.uname))
            loginUser = msg[5].strip('"')
            log("changing login user to {0}".format(loginUser))
            created.setLoginUser(loginUser)

        else:
            log("login user is {0}".format(created.uname))            

        # super user command: assume it is sudo
        SUPER_USER_COMMAND = 'sudo'
        # check if the instance have sudo command
        out, err = execute("ssh {0}@{1} 'which sudo'".format(created.uname, created.pubDns))
        if not out:
            SUPER_USER_COMMAND = '' 
        # in case newly created instance doesn't have the target directory
        log('creating target dir...')
        execute("ssh {0}@{1} '{2} mkdir -p {3}'".format(created.uname, created.pubDns, SUPER_USER_COMMAND, target_dir))

        # if user cannot log in as root user
        if created.uname != 'root':
            # use chown to change the ownership of the entire target_dir to loginUser
            log('changing target dir ownership...')
            execute("ssh {0}@{1} '{2} chown -R {0} {3}'".format(created.uname, created.pubDns, SUPER_USER_COMMAND, target_dir))
            # user chmod to change the mod of the entire target_dir to -(d)rwx------
            log('changing target dir mode...')
            execute("ssh {0}@{1} '{2} chmod -R 700 {3}'".format(created.uname, created.pubDns, SUPER_USER_COMMAND, target_dir))

        # check target_dir
        log("checking target directory...")
        out, err = execute("ssh {0}@{1} 'ls -l {2}'".format(created.uname, created.pubDns, target_dir))

        if err:
            elog("afewmore ERROR: cannot access directory or no such file")            

    return created

def dup_instance(origin_instance, num):

    instances_queue = [] # cache the instances references
    origin = origin_instance
    out, err = execute('aws ec2 run-instances --placement AvailabilityZone={0} --image-id {1} --security-group-ids {2} --count {3} --instance-type {4} --key-name \'{5}\' --query \'Instances[*].InstanceId\' --output json'
        .format(
        origin.azone,
        origin.imgId,
        " ".join([group.gid for group in origin.sgroups]),
        num,
        origin.itype,
        origin.kname
    ))
    if out:
        for instance_id in json.loads(out):
            log("pushing instance: {0} to queue".format(instance_id))
            instances_queue.append(Instance(instance_id))
        return deque(instances_queue)
    else:
        elog(err)
    
def scp(origin, targets, dir="/data"):

    # format target directory
    if dir[len(dir) - 1] != "/":
        dir += "/"

    while len(targets) is not 0:
        target = targets.popleft()
        target.uname = origin.uname

        start_time = time.time()

        if target.isReady():
            target = analyse_created_instance(target, dir)
            log("copying to target: {0}".format(target.insId))
            out, err = execute("scp -3C -r {0}@{1}:{2} {3}@{4}:{5}"
                .format(origin.uname, origin.pubDns, dir + ".*", target.uname, target.pubDns, dir))
            if err:
                elog(err)
            if out:
                log(out)
            else:
                log("successfully copied!")
                if not DEBUG:
                    print "\t" + target.insId
                # origin = target
                log(target)
        else:
            targets.append(target)
        
        end_time = time.time()

        if end_time - start_time < 5:
            log("wating...")
            time.sleep(5)

def start(instance_id, copy_dir, num_new_ins):
    log("starting with {0} {1} {2}".format(instance_id, copy_dir, num_new_ins))
    log("verbose: " + str(DEBUG))

    origin_instance = analyse_original_instance(instance_id, copy_dir)
    log("done checking source instance: " + origin_instance.insId)

    log("duplicating instances...")
    targets_queue = dup_instance(origin_instance, num_new_ins)
    log("done duplicating instnaces...")

    log("copying " + copy_dir + "...")
    scp(origin_instance, targets_queue, copy_dir)

    log("**********DONE**********\n")

if __name__ == "__main__":

    DEBUG = False  # program will print debug infomation to stdout when DEBUG is True
    SSH_CONFIG_DIR = os.path.expanduser('~') + "/.ssh/config"  # default ssh config file location
    INSTANCE_ID = "" # source instance id, should be provided from user
    NUM_NEW_INS = 10 # default new number of instances to start
    COPY_DIR = "/data" # default source directory to copy from
    START_TIME = time.time()




