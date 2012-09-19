__author__ = 'artzab'

from suds.client import Client
import logging

logging.getLogger('suds.client').setLevel(logging.CRITICAL)
testClient = Client('http://localhost:7789/?wsdl', cache=None)

result = testClient.service.GetTemplates()

print result