#!/bin/env python

import yaml
import sys
import server
import pxe_manager

def main():
    pm = pxe_manager.Cobbler("./cobblers.yaml")

    commands = yaml.load(open(sys.argv[1]))
    ilo_ip = user_commands["ilo_ip"]
    s = server.PhysicsServer(ilo_ip, commands)

    pm.reinstall(s)

def test():
    pm = pxe_manager.CobblerManager("./cobblers.yaml")

    user_commands = yaml.load(open(sys.argv[1]))
    ilo_ip = user_commands["ilo_ip"]
    s = server.PhysicsServer(ilo_ip, user_commands)

    pm.reinstall(s)

if __name__ == '__main__':
    #main()
    test()
