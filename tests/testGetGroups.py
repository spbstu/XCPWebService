__author__ = 'artzab'

from suds.client import Client
import logging

logging.basicConfig(level=logging.INFO)
testClient = Client('http://localhost:7789/?wsdl', cache=None)

result = testClient.service.GetGroups()

print result