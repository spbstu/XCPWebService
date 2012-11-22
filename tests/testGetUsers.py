#-*- encoding: utf-8; -*-

__author__ = 'artzab'

from suds.client import Client
import logging

logging.basicConfig(level=logging.INFO)
testClient = Client('http://xxvp.avalon.ru/wss/?wsdl', cache=None, username='bilbo', password='BILBO')
#testClient = Client('http://localhost:7789/?wsdl', cache=None)
#testClient = Client('http://localhost:7789/?wsdl', cache=None, username='bilbo', password='BILBO')

#result = testClient.service.say_hello()
#result = testClient.service.GetStudentsByGroup(u'FMIT-Students-4241-1')
#result = testClient.service.GetUsersVM('62618835-6b9f-d4ae-1ade-bd8d624d7742')
#result = testClient.service.GetStatusVM("62618835-6b9f-d4ae-1ade-bd8d624d7742")
#result = testClient.service.GetLabs()
#result = testClient.service.GetVMsByLab('1C-LAB')
result = testClient.service.GetGroups()

print result