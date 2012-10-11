__author__ = 'artzab'

import sys
from suds.client import Client
import logging

logging.basicConfig(level=logging.INFO)
testClient = Client('http://localhost:7789/?wsdl', cache=None)

configLab = testClient.factory.create('ns1:ConfigLab')
configLab.Action    = "delete"
configLab.Users     = {'string': ["ARTZAB@avalon.ru", "TEST@avalon.ru",]}
configLab.NameLab   = "1C-LAB"

print configLab

result = testClient.service.CreateLab(configLab)

print result