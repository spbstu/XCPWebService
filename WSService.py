#!/usr/bin/env python

__author__ = 'artzab'
import logging, os
from soaplib.core.server import wsgi
from WSMethodVLAB import VLABManager
from subprocess import Popen, PIPE
import xcpconf
from base64 import b64decode
from soaplib import core
import kerberos

os.chdir(os.path.dirname(os.path.realpath(__file__)))

class KerberosAuth:
    def __init__(self, wrapped, realm, service='HTTP'):
        self.realm=realm
        self.service=service
        self.wrapped=wrapped

    def __call__(self, environ, start_response):
        def error():
            start_response('500 Error', [
                ('content-type', 'text/plain'),
                ])
            return ['Internal error']
        def noauth(msg=None):
            start_response('401 Unauthorized', [
                ('content-type', 'text/plain'),
                ('WWW-Authenticate','Negotiate'),
                ('WWW-Authenticate','Basic realm="Web Service for CloudLab"')
            ])
            if msg:
                return ['No auth. Error: %s' % msg]
            return ['No auth']


        if 'HTTP_AUTHORIZATION' not in environ:
            return noauth()

        type, authstr = environ['HTTP_AUTHORIZATION'].split(' ', 1)

        if type == 'Negotiate':
            result, context = kerberos.authGSSServerInit(self.service)
            if result != 1:
                return error()

            gssstring=''
            r=kerberos.authGSSServerStep(context,authstr)
            if r == 1:
                gssstring=kerberos.authGSSServerResponse(context)
            else:
                return noauth()
            def new_start_response(status, headers):
                start_response(
                    status,
                    [
                        ('WWW-Authenticate','Negotiate %s' % gssstring)
                    ]+headers
                )

            environ['REMOTE_USER']=kerberos.authGSSServerUserName(context)
            kerberos.authGSSServerClean(context)
        elif type == 'Basic':
            username, password = b64decode(authstr).split(':',1)
            try:
                kerberos.checkPassword(username, password, self.service, self.realm)
            except Exception, e:
                return noauth(e.message)
            new_start_response=start_response
            environ['REMOTE_USER']=username
        return self.wrapped(environ, new_start_response)

soap_application = core.Application([VLABManager], 'http://devel.avalon.ru/')
application=KerberosAuth(wsgi.Application(soap_application), xcpconf.config['krbRealm'])

if __name__=='__main__':

    kinit = '/usr/bin/kinit'
    kinit_args = [ kinit, '%s@%s' % (xcpconf.config['krbLogin'], xcpconf.config['krbRealm']) ]
    kinit = Popen(kinit_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    kinit.stdin.write('%s\n' % xcpconf.config['krbPassword'])
    kinit.wait()
    logging.basicConfig(level=logging.DEBUG)
    try:
        from wsgiref.simple_server import make_server
        server = make_server('0.0.0.0', 7789, application)
        print "Server run on port 7789"
        server.serve_forever()
    except ImportError:
        print "Error: Server code requires Python >= 2.5"
                
