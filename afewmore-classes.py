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


# class SecurityGroups:
# members: gname -> group name
#          gid -> group id
class SecurityGroups:
    def __init__(self, scgrp):
        self.gname = scgrp["GroupName"]
        self.gid = scgrp["GroupId"]
    def __str__(self):
        return "\tGroupName: {0}\n\tGroupId: {1}".format(self.gname, self.gid)

# class Instance:
# members: 
    # insId -> instance id
    # azone -> AvailabilityZone
    # kname -> key name
    # imgid -> image id
    # itype -> instance type
    # sgroups -> SecurityGroups[]
    # pubIp -> public ip address
    # pubDns -> public dns
    # uname -> login user name
class Instance:
    def __init__(self, instance_id):
        out, err = execute("aws ec2 describe-instances --instance-id {0} --output json".format(instance_id))

	if out:
            instance = json.loads(out)["Reservations"][0]["Instances"][0]
            self.insId = instance_id
            self.azone = instance["Placement"]["AvailabilityZone"]
            self.kname = instance["KeyName"]
            self.imgId = instance["ImageId"]
            self.itype = instance["InstanceType"]
            self.pubIp = instance["PublicIpAddress"]
            self.pubDns = instance["PublicDnsName"]
            self.uname = "root"
            self.scgrps = []
            for group in instance["SecurityGroups"]:
                self.scgrps.append(SecurityGroups(group))
	else:
	    elog(err)

    def __str__(self):
        res = "\tInstanceId: {0} \n\tAvailabilityZone: {1}\n\tKeyName: {2}\n\tImageId: {3}\n\tInstanceType: {4}\n\tPublicIpAddress: {5}".format(self.insId, self.azone, self.kname, self.imgId, self.itype, self.pubIp)
        for i, group in enumerate(self.scgrps):
            res += "\n\tSG #" + str(i)
            res += str(group)
        return res


