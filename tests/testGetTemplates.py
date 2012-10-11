__author__ = 'artzab'

from suds.client import Client
import logging

logging.getLogger('suds.client').setLevel(logging.CRITICAL)
testClient = Client('http://localhost:7789/?wsdl', cache=None)

result = testClient.service.ChangeStateVM("b9356022-122b-9b22-76db-81867fd007f6", "shutdown")

print result