#-*- encoding: utf-8; -*-
from LDAPMethods2 import LDAPMethods
from WSPropertyVLAB import StatusVLAB, ValuesXCP, ValueXCP, ValuesAD, SingleValueXCP
from XCPMethods2 import XCPMethods
from XVPMethods2 import XVPMethods
import xcpconf

__author__ = 'artzab'

def _createLab(xcp, xvp, configLab):

    for strUser in configLab.Users:

        if configLab.NameLab not in xcp.configsLabs:
            xcp.messages("ERROR", "Lab name '%s' not found" % configLab.NameLab)
            xcp.logging.StatusOK = False
            return

        poolName = xcp.GetPoolName()

        for vm in xcp.configsLabs[configLab.NameLab]['vms']:
            strVM = strUser.split("@")[0] + "." + vm

            ##Check vm to exist
            xcp.messages("DEBUG", "Check vm: %s to exist" % strVM)
            objVMs = xcp.FindVM(strVM)
            if objVMs:
                xcp.messages("WARN", "VM: %s found. This VM not create!!!" % strVM)
                _res = xvp.CreateRightsXVP(strUser, xcp.xapi.VM.get_uuid(objVMs[0]), poolName)
                if not _res:
                    xcp.messages(
                        "ERROR", "Rights for vm: %s on the user: %s Not create!!!" % (strVM, strUser))

                continue


            ##Create VM
            xcp.messages("DEBUG", "Cretate vm: %s" % strVM)
            ref = xcp.CreateVM(strUser, vm, configLab.NameLab)
            if not ref:
                xcp.messages("ERROR", "VM: %s Not create!!!" % strVM)
                xcp.logging.StatusOK = False
                return
            xcp.messages("DEBUG", "VM: %s Created!" % strVM)
            xcp.messages("DEBUG", "Create rights for vm: %s" % strVM)

            ##Create Rights XVP
            _res = xvp.CreateRightsXVP(strUser, xcp.xapi.VM.get_uuid(ref), poolName)
            if not _res:
                xcp.messages("ERROR", "Rights for vm: %s on the user: %s Not create!!!" % (strVM, strUser))
                xcp.DeleteVM(strVM)
                xcp.logging.StatusOK = False
                return
            xcp.messages("DEBUG", "Rights for vm: %s on the user: %s Created!!!" % (strVM, strUser))

    return

def _deleteLab(xcp, xvp, configLab):
    ##
    ## Delete lab
    ##

    for strUser in configLab.Users:

        if configLab.NameLab not in xcp.configsLabs:
            xcp.messages("ERROR", "Lab name '%s' not found" % configLab.NameLab)
            xcp.logging.StatusOK = False
            return

        poolName = xcp.GetPoolName()

        for vm in xcp.configsLabs[configLab.NameLab]['vms']:
            strVM = strUser.split("@")[0] + "." + vm
            xcp.messages("DEBUG", "Check vm: %s to exist" % strVM)
            objVMs = xcp.FindVM(strVM)
            if not objVMs:
                xcp.messages("WARN", "VM: %s not found. This VM not deleted!!!" % strVM)
                continue
            xcp.messages("DEBUG", "Delete vm: %s" % strVM)
            uuid = xcp.xapi.VM.get_uuid(objVMs[0])
            xcp.DeleteVM(strVM)
            xcp.messages("DEBUG", "VM: %s Deleted!" % strVM)
            xcp.messages("DEBUG", "Delete rights for vm: %s" % strVM)
            _res = xvp.DeleteRightsXVP(strUser, uuid)
            if not _res:
                xcp.messages("WARN", "Rights for vm: %s on the user: %s Not deleted!!!" % (strVM, strUser,))
                continue
            xcp.messages("DEBUG", "Rights for VM: %s on the user: %s deleted!" % (strVM, strUser,))


    return

