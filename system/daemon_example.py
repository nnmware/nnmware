#!/usr/bin/python
# -*- coding: utf-8 -*-
# Example of daemons
#
# Normal Exit - "cdrdaemon stop"
#
import os
import sys
import time
from socket import *

###########################################################################
workdir = "/var/www/nnmware"
logfile = "nnmware.log"
pidfile = "nnmware.pid"
statHost = ""
statPort = 9000
child = 5   # allow 5 simultaneous pending connections
buffer = 1024  # 1K buffer of data
###########################################################################
sys.path.insert(0, '/PATH/TO/YOU/PROJECT')
os.environ['DJANGO_SETTINGS_MODULE'] = 'nnmware.settings'
from nnmware.apps.cdr.models import Pabx, Cdr


class Log:
    """ Autoflush"""

    def __init__(self, f):
        self.f = f

    def write(self, s):
        self.f.write(s)
        self.f.flush()


def get_daemon_pid():
    if os.path.exists(pidfile):
        pid = open(pidfile, 'r').read()
        return int(pid)
    else:
        return None


def stopd():
    print 'Stopping Test Daemon...\n\r',
    if not os.path.exists('%s/%s' % (workdir, pidfile)):
        print 'Daemon does not appear to be running'
        return
    pid = get_daemon_pid()
    sys.stdout = sys.stderr = Log(open('%s/%s' % (workdir, logfile), 'a+'))
    print 'CDRDaemon stopped at ' + time.strftime("%Y/%m/%d %H.%M.%S")
    os.popen('kill -9 %d' % pid)
    os.remove('%s/%s' % (workdir, pidfile))


def store(record):
    # Work with data from PABX
    pabx, created = Pabx.objects.get_or_create(ip=record)
    rec = Cdr()
    rec.pabx = pabx
    rec.save()


def main():
    #change to data directory if needed
    os.chdir(workdir)
    # Redirect outputs to a logfile
    sys.stdout = sys.stderr = Log(open('%s/%s' % (workdir, logfile), 'a+'))
    # ensure the that the daemon runs a normal user
    os.setegid(0)     # set group
    os.seteuid(0)     # set user
    #start the user program here:
    print 'CDRDaemon running at ' + time.strftime("%Y/%m/%d %H.%M.%S")

    s = socket(AF_INET, SOCK_STREAM)    # Create the TCP Socket
    s.bind((statHost, statPort))        # bind it to the server port
    s.listen(child)                     # allow X simultaneous pending connections
    (connection, address) = s.accept()  # connection is a new socket
    try:
        while 1:
            data = connection.recv(buffer)  # receive up to 1K bytes
            if data:
                store(address[0])
                r = data.split()
                result = address[0] + ' '
                for item in r:
                    result += item + ' '
                print result
                #smsfile = open(filename, 'w+')
                #smsfile.write(msg)
                #smsfile.	close()
    except KeyboardInterrupt:
        stopd()
        #	print 'CDRDaemon normal exit at '+time.strftime("%Y/%m/%d %H.%M.%S")
    #	os.remove('%s/%s' % (workdir,pidfile))
    connection.close()              # close socket

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start' and os.path.exists('%s/%s' % (workdir, pidfile)):
            print 'Process appears to be running'
            sys.exit()
        if sys.argv[1] == 'stop':
            stopd()
            sys.exit()
            # Double fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/")   # don't prevent unmounting....
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            open('%s/%s' % (workdir, pidfile), 'w').write("%d" % pid)
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # start the daemon main loop
    main()
