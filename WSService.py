#!/usr/bin/env python

__author__ = 'artzab'
import soaplib
import logging
from soaplib.core.server import wsgi
from WSMethodVLAB import VLABManager

if __name__=='__main__':

    logging.basicConfig(level=logging.DEBUG)

    try:
        from wsgiref.simple_server import make_server
        soap_application = soaplib.core.Application([VLABManager], 'http://devel.avalon.ru/')
        wsgi_application = wsgi.Application(soap_application)
        server = make_server('localhost', 7789, wsgi_application)
        print "Server run on port 7789"
        server.serve_forever()
    except ImportError:
        print "Error: Server code requires Python >= 2.5"
                
