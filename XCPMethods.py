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