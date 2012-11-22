from BaseMethods import BaseMethods

__author__ = 'artzab'

import XenAPI
import xcpconf
import pprint
import re

class XCPMethods(BaseMethods):

    @property
    def configsLabs(self, prn=False):
        if prn:
            return str(pprint.pprint(self._configsLabs))
        return self._configsLabs
    @configsLabs.setter
    def configsLabs(self, value): self._configsLabs = value

    @property
    def xapi(self):
        if not self._xapiOK:
            self.messages("ERROR","XAPI not connect to pool",True)
            return None
        return self._xapi
    @xapi.setter
    def xapi(self, value): self._xapi = value

    def __init__(self, logging=None, conf=None):
        BaseMethods.__init__(self, logging, conf)
        self.configsLabs = {}
        self._xapiOK = False


    def ConnectXCP(self):

        self.messages(mesg="Connect to xcp master host: %s, user: %s" % (self.config['PoolMasterHost'], self.config['PoolLogin']))
        try:
            xcpSession = XenAPI.Session(self.config['PoolMasterHost'])
            xcpSession.login_with_password(self.config['PoolLogin'], self.config['PoolPassword'])

            xapi = xcpSession.xenapi
        except Exception, e:
            self.logging.StatusOK = False
            self.messages(type="ERROR",mesg="Cannot connect to XCP!!!")
            return False

        self._xapiOK = True
        self.xapi = xapi
        self.logging.StatusOK = True
        return True

    def ReadConfs(self):

        xapi = self.xapi

        templ = {}
        pVlab = re.compile(r'vlab:(.*)=>(.*)', re.IGNORECASE)
        pVlabObj = re.compile(r'([^\s]+)\[([^\s]+)\]:(.*)=>(.*)', re.IGNORECASE)
        query = 'field "is_a_template" = "true" and field "is_a_snapshot" = "false"'
        templXCP = xapi.VM.get_all_records_where(query)
        for key in templXCP:
            if templXCP[key]['tags']:
                templ[key] = {'tags': templXCP[key]['tags'], 'name': templXCP[key]['name_label']}

        confs = {}
        nets = {}
        for key in templ:
            for tag in templ[key]['tags']:
                mVlab = pVlab.match(tag)
                mVlabObj = pVlabObj.match(tag)

                if mVlab:
                    mObj = 'templ'
                    vlabName= mVlab.groups()[0].strip()
                    vlabVMName= mVlab.groups()[1].strip()
                    vlabObj = templ[key]['name']
                elif mVlabObj:
                    mObj = mVlabObj.groups()[0]
                    vlabName = mVlabObj.groups()[1].strip()
                    vlabVMName= mVlabObj.groups()[2].strip()
                    vlabObj = mVlabObj.groups()[3].strip()

                if 'net' in mObj or 'tags' in mObj:
                    vlabObj = vlabObj.split(",")

                if 'net' in mObj:
                    ret = {}
                    for net in vlabObj:
                        if net not in nets:
                            objNets = xapi.network.get_by_name_label(net)
                            if objNets:
                                nets[net] = objNets[0]
                            else:
                                nets[net] = None
                        ret[net] = nets[net]
                    vlabObj = ret
                elif 'templ' in mObj:
                    vlabObj = {vlabObj: key}

                if vlabName in confs:
                    if vlabVMName in confs[vlabName]['vms']:
                        confs[vlabName]['vms'][vlabVMName][mObj] = vlabObj
                    else:
                        confs[vlabName]['vms'][vlabVMName] = {mObj: vlabObj,}
                else:
                    confs[vlabName] = {'vms': {vlabVMName: {mObj: vlabObj,}}}

        self.configsLabs = confs

        return confs

    def GetPoolName(self):
        pools = self.xapi.pool.get_all_records()
        return pools.values()[0]['name_label']

    def FindNet(self, strNet):
        return self.xapi.network.get_by_name_label(strNet)

    def GetNetworks(self):
        return self.xapi.network.get_all_records()

    def GetTemplates(self):
        listTemplates = []
        for objVM in self.xapi.VM.get_all_records():
            if self.xapi.VM.get_is_a_template(objVM) and not self.xapi.VM.get_is_a_snapshot(objVM):
                listTemplates.append(objVM)
        return listTemplates

    def GetVMs(self):
        listTemplates = []
        for objVM in self.xapi.VM.get_all_records():
            if not self.xapi.VM.get_is_a_template(objVM) and not self.xapi.VM.get_is_a_snapshot(objVM):
                listTemplates.append(objVM)
        return listTemplates

    def GetStatusVM(self, uuid):
        objVMs = self.xapi.VM.get_all_records_where('field "uuid" = "%s"' % uuid)
        if not objVMs:
            self.messages("ERROR","VM: %s not found. VM not get status!" % uuid)
            return None
        for objVM in objVMs:
            result = objVMs[objVM]["power_state"].lower()
            return result

    def ChangeStateVM(self, uuid, state):

        try:
            objVM = self.FindVMbyUUID(uuid)
        except Exception, e:
            self.messages("ERROR", "VM: %s not found. VM not change status! %s " % (uuid, e))
            return False

        if 'shutdown' in state:
            self.xapi.VM.clean_shutdown(objVM)
        elif 'reboot' in state:
            self.xapi.VM.clean_reboot(objVM)
        elif 'start' in state:
            self.xapi.VM.start(objVM, False, False)
        else:
            self.messages('ERROR', 'Wrong state to change, available next state: shutdown, reboot, start!!!')
            return False

        return True


    def FindTemplate(self, strTemplate):
        objVMs = self.FindVM(strTemplate)
        if objVMs:
            if self.xapi.VM.get_is_a_template(objVMs[0]):
                return objVMs[0]
            else:
                self.messages("WARN", "VM by name: %s is not template" % strTemplate)
        return None


    def FindVM(self, strVM):
        return self.xapi.VM.get_by_name_label(strVM)

    def FindVMbyUUID(self, uuid):
        try:
            vm = self.xapi.VM.get_by_uuid(uuid)
        except Exception, e:
            if 'UUID_INVALID' in e.details[0]:
                self.messages("WARN","Cannot find VM by UUID: %s" % uuid)
                return False
            else:
                self.messages("ERROR","Cannot find VM by UUID: %s, error: %s " % (uuid,e,),True)
                return False

        return vm

    def GetGroupsByUUID(self, uuid):

        vm = self.FindVMbyUUID(uuid)
        if not vm:
            return []
        tags = self.xapi.VM.get_tags(vm)
        if not tags:
            return []
        result = []
        for tag in tags:
            if 'group' in tag:
                result.append(tag.split(" ")[1])

        return result

    def GetVMByGroup(self, group):

        result =[]

        query = 'field "is_a_template" = "false" and field "is_a_snapshot" = "false"'
        vms = self.xapi.VM.get_all_records_where(query)

        for vm in vms:
            for tag in vms[vm]['tags']:
                if 'group' in tag and group in tag:
                    result.append(vm)

        return result

    def GetLabs(self):
        return [lab for lab in self.configsLabs]

    def CreateVM(self, strUser, vmName, nameLab):

        if vmName not in self.configsLabs[nameLab]['vms']:
            self.logging.StatusOK = False
            self.messages("ERROR","Name VM '%s' not found in conf" % vmName)
            return False

        cfgVM = self.configsLabs[nameLab]['vms'][vmName]

        strVM = strUser.split("@")[0] + "." + vmName

        ##Clone template
        self.messages("DEBUG", "Clone template: %s to vm: %s" % (cfgVM['templ'].keys()[0], strVM))
        objVM = self.xapi.VM.clone(cfgVM['templ'].values()[0], strVM)
        if not objVM:
            self.messages("ERROR", "Template: %s not clone to vm: %s" % (cfgVM['templ'].keys()[0], strVM))
            self.logging.StatusOK = False
            return False

        ##Clear all default network interfaces
        self.messages("DEBUG", "Delete VIFs cloned VM")
        objVIFs = self.xapi.VIF.get_all_records()
        for objVIF in objVIFs:
            record = objVIFs[objVIF]
            if record["VM"] == objVM:
                self.xapi.VIF.destroy(objVIF)

        ##Create network interfaces
        self.messages("DEBUG", "Create VIF for vm: %s" % strVM)
        for network in cfgVM['net']:
            cfgVIF = {
                'device': '0',
                'network': cfgVM['net'][network],
                'VM': objVM,
                'MAC': "",
                'MTU': "1500",
                'qos_algorithm_type': "",
                'qos_algorithm_params': {},
                'other_config': {}
            }
            objVIF = self.xapi.VIF.create(cfgVIF)
            if not objVIF:
                self.messages("ERROR", "VIF not create for vm: %s" % strVM)
                self.logging.StatusOK = False
                self.xapi.VM.destroy(objVM)
                return False

        self.messages("DEBUG","Set tags for vm: %s" % strVM)
        self.xapi.VM.set_tags(objVM, cfgVM['tags'])
        cfgOtherConfig = self.xapi.VM.get_other_config(objVM)
        cfgOtherConfig['folder'] = cfgVM['folder']
        self.xapi.VM.set_other_config(objVM, cfgOtherConfig)
        self.messages("DEBUG", "Provision vm: %s" % strVM)
        self.xapi.VM.provision(objVM)

        return objVM

    def DeleteVM(self, strVM):
        objVM = self.FindVM(strVM)
        if not objVM:
            self.messages("WARN", "VM: %s not found. VM not delete!" % strVM)
            return False
        objVMs = self.xapi.VM.get_all_records()
        self.messages("DEBUG", "Check power state")
        pwrState = objVMs[objVM[0]]["power_state"].lower()
        if 'halted' not in pwrState:
            self.xapi.VM.hard_shutdown(objVM[0])
        if self.config['debug']:
            self.messages("DEBUG: Delete VDIs VM: %s" % strVM)
        objVBDs = self.xapi.VBD.get_all_records()
        cfgVBDs = objVMs[objVM[0]]["VBDs"]
        for objVBD in cfgVBDs:
            record = objVBDs[objVBD]
            if 'CD' not in record["type"]:
                self.xapi.VDI.destroy(record["VDI"])
        self.xapi.VM.destroy(objVM[0])
        return True

    def GetVMsByLab(self, nameLab):

        result =[]

        if not nameLab in self.configsLabs:
            self.logging.StatusOK = False
            self.messages("ERROR","Lab %s not found in conf" % nameLab)
            return result

        for cfgVMkey in self.configsLabs[nameLab]['vms']:
            objVMs = self.FindVM(cfgVMkey)
            for objVM in objVMs:
                result.append(objVM)

        return result


if __name__=='__main__':
    xcp = XCPMethods(conf=xcpconf.config)
    xcp.ConnectXCP()
    xcp.ReadConfs()
    pprint.pprint(xcp.configsLabs)

    for name in xcp.configsLabs['1C-LAB']['vms']:
        print xcp.configsLabs['1C-LAB']['vms'][name]['templ']
