__author__ = 'artzab'

import XenAPI
import xcpconf

from WSPropertyVLAB import *

def _findNet(xapi, strNet):
    return xapi.network.get_by_name_label(strNet)

def _getNetworks(xapi):
    return xapi.network.get_all_records()
def _getTemplates(xapi):
    listTemplates = []
    for objVM in xapi.VM.get_all_records():
        if xapi.VM.get_is_a_template(objVM) and not xapi.VM.get_is_a_snapshot(objVM):
            listTemplates.append(objVM)
    return listTemplates

def _getVMs(xapi):
    listTemplates = []
    for objVM in xapi.VM.get_all_records():
        if not xapi.VM.get_is_a_template(objVM) and not xapi.VM.get_is_a_snapshot(objVM):
            listTemplates.append(objVM)
    return listTemplates

def _getStatusVM(xapi, uuid, res):
    result = "NONE"
    objVMs = xapi.VM.get_all_records()
    objVM = _findVMbyUUID(xapi, uuid)
    if not objVM:
        res.Messages.append("ERROR: VM: %s not found. VM not get status!" % uuid)
        return None
    result = objVMs[objVM]["power_state"].lower()
    return result

def _changeStateVM(xapi, uuid, state, res):

    try:
        objVM = _findVMbyUUID(xapi, uuid)
    except Exception, e:
        res.Messages.append("ERROR: VM: %s not found. VM not change status! %s " % (uuid, e))
        return False

    if 'shutdown' in state:
        xapi.VM.clean_shutdown(objVM)
    elif 'reboot' in state:
        xapi.VM.clean_reboot(objVM)
    elif 'start' in state:
        xapi.VM.start(objVM)
    else:
        res.Messages.append('ERROR: Wrong state to change, avalible next state: shutdown, reboot, start!!!')
        return False

    return True


def _findTemplate(xapi, strTemplate, res):
    objVMs = findVM(xapi, strTemplate)
    if objVMs:
        if xapi.VM.get_is_a_template(objVMs[0]):
            return objVMs[0]
        else:
            res.Messages.append("WARN: VM by name: %s is not template" % strTemplate)
    return None


def _findVM(xapi, strVM):
    return xapi.VM.get_by_name_label(strVM)

def _findVMbyUUID(xapi, uuid):
    return xapi.VM.get_by_uuid(uuid)

def _readConfs(xapi):
    _templ = {}
    pVlab = re.compile(r'vlab:(.*)=>(.*)', re.IGNORECASE)
    pVlabObj = re.compile(r'([^\s]+)\[([^\s]+)\]:(.*)=>(.*)', re.IGNORECASE)
    _templXCP = xapi.VM.get_all_records_where('field "is_a_template" = "true" and field "is_a_snapshot" = "false"')

    for key in _templXCP:
        if _templXCP[key]['tags']:
            _templ[key] = {'tags': _templXCP[key]['tags'], 'name': _templXCP[key]['name_label']}

    _confs = {}
    _nets = {}
    for key in _templ:
        for tag in _templ[key]['tags']:
            mVlab = pVlab.match(tag)
            mVlabObj = pVlabObj.match(tag)

            if mVlab:
                _mObj = 'templ'
                _vlabName= mVlab.groups()[0].strip()
                _vlabVMName= mVlab.groups()[1].strip()
                _vlabObj = _templ[key]['name']
            elif mVlabObj:
                _mObj = mVlabObj.groups()[0]
                _vlabName = mVlabObj.groups()[1].strip()
                _vlabVMName= mVlabObj.groups()[2].strip()
                _vlabObj = mVlabObj.groups()[3].strip()

            if 'net' in _mObj or 'tags' in _mObj:
                _vlabObj = _vlabObj.split(",")

            if 'net' in _mObj:
                _ret = {}
                for _net in _vlabObj:
                    if _net not in _nets:
                        _objNets = xapi.network.get_by_name_label(_net)
                        if _objNets:
                            _nets[_net] = _objNets[0]
                        else:
                            _nets[_net] = None
                    _ret[_net] = _nets[_net]
                _vlabObj = _ret
            elif 'templ' in _mObj:
                _vlabObj = {_vlabObj: key}

            if _vlabName in _confs:
                if _vlabVMName in _confs[_vlabName]['vms']:
                    _confs[_vlabName]['vms'][_vlabVMName][_mObj] = _vlabObj
                else:
                    _confs[_vlabName]['vms'][_vlabVMName] = {_mObj: _vlabObj,}
            else:
                _confs[_vlabName] = {'vms': {_vlabVMName: {_mObj: _vlabObj,}}}

    return _confs

