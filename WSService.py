#!/usr/bin/env python
from subprocess import Popen, PIPE

__author__ = 'artzab'
import soaplib
import logging
from soaplib.core.server import wsgi
from WSMethodVLAB import VLABManager
import xcpconf


if __name__=='__main__':

    kinit = '/usr/bin/kinit'
    kinit_args = [ kinit, '%s@%s' % (xcpconf.config['krbLogin'], xcpconf.config['krbRealm']) ]
    kinit = Popen(kinit_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    kinit.stdin.write('%s\n' % xcpconf.config['krbPassword'])
    kinit.wait()
    logging.basicConfig(level=logging.DEBUG)

    try:
        from wsgiref.simple_server import make_server
        soap_application = soaplib.core.Application([VLABManager], 'http://devel.avalon.ru/')
        wsgi_application = wsgi.Application(soap_application)
        server = make_server('0.0.0.0', 7789, wsgi_application)
        print "Server run on port 7789"
        server.serve_forever()
    except ImportError:
        print "Error: Server code requires Python >= 2.5"
                