def CreateLab(configLab):
    res = StatusVLAB()
    res.Messages = []
    res.StatusOK = True

    xcp = XCPMethods(logging=res, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return
    xcp.ReadConfs()

    xvp = XVPMethods(logging=res, conf=config)
    xvp.ConnectDB()
    if not xvp.SQLConnect:
        return
    xvp.sqlCur = xvp.SQLConnect.cursor()


    if configLab.Action.lower() == "create":
        _createLab(xcp, xvp, configLab)
    elif configLab.Action.lower() == "delete":
        _deleteLab(xcp, xvp, configLab)
    else:
        res.Messages.append("ERROR: Action is wrong!!! Action is 'create' or 'delete'")
        res.StatusOK = False

    xvp.SQLConnect.commit()
    xvp.SQLConnect.close()
    xcp.xapi.logout()

    return res

def GetNetworks():

    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True


    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    objs = xcp.GetNetworks()
    if not objs:
        res.Status.StatusOK = False
        return res

    for obj in objs:
        valueXCP = ValueXCP()
        valueXCP.Ref = obj
        valueXCP.Value= xcp.xapi.network.get_name_label(obj)
        res.Values.append(valueXCP)

    return res

def GetTemplates():
    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    objs = xcp.GetTemplates()
    if not objs:
        res.Status.StatusOK = False
        return res

    for obj in objs:
        valueXCP = ValueXCP()
        valueXCP.Ref = obj
        valueXCP.Value= xcp.xapi.VM.get_name_label(obj)
        res.Values.append(valueXCP)

    return res

def GetLabs():
    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res
    xcp.ReadConfs()
    for obj in xcp.GetLabs():
        valueXCP = ValueXCP()
        valueXCP.Value= obj
        res.Values.append(valueXCP)
    return res

def GetAllVM():
    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    objs = xcp.GetVMs()
    if not objs:
        res.Status.StatusOK = False
        return res

    for obj in objs:
        valueXCP = ValueXCP()
        valueXCP.Ref = xcp.xapi.VM.get_uuid(obj)
        valueXCP.Value= xcp.xapi.VM.get_name_label(obj)
        res.Values.append(valueXCP)

    return res

def GetStatusVM(uuid):
    res = SingleValueXCP()
    res.Status = StatusVLAB()
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    objs = xcp.GetStatusVM(uuid)
    if not objs:
        res.Status.StatusOK = False
        return res

    res.Values = objs

    return res

def ChangeStateVM(uuid, state):
    res = StatusVLAB()
    res.Messages = []
    res.StatusOK = True

    xcp = XCPMethods(logging=res, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    if not xcp.ChangeStateVM(uuid, state):
        res.StatusOK = False

    return res

def GetGroups():
    res = ValuesAD()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    ad = LDAPMethods(logging=res.Status, conf=config)
    ad.InitAD()

    for obj in ad.GetAdGroups():
        res.Values.append(obj)

    return res

def GetStudentsByGroup(group):
    res = ValuesAD()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    ad = LDAPMethods(logging=res.Status, conf=config)
    ad.InitAD()

    for obj in ad.GetAdUsers(group):
        res.Values.append(obj)

    return res

def GetUsersVM(uuid):
    res = ValuesAD()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    xvp = XVPMethods(logging=res.Status, conf=config)
    xvp.ConnectDB()
    if not xvp.SQLConnect:
        return
    xvp.sqlCur = xvp.SQLConnect.cursor()

    objs = xcp.GetGroupsByUUID(uuid)
    if not objs:
        res.Status.StatusOK = False
        return res

    pool = xcp.GetPoolName()

    for obj in xvp.GetUsersByVMUUID(pool,uuid,objs):
        res.Values.append(obj)

    return res

def GetVMsUsers(strUser):
    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    xvp = XVPMethods(logging=res.Status, conf=config)
    xvp.ConnectDB()
    if not xvp.SQLConnect:
        return
    xvp.sqlCur = xvp.SQLConnect.cursor()

    pool = xcp.GetPoolName()
    uuids = xvp.GetVMUUIDByUser(pool,strUser)
    if len(uuids)>0:
        if uuids[0] == '*':
            return GetAllVM()

    for obj in uuids:
        vm = xcp.FindVMbyUUID(obj)

        if not res.Status.StatusOK:
            return res

        if not vm:
            continue

        valueXCP = ValueXCP()
        valueXCP.Ref = obj
        valueXCP.Value= xcp.xapi.VM.get_name_label(vm)
        res.Values.append(valueXCP)

    for group in xvp.GetVMGroupByUser(pool,strUser):
        for obj in xcp.GetVMByGroup(group):
            valueXCP = ValueXCP()
            valueXCP.Ref = xcp.xapi.VM.get_uuid(obj)
            valueXCP.Value= xcp.xapi.VM.get_name_label(obj)
            res.Values.append(valueXCP)

    return res

def GetVMsByLab(strLab):
    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    xcp.ReadConfs()

    for obj in xcp.GetVMsByLab(strLab):
        valueXCP = ValueXCP()
        valueXCP.Ref = obj['uuid']
        valueXCP.Value= obj['name_label']
        res.Values.append(valueXCP)

    return res

def GetStudentsByLab(strLab):
    res = ValuesAD()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xcp = XCPMethods(logging=res.Status, conf=config)
    resOK = xcp.ConnectXCP()
    if not resOK:
        return res

    xcp.ReadConfs()

    xvp = XVPMethods(logging=res.Status, conf=config)
    xvp.ConnectDB()
    if not xvp.SQLConnect:
        return
    xvp.sqlCur = xvp.SQLConnect.cursor()
    pool = xcp.GetPoolName()

    for obj in xcp.GetVMsByLab(strLab):
        for user in xvp.GetUsersByVMUUIDWithoutGroups(pool,obj['uuid']):
            res.Values.append(user)

    return res

global config
config = xcpconf.config

