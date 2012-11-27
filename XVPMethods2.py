from BaseMethods import BaseMethods

__author__ = 'artzab'

import MySQLdb

try:
    import sqlite as sqlite3
except ImportError, e:
    import sqlite3


class XVPMethods(BaseMethods):


    @property
    def sqlCur(self):
        if not self._sqlCur:
            self.messages("ERROR", "SQL Cursor not set!!!", True)
        return self._sqlCur
    @sqlCur.setter
    def sqlCur(self, sqlCur):
        self._sqlCur = sqlCur

    @property
    def SQLConnect(self):
        if not self._SQLConnect:
            self.messages("ERROR", "SQL not connect!!!", True)
        return self._SQLConnect
    @SQLConnect.setter
    def SQLConnect(self, sqlCur):
        self._SQLConnect = sqlCur


    def CreateRightsXVP(self, strUser, strVM, poolName):

        DomainKrb = strUser.split("@")[1].upper()
        strUser = strUser.split("@")[0].lower()
        sqlCur = self.sqlCur


        ##Check exist rights from user
        sqlCur.execute("""
            select * from xvp_users
            where username = %s
            and vmname = %s""", (strUser + "@" + DomainKrb, strVM))
        self.messages("DEBUG", "Result exec SQL exist Rights: %s " % sqlCur.rowcount)
        if len(sqlCur.fetchall()) == 0:
            self.messages("DEBUG", "Insert row where VM: %s, user: %s" % (strVM, strUser))
            sqlCur.execute("""
                insert into xvp_users
                values (%s, %s, %s, %s, %s)""",
                (strUser + "@" + DomainKrb, poolName, '*', strVM, 'all',))
            if self.config['debug']:
                self.messages("DEBUG", "Result exec SQL insert 'all' rights: %s" % sqlCur.rowcount)

        sqlCur.execute("""
            select * from xvp_users
            where username = %s
            and rights = %s""", (strUser + "@" + DomainKrb, 'none',))
        self.messages("DEBUG", "Result exec SQL found 'none' rights: %s" % sqlCur.rowcount)
        if len(sqlCur.fetchall()) == 0:
            sqlCur.execute("""
                insert into xvp_users
                values (%s, %s, %s, %s, %s)""",
                (strUser + "@" + DomainKrb, poolName, '-', '-', 'none'))
            self.messages("DEBUG", "Result exec SQL add 'none' rights: %s" % sqlCur.rowcount)
        return True

    def DeleteRightsXVP(self, strUser, strVM):

        DomainKrb = strUser.split("@")[1].upper()
        strUser = strUser.split("@")[0].lower()
        sqlCur = self.sqlCur

        self.messages("DEBUG", "Delete row where VM: %s, user: %s" % (strVM, strUser))
        sqlCur.execute("""
            delete from xvp_users
            where username = %s
            and vmname = %s""", (strUser + "@" + DomainKrb, strVM,))
        self.messages("DEBUG", "Result exec SQL, delete rights for vm: %s" % sqlCur.rowcount)
        sqlCur.execute("""
            select * from xvp_users
            where username = %s
            and rights != %s""", (strUser + "@" + DomainKrb, 'none',))
        if self.config['debug']:
            self.messages("DEBUG", "Result exec SQL, select any common rights for user: %s" % sqlCur.rowcount)
        if len(sqlCur.fetchall()) == 0:
            sqlCur.execute("""
                delete from xvp_users
                where username = %s""", (strUser + "@" + DomainKrb,))
            self.messages("DEBUG", "Result exec SQL, delete common rights for user: %s" % sqlCur.rowcount)
        return True

    def GetUsersByVMUUID(self, pool, uuid, groups):

        result = []

        sqlCur = self.sqlCur

        #Find row by uuid
        sqlCur.execute("""
            select username from xvp_users
            where vmname = %s
            and poolname = %s
            and rights = 'all'""", (uuid, pool,))

        for item in sqlCur.fetchall():
            result.append(item[0])

        #Find row owner group vm
        sqlCur.execute("""
            select username from xvp_users
            where groupname in (%s)
            and poolname = %s
            and vmname = '*'
            and rights = 'all'""", (",".join(map(str,groups)), pool,))

        for item in sqlCur.fetchall():
            result.append(item[0])

        #Find row owner pool
        sqlCur.execute("""
            select username from xvp_users
            where groupname = '*'
            and poolname = %s
            and vmname = '*'
            and rights = 'all'""", (pool,))

        for item in sqlCur.fetchall():
            result.append(item[0])

        #Find row owner XVP
        sqlCur.execute("""
            select username from xvp_users
            where groupname = '*'
            and poolname = '*'
            and vmname = '*'
            and rights = 'all'""")

        for item in sqlCur.fetchall():
            result.append(item[0])

        return result

    def GetUsersByVMUUIDWithoutGroups(self, pool, uuid):

        result = []

        sqlCur = self.sqlCur

        #Find row by uuid
        sqlCur.execute("""
            select username from xvp_users
            where vmname = %s
            and poolname = %s
            and rights = 'all'""", (uuid, pool,))

        for item in sqlCur.fetchall():
            result.append(item[0])

        return result

    def GetVMUUIDByUser(self, pool, strUser):

        result = []

        sqlCur = self.sqlCur

        sqlCur.execute("""
            select count(*) from xvp_users
            where username = %s
            and (poolname = %s or poolname = '*')
            and rights = 'all'
            and groupname = '*'
            and vmname = '*'""",(strUser, pool,))

        if sqlCur.fetchall()[0][0]>0:
            result.append('*')


        sqlCur.execute("""
            select vmname from xvp_users
            where username = %s
            and poolname = %s
            and rights = 'all'
            and vmname != '-'
            and vmname != '*'""",(strUser, pool,))

        for item in sqlCur.fetchall():
            result.append(item[0])

        return result

    def GetVMGroupByUser(self, pool, strUser):

        result = []

        sqlCur = self.sqlCur

        sqlCur.execute("""
            select count(*) from xvp_users
            where username = %s
            and (poolname = %s or poolname = '*')
            and rights = 'all'
            and groupname = '*'
            and vmname = '*'""",(strUser, pool,))

        if sqlCur.fetchall()[0][0]>0:
            result.append('*')
            return result


        sqlCur.execute("""
            select groupname from xvp_users
            where username = %s
            and poolname = %s
            and rights = 'all'
            and groupname != '*'
            and vmname = '*'""",(strUser, pool,))

        for item in sqlCur.fetchall():
            result.append(item[0])

        return result

    def ConnectDB(self):

        if self.config['SQLEngenie'] == "SQLite":
            self.messages("DEBUG", "Connect to sqlite db: " + self.config['SQLiteBase'])

            SQLConnect = sqlite3.connect(self.config['SQLiteBase'])
            SQLConnect.isolation_level = None

        elif self.config['SQLEngenie'] == "MySQL":
            self.messages("DEBUG", "Connect to mysql db: %s, host: %s, user %s" % (self.config['SQLDB'], self.config['SQLHost'], self.config['SQLUser']))

            SQLConnect = MySQLdb.connect(host=self.config['SQLHost'], user=self.config['SQLUser'], passwd=self.config['SQLPassword'],
                db=self.config['SQLDB'], charset='utf8')
        else:
            self.logging.StatusOK = False
            self.messages("ERROR", "No select valid DB engenie")
            return False

        self.SQLConnect = SQLConnect
        self.logging.StatusOK = True
        return True
