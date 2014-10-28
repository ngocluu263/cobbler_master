#!/bin/env python

import re
import yaml
import xmlrpclib
import utils

class CobblerManager(object):

    """initialize multi cobbler api servers, test them and cache them.
    At the same time, this class should provide methods to find correct server
    with pxe address"""

    def __init__(self, config_file):
        # Load server ip and ports from local config
        self.cobblers = yaml.load(open(config_file))
        self.remotes = {}
        self.check_setup()
        
    def check_setup(self):
        """
        Detect permissions and service accessibility problems and provide
        nicer error messages for them.
        """

        for name, dc in self.cobblers.iteritems():
            s = xmlrpclib.Server(dc["cobbler"]["url"])
            #try:
            s.ping()
            # token = s.login("", dc["cobbler"]["secret"])
            token = s.login(dc["cobbler"]["user"], dc["cobbler"]["passwd"])
            self.remotes[name] = {
                "api": s,
                "token": token
            }
            #except:
            #    raise CobblerApiConnectError("httpd does not appear to be"
            #            "running and proxying cobbler, or SELinux is in the"
            #            "way.")

    def get_remote_by_pxe_ip(self, pxe_ip):
        subnet = '.'.join(pxe_ip.split('.')[:3])
        for name, cobbler in self.cobblers.iteritems():
            if subnet in cobbler["subnet"]:
                return self.remotes[name]

    def generate_cobbler_commands(self, server):

        # some field is Deprecated by cobbler, if these fields exist, the
        # xmlrpc api will be unusable, and no error return.
        utils.replace_deprecate_field(server.commands)

        commands = {}
        for i_mac in server.macs:
            commands[i_mac] = []
            # """If the name of the cobbler system already looks like a mac
            # address, this is inferred from the system name and does not
            # need to be specified.""" -- Cobbler Document.
            # In fact, i don't know the mac address i have belong to which
            # ethernet device. So, i just use mac address as name of system
            # object.
            #system_name = "01-" + i_mac.replace(":", "-").lower()
            system_name = i_mac

            # clean up
            commands[i_mac].append({
                "type": "system",
                "action": "remove",
                "options": {
                    "name": system_name
                    }
                })

            # init system object
            commands[i_mac].append({
                "type": "system",
                "action": "add",
                "options": {
                    "name": system_name,
                    "in_place": False,
                    "profile": server.commands["profile"]
                    }
                })

            for i_interface in server.commands["interfaces"]:
                c = {
                    "type": "system",
                    "action": "edit",
                    "options": {
                        "name": system_name,
                        "in_place": False # """edit items in kopts or ksmeta
                                          # without clearing the other items
                                          # default: False""" -- Cobbler code
                        }
                    }

                for i_option, i_value in i_interface.iteritems():
                    c["options"][i_option] = str(i_value)

                commands[i_mac].append(c)

        return commands

    def generate_pxe_files(self, server):
        """
        remote.xapi_object_edit(object_type,
                                   options.name,
                                   object_action,
                                   utils.strip_none(vars(options),
                                           omit_none=True),
                                   self.token)
        """

        remote = self.get_remote_by_pxe_ip(server.ilo_ip)
        for commands in self.generate_cobbler_commands(server).values():
            for c in commands:
                try:
                    remote["api"].xapi_object_edit( c["type"],
                            c["options"]["name"], c["action"], c["options"],
                            remote["token"])
                except xmlrpclib.Fault as e:
                    print e
        
    def reinstall(self, server):
        self.generate_pxe_files(server)
        server.restart_with_pxe()

