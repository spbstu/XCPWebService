#-*- encoding: utf-8; -*-
__author__ = 'artzab'

import ldap, ldap.sasl

###
### Main
###

def _getAdGroups():
    listGroups = []
    if not ldapInit:
        return listGroups
    for ldapRoot in ldapRoots:
        ldapResult = ldapInit.search_s(ldapRoot,ldap.SCOPE_SUBTREE, '(objectClass=group)',['cn'])
        for ldapDN, ldapEntry in ldapResult:
            listGroups.append(ldapEntry['cn'][0])
    return listGroups

def _getAdUsers(strGroup):
    listUsers = []
    if not ldapInit:
        return listUsers
    for ldapRoot in ldapRoots:
        ldapResult = ldapInit.search_s(ldapRoot,ldap.SCOPE_SUBTREE, '(&(objectClass=group)(cn=%s))'  % strGroup.encode('utf-8'), ['cn','member'])
        for ldapDN, ldapEntry in ldapResult:
            if 'member' not in ldapEntry:
                break
            for member in ldapEntry['member']:
                filter = "(&(distinguishedName=%s)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(objectClass=user)(!(objectClass=Computer)))" % member
                ldapResult2 = ldapInit.search_s(ldapRoot,ldap.SCOPE_SUBTREE, filter, ['cn','sAMAccountName'])

                for ldapDN, ldapEntry in ldapResult2:
                    listUsers.append(ldapEntry['sAMAccountName'][0].upper())
            break
    return listUsers

def _initAD(url, roots, res):
    global ldapInit
    global ldapRoots
    try:
        ldapInit = ldap.initialize("ldap://" + url)
        ldapInit.protocol_version = ldap.VERSION3
        saslInit = ldap.sasl.gssapi()
        ldapInit.sasl_interactive_bind_s("",saslInit)
        ldapRoots = roots
    except Exception, e:
        res.Messages.append("ERROR: Cannot connect to LDAP: %s, error: %s" % (url, e))
        res.SatausOK = False

ldapInit = None
ldapRoots = []

if __name__=='__main__':

    _initAD('dc2.avalon.ru',[
        "OU=Students,DC=avalon,DC=ru",
        "OU=Студенты ФУИТ,DC=avalon,DC=ru",
        ], None)

    print _getAdUsers(u'ФПС Студенты "Дизайн" 1 Семестр')