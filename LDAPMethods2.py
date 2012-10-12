#-*- encoding: utf-8; -*-
from BaseMethods import BaseMethods

__author__ = 'artzab'

import ldap, ldap.sasl
import xcpconf

###
### Main
###

class LDAPMethods(BaseMethods):

    @property
    def ldapInit(self):
        if self._ldapInit == None:
            self.messages("ERROR", "LDAP no init!!!", True)
        return self._ldapInit
    @ldapInit.setter
    def ldapInit(self, value): self._ldapInit = value

    @property
    def ldapRoots(self): return self._ldapRoots
    @ldapRoots.setter
    def ldapRoots(self, value): self._ldapRoots = value

    def __init__(self, logging=None, conf=None):
        BaseMethods.__init__(self, logging, conf)
        self.ldapRoots = []
        self.ldapInit = None


    def GetAdGroups(self):
        listGroups = []
        if not self.ldapInit:
            return listGroups
        for ldapRoot in self.ldapRoots:
            ldapResult = self.ldapInit.search_s(ldapRoot,ldap.SCOPE_SUBTREE, '(objectClass=group)',['cn'])
            for ldapDN, ldapEntry in ldapResult:
                listGroups.append(ldapEntry['cn'][0])
        return listGroups

    def GetAdUsers(self, strGroup):
        listUsers = []
        if not self.ldapInit:
            return listUsers
        for ldapRoot in self.ldapRoots:
            ldapResult = self.ldapInit.search_s(ldapRoot,ldap.SCOPE_SUBTREE, '(&(objectClass=group)(cn=%s))'  % strGroup.encode('utf-8'), ['cn','member'])
            for ldapDN, ldapEntry in ldapResult:
                if 'member' not in ldapEntry:
                    break
                for member in ldapEntry['member']:
                    filter = "(&(distinguishedName=%s)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(objectClass=user)(!(objectClass=Computer)))" % member
                    ldapResult2 = self.ldapInit.search_s(ldapRoot,ldap.SCOPE_SUBTREE, filter, ['cn','userPrincipalName'])

                    for ldapDN, ldapEntry in ldapResult2:
                        listUsers.append(ldapEntry['userPrincipalName'][0].upper())
                break
        return listUsers

    def InitAD(self):

        try:
            ldapInit = ldap.initialize("ldap://" + self.config['ldapHost'])
            ldapInit.protocol_version = ldap.VERSION3
            saslInit = ldap.sasl.gssapi()
            ldapInit.sasl_interactive_bind_s("",saslInit)
            self.ldapRoots = self.config['ldapRoots']
        except Exception, e:
            self.messages("ERROR", "Cannot connect to LDAP: %s, error: %s" % (self.config['ldapHost'], e), True)
            return False

        self.ldapInit = ldapInit
        self.logging.StatusOK = True
        return True

if __name__=='__main__':

    ad = LDAPMethods(conf=xcpconf.config)
    ad.InitAD()
    print ad.GetAdUsers(u'ФПС Студенты "Дизайн" 1 Семестр')
