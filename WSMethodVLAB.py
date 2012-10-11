#!/usr/bin/env python

__author__ = 'artzab'
from soaplib.core.service import DefinitionBase, soap
from soaplib.core._base import ValidatingApplication

from WSPropertyVLAB import *
from VLABMethod import *

class VLABManager(DefinitionBase):
    __names__ = "Service.VLABManager"
    
    @soap(ConfigLab,_returns=StatusVLAB)
    def CreateLab(self,config_lab):
        return CreateLab(config_lab)

    @soap(_returns=ValuesXCP)
    def GetAllVM(self):
        return GetAllVM()

    @soap(String, _returns=SingleValueXCP)
    def GetStatusVM(self, uuid):
        return GetStatusVM(uuid)

    @soap(String, _returns=ValuesAD)
    def GetUsersVM(self, uuid):
        return GetUsersVM(uuid)

    @soap(String, _returns=ValuesXCP)
    def GetVMsUsers(self, user):
        return GetVMsUsers(user)

    @soap(String, String, _returns=StatusVLAB)
    def ChangeStateVM(self, uuid, state):
        return ChangeStateVM(uuid, state)

    @soap(_returns=ValuesXCP)
    def GetNetworks(self):
        return GetNetworks()

    @soap(_returns=ValuesXCP)
    def GetTemplates(self):
        return GetTemplates()

    @soap(_returns=ValuesAD)
    def GetGroups(self):
        return GetGroups()

    @soap(String,_returns=ValuesAD)
    def GetStudentsByGroup(self, group):
        return GetStudentsByGroup(group)

services = [
    VLABManager,
]

application = ValidatingApplication(services, tns='http://devel.avalon.ru/')
