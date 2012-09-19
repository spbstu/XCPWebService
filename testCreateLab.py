__author__ = 'artzab'

import sys
from suds.client import Client
import logging

logging.basicConfig(level=logging.INFO)
testClient = Client('http://localhost:7789/?wsdl', cache=None)

net = testClient.factory.create('ns1:PropertyConf')
net.Ref             = "OpaqueRef:f177df5d-4413-36bb-e85b-6dc1a948b56c"
net.Value           = "Avalon"

templ = testClient.factory.create('ns1:PropertyConf')
templ.Value         = "T-Ubuntu10.10"
templ.Ref           = "OpaqueRef:78f09ce9-c3de-2328-6422-53431ae3835a"

vmConf = testClient.factory.create('ns1:VMConf')
vmConf.Folder       = "/LABs/FST/TEST"
vmConf.Suffix       = "-TEST-WEBSERVICE"
vmConf.Template     = templ
vmConf.Networks     = {'PropertyConf':[net,]}
vmConf.Tags         = {'string':["group test",]}
vmConfs = testClient.factory.create('ns1:VMConfArray')
vmConfs = [vmConf,]

configLab = testClient.factory.create('ns1:ConfigLab')
configLab.Action    = "delete"
configLab.DomainKrb = "AVALON.RU"
configLab.PoolName  = "Main0"
configLab.Users     = {'string': ["ARTZAB", "TEST",]}
configLab.VMs       = {'VMConf':[vmConf,]}

print configLab

result = testClient.service.CreateLab(configLab)

print result