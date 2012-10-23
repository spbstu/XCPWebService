__author__ = 'artzab'

from suds.client import Client
import logging

logging.getLogger('suds.client').setLevel(logging.CRITICAL)
testClient = Client('http://192.168.19.12:7789/?wsdl', cache=None)

result = testClient.service.GetAllVM()

print result