def _createVM(xapi, strUser, cfgVM, res):
    strVM = strUser + cfgVM.Suffix

    ##Clone template
    if config['debug']:
        res.Messages.append("DEBUG: Clone template: %s to vm: %s" % (cfgVM.Template.Value, strVM))
    objVM = xapi.VM.clone(cfgVM.Template.Ref, strVM)
    if not objVM:
        res.Messages.append("ERROR: Template: %s not clone to vm: %s" % (cfgVM.Template.Value, strVM))
        res.StatusOK = False
        return False

    ##Clear all default network interfaces
    if config['debug']:
        res.Messages.append("DEBUG: Delete VIFs cloned VM")
    objVIFs = xapi.VIF.get_all_records()
    for objVIF in objVIFs:
        record = objVIFs[objVIF]
        if record["VM"] == objVM:
            xapi.VIF.destroy(objVIF)

    ##Create network interfaces
    if config['debug']:
        res.Messages.append("DEBUG: Create VIF for vm: %s" % strVM)
    for network in cfgVM.Networks:
        cfgVIF = {
            'device': '0',
            'network': network.Ref,
            'VM': objVM,
            'MAC': "",
            'MTU': "1500",
            'qos_algorithm_type': "",
            'qos_algorithm_params': {},
            'other_config': {}
        }
        objVIF = xapi.VIF.create(cfgVIF)
        if not objVIF:
            res.Messages.append("ERROR: VIF not create for vm: %s" % strVM)
            res.StatusOK = False
            xapi.VM.destroy(objVM)
            return False
    if config['debug']:
        res.Messages.append("DEBUG: Set tags for vm: %s" % strVM)
    cfgTags = []
    for tag in cfgVM.Tags:
        cfgTags.append(tag)
    xapi.VM.set_tags(objVM, cfgTags)
    cfgOtherConfig = xapi.VM.get_other_config(objVM)
    cfgOtherConfig['folder'] = cfgVM.Folder
    xapi.VM.set_other_config(objVM, cfgOtherConfig)
    if config['debug']:
        res.Messages.append("DEBUG: Provision vm: %s" % strVM)
    xapi.VM.provision(objVM)

    return objVM

def _deleteVM(xapi, strVM, res):
    objVM = _findVM(xapi, strVM)
    if not objVM:
        res.Messages.append("WARN: VM: %s not found. VM not delete!" % strVM)
        return False
    objVMs = xapi.VM.get_all_records()
    if config['debug']:
        res.Messages.append("DEBUG: Check power state")
    pwrState = objVMs[objVM[0]]["power_state"].lower()
    if 'halted' not in pwrState:
        xapi.VM.hard_shutdown(objVM[0])
    if config['debug']:
        res.Messages.append("DEBUG: Delete VDIs VM: %s" % strVM)
    objVBDs = xapi.VBD.get_all_records()
    cfgVBDs = objVMs[objVM[0]]["VBDs"]
    for objVBD in cfgVBDs:
        record = objVBDs[objVBD]
        if 'CD' not in record["type"]:
            xapi.VDI.destroy(record["VDI"])
    xapi.VM.destroy(objVM[0])
    return True

def _connectXCP(res):

    if config['debug']:
        res.Messages.append(
            "DEBUG: Connect to xcp master host: " + config['PoolMasterHost'] + ", user: " + config['PoolLogin'])
    try:
        xcpSession = XenAPI.Session(config['PoolMasterHost'])
        xcpSession.login_with_password(config['PoolLogin'], config['PoolPassword'])

        xapi = xcpSession.xenapi
    except Exception, e:
        res.StatusOK = False
        res.Messages.append("ERROR: Cannot connect to XCP!!!")
        return None, False

    return xapi, True

config = xcpconf.config