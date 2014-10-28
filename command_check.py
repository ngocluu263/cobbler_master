import sys
import deploy
import yaml

try:
    form = yaml.load(open(sys.argv[1]))
except yaml.scanner.ScannerError as e:
    print e

s = deploy.PhysicsServer()

for mac, command in s.commands.iteritems():
    for c in command:
	print c["type"], c["action"]
	for option, value in c["options"].iteritems():
	    print "--{0}={1}".format(option, value)

	print ""
