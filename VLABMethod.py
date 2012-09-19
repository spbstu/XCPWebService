from LDAPMethods import _initAD, _getAdGroups, _getAdUsers
from WSPropertyVLAB import StatusVLAB, ValuesXCP, ValueXCP, ValuesAD
from XCPMethods import _connectXCP, _getNetworks, _deleteVM, _findVM, _createVM, _getTemplates
from XVPMethods import _connectDB, _deleteRightsXVP, _createRightsXVP
import xcpconf

__author__ = 'artzab'

def _createLab(xapi, sqlCur, configLab, res):
    for strUser in configLab.Users:
        for cfgVM in configLab.VMs:
            strVM = strUser + cfgVM.Suffix

            ##Check vm to exist
            if config['debug']:
                res.Messages.append("DEBUG: Check vm: %s to exist" % strVM)
            objVMs = _findVM(xapi, strVM)
            if objVMs:
                res.Messages.append("WARN: VM: %s found. This VM not create!!!" % strVM)
                _res = _createRightsXVP(sqlCur, strUser, xapi.VM.get_uuid(objVMs[0]), configLab, res)
                if not _res:
                    res.Messages.append(
                        "ERROR: Rights for vm: %s on the user: %s Not create!!!" % (strVM, strUser))

                continue

            ##Create VM
            if config['debug']:
                res.Messages.append("DEBUG: Cretate vm: %s" % strVM)
            ref = _createVM(xapi, strUser, cfgVM, res)
            if not ref:
                res.Messages.append("ERROR: VM: %s Not create!!!" % strVM)
                res.StatusOK = False
                return
            if config['debug']:
                res.Messages.append("DEBUG: VM: %s Created!" % strVM)
                res.Messages.append("DEBUG: Create rights for vm: %s" % strVM)

            ##Create Rights XVP
            _res = _createRightsXVP(sqlCur, strUser, xapi.VM.get_uuid(ref), configLab, res)
            if not _res:
                res.Messages.append("ERROR: Rights for vm: %s on the user: %s Not create!!!" % (strVM, strUser))
                res.StatusOK = False
                return
            if config['debug']:
                res.Messages.append("DEBUG: Rights for vm: %s on the user: %s Created!!!" % (strVM, strUser))

    return

def _deleteLab(xapi, sqlCur, configLab, res):
    ##
    ## Delete lab
    ##

    for strUser in configLab.Users:
        for cfgVM in configLab.VMs:
            strVM = strUser + cfgVM.Suffix
            if config['debug']:
                res.Messages.append("DEBUG: Check vm: %s to exist" % strVM)
            objVMs = _findVM(xapi, strUser + cfgVM.Suffix)
            if not objVMs:
                res.Messages.append("WARN: VM: %s not found. This VM not deleted!!!" % strVM)
                continue
            if config['debug']:
                res.Messages.append("DEBUG: Delete vm: %s" % strVM)
            uuid = xapi.VM.get_uuid(objVMs[0])
            _deleteVM(xapi, strVM, res)
            if config['debug']:
                res.Messages.append("DEBUG: VM: %s Deleted!" % strVM)
                res.Messages.append("DEBUG: Delete rights for vm: %s" % strVM)
            _res = _deleteRightsXVP(sqlCur, strUser, uuid, configLab, res)
            if not _res:
                res.Messages.append("WARN: Rights for vm: %s on the user: %s Not deleted!!!" % (strVM, strUser,))
                continue
            if config['debug']:
                res.Messages.append("DEBUG: Rights for VM: %s on the user: %s deleted!" % (strVM, strUser,))


    return

def CreateLab(configLab):
    res = StatusVLAB()
    res.Messages = []
    res.StatusOK = True

    SQLConnect = _connectDB(res)
    if not SQLConnect:
        return
    SQLCursor = SQLConnect.cursor()

    xapi, resOK = _connectXCP(res)
    if not resOK:
        return


    if configLab.Action.lower() == "create":
        _createLab(xapi, SQLCursor, configLab, res)
    elif configLab.Action.lower() == "delete":
        _deleteLab(xapi, SQLCursor, configLab, res)
    else:
        res.Messages.append("ERROR: Action is wrong!!! Action is 'create' or 'delete'")
        res.StatusOK = False

    SQLConnect.commit()

    return res

def GetNetworks():

    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True


    xapi, resOK = _connectXCP(xcpconf.config, res.Status)
    if not resOK:
        return res

    objs = _getNetworks(xapi)
    if not objs:
        res.Status.StatusOK = False
        return res

    for obj in objs:
        valueXCP = ValueXCP()
        valueXCP.Ref = obj
        valueXCP.Value= xapi.network.get_name_label(obj)
        res.Values.append(valueXCP)

    return res

def GetTemplates():
    res = ValuesXCP()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    xapi, resOK = _connectXCP(xcpconf.config, res.Status)
    if not resOK:
        return res

    objs = _getTemplates(xapi)
    if not objs:
        res.Status.StatusOK = False
        return res

    for obj in objs:
        valueXCP = ValueXCP()
        valueXCP.Ref = obj
        valueXCP.Value= xapi.VM.get_name_label(obj)
        res.Values.append(valueXCP)

    return res

def GetGroups():
    res = ValuesAD()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    _initAD(config['ldapHost'],config['ldapRoots'],res)

    for obj in _getAdGroups():
        res.Values.append(obj)

    return res

def GetStudentsByGroup(group):
    res = ValuesAD()
    res.Status = StatusVLAB()
    res.Values = []
    res.Status.Messages = []
    res.Status.StatusOK = True

    _initAD(config['ldapHost'],config['ldapRoots'],res)

    for obj in _getAdUsers(group):
        res.Values.append(obj)

    return res

global config
config = xcpconf.config

