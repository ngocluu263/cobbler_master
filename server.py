#!/bin/env python

import urllib2
import inspect
import commands
import paramiko
import error

class PhysicsServer(object):

    """Contain info about physics server, like ilo ip, mac address, etc."""

    IPMITOOL = '/usr/bin/ipmitool'
    SMCIPMITOOl = '/root/SMCIPMITool_2.8.1/SMCIPMITool'
    ILO_AUTH = {
        "dell": {
            "user": "root",
            "passwd": "******"
            },
        "supermicro": {
            "user": "ADMIN",
            "passwd": "*****"
            },
        "huawei": {
            "user": "root",
            "passwd": "*********"
            }
    }

    def __init__(self, ilo_ip="", commands="", vendor="", macs=[]):
        self.ilo_ip = ilo_ip
        self.vendor = vendor
        self.macs = macs  # multi mac address support pxe maybe :)
        self.commands = commands

        if not self.vendor:
            self.detect_vendor()

        if not self.macs:
            self.fetch_macs()
        
    def detect_vendor(self):
        """get vendor name use curl

        :ilo_ip: ip address of remote control card

        """
        # We need a system like cmdb, to provide vendor information.
        # But, there is none, fornow.
        _, content = commands.getstatusoutput('curl -m 2 http://' + self.ilo_ip)
        _, info = commands.getstatusoutput('curl -m 2 -I http://' + self.ilo_ip)

        if "Huawei" in info:
            self.vendor = "huawei"
        elif "designs/imm" in info:
            self.vendor = "ibm"
        elif "start.html" in info:
            self.vendor = "dell"
        elif "images/logo.gif" in content:
            self.vendor = "supermicro"
        else:
            raise error.UnknownVendorError("self.vendor")

    def fetch_macs(self):
        if self.vendor in ["dell", "supermicro", "huawei"]:
            eval("self.%s_%s()" % (inspect.stack()[0][3], self.vendor.lower()))
        # else:
        #     raise error.CannotGetMacAddr("vendor: {0}, ilo_ip:{1}"
        #            .format(self.vendor, self.ilo_ip))
    
    def fetch_macs_huawei(self):
        """
        Command Output:

        root@BMC:/#ipmcget -d macaddr
        NIC1:04-F9-38-ED-D7-5C
        NIC2:04-F9-38-ED-D7-5D
        NIC3:04-F9-38-ED-D7-5E
        NIC4:04-F9-38-ED-D7-5F
        """
        client = paramiko.SSHClient()

        client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        client.connect(self.ilo_ip,
                username=self.__class__.ILO_AUTH[self.vendor]["user"],
                password=self.__class__.ILO_AUTH[self.vendor]["passwd"])
        stdin, stdout, stderr = client.exec_command("/ipmc/ipmcget -d macaddr")

        for i_line in stdout.readlines():
            if "NIC" in i_line:
                self.macs.append(i_line.strip().split(":")[1])


    def fetch_macs_dell(self):
        """
        Command Output:
        System LOMs
        NIC Number      MAC Address             Status

        0               ec:f4:bb:c1:d7:90       Enabled
        1               ec:f4:bb:c1:d7:92       Enabled
        2               ec:f4:bb:c1:d7:94       Enabled
        3               ec:f4:bb:c1:d7:95       Enabled

        iDRAC7 MAC Address f8:bc:12:4a:e7:8e

        """
        status, output = commands.getstatusoutput("%s -I"
            "lanplus -U %s -P %s -H %s delloem mac" % (
                self.__class__.IPMITOOL,
                self.__class__.ILO_AUTH[self.vendor]["user"],
                self.__class__.ILO_AUTH[self.vendor]["passwd"],
                self.ilo_ip))

        for i_line in output.splitlines():
            if "Enabled" in i_line:
                self.macs.append(i_line.strip().split()[1])

    def fetch_macs_supermicro(self):
        """
        Command Output:
        $ ./SMCIPMITool xxxxxxxxx ADMIN ADMIN ipmi oem mac
        System MAC Address 1: 00:25:90:D6:3F:C0

        """
        status, output = commands.getstatusoutput("%s %s %s "
            "%s ipmi oem mac" % (self.__class__.SMCIPMITOOl,
                self.ilo_ip,
                self.__class__.ILO_AUTH[self.vendor]["user"],
                self.__class__.ILO_AUTH[self.vendor]["passwd"]))

        for i_line in output.splitlines():
            if "System MAC Address" in i_line:
                self.macs.append(i_line.strip().split()[4])

    def restart_with_pxe(self):
        """after ks file generated, restart target server with pxe

        :ilo_ip: ip address of remote control card
        :returns: true if ipmitool commands excuted success
        @todo add error exceptions

        """
        # set boot device of next time, first.
        commands.getstatusoutput("/usr/bin/ipmitool -I lanplus -U %s -P"
            "%s -H %s chassis bootdev pxe" % (
                    self.__class__.ILO_AUTH[self.vendor]["user"],
                    self.__class__.ILO_AUTH[self.vendor]["passwd"],
                 self.ilo_ip))

        # reset the server 
        commands.getstatusoutput("/usr/bin/ipmitool -I lanplus -U %s -P"
            "%s -H %s chassis power reset" % (
                    self.__class__.ILO_AUTH[self.vendor]["user"],
                    self.__class__.ILO_AUTH[self.vendor]["passwd"],
                 self.ilo_ip))

def main():
    s = PhysicsServer("10.11.3.1")
    print s.vendor
    print s.macs
    

if __name__ == '__main__':
    main()
