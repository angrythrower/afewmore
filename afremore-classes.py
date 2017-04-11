#!/usr/bin/env python

import subprocess
import sys
import json

import os
import signal
import time

from collections import deque

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
    # idFile -> identity file(.pem)
class Instance:
    def __init__(self, instance_id):
        out = execute("aws ec2 describe-instances --instance-id {0} --output json".format(instance_id))

            instance = json.loads(out)["Reservations"][0]["Instances"][0]
            self.insId = instance_id
            self.azone = instance["Placement"]["AvailabilityZone"]
            self.kname = instance["KeyName"]
            self.imgId = instance["ImageId"]
            self.itype = instance["InstanceType"]
            self.pubIp = instance["PublicIpAddress"]
            self.pubDns = instance["PublicDnsName"]
            self.uname = "root"
            self.idFile = "~/.ssh/cs615-key2.pem"
            self.scgrps = []
            for group in instance["SecurityGroups"]:
                self.scgrps.append(SecurityGroups(group))

    def __str__(self):
        res = "\tInstanceId: {0} \n\tAvailabilityZone: {1}\n\tKeyName: {2}\n\tImageId: {3}\n\tInstanceType: {4}\n\tPublicIpAddress: {5}".format(self.insId, self.azone, self.kname, self.imgId, self.itype, self.pubIp)
        for i, group in enumerate(self.scgrps):
            res += "\n\tSG #" + str(i)
            res += str(group)
        return res


# class Host:
# description: store hsot infomation parsed from ~/.ssh/config file
# members:
#   host -> Host alias specified by user in config
#   pubIp -> HostName specified by user in config
#   user -> User specified by user in config
#   idFile -> IdentityFile specified by user in config
class Host:
    def __init__(self, info_arr):
        cache = {}
        for item in info_arr:
            cache[item[0]] = item[1]
        self.host = cache["Host"]
        self.pubIp = cache["HostName"]
        self.user = cache["User"]
        self.idFile = cache["IdentityFile"]

    def __str__(self):
        return "\n".join([
            "\tHost: " + self.host, 
            "\tHostName: " + self.pubIp,
            "\tUser: " + self.user, 
            "\tIdentityFile: " + self.idFile,
            ])

