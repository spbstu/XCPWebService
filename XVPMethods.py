__author__ = 'artzab'

import MySQLdb
import xcpconf
try:
    import sqlite as sqlite3
except ImportError, e:
    import sqlite3

def _createRightsXVP(sqlCur, strUser, strVM, configLab, res):
    strUser = strUser.lower()

    ##Check exist rights from user
    sqlCur.execute("""
		select * from xvp_users
		where username = %s
		and vmname = %s""", (strUser + "@" + configLab.DomainKrb, strVM))
    if config['debug']:
        res.Messages.append("DEBUG: Result exec SQL exist Rights: %s " % sqlCur.rowcount)
    if len(sqlCur.fetchall()) == 0:
        if config['debug']:
            res.Messages.append("DEBUG: Insert row where VM: %s, user: %s" % (strVM, strUser))
        sqlCur.execute("""
			insert into xvp_users
			values (%s, %s, %s, %s, %s)""",
            (strUser + "@" + configLab.DomainKrb, configLab.PoolName, '*', strVM, 'all',))
        if config['debug']:
            res.Messages.append("DEBUG: Result exec SQL insert 'all' rights: %s" % sqlCur.rowcount)

    sqlCur.execute("""
		select * from xvp_users
		where username = %s
		and rights = %s""", (strUser + "@" + configLab.DomainKrb, 'none',))
    if config['debug']:
        res.Messages.append("DEBUG: Result exec SQL found 'none' rights: %s" % sqlCur.rowcount)
    if len(sqlCur.fetchall()) == 0:
        sqlCur.execute("""
			insert into xvp_users
			values (%s, %s, %s, %s, %s)""",
            (strUser + "@" + configLab.DomainKrb, configLab.PoolName, '-', '-', 'none'))
        if config['debug']:
            res.Messages.append("DEBUG: Result exec SQL add 'none' rights: %s" % sqlCur.rowcount)
    return True

def _deleteRightsXVP(sqlCur, strUser, strVM, configLab, res):
    if config['debug']:
        res.Messages.append("DEBUG: Delete row where VM: %s, user: %s" % (strVM, strUser))
    sqlCur.execute("""
		delete from xvp_users
		where username = %s
		and vmname = %s""", (strUser + "@" + configLab.DomainKrb, strVM,))
    if config['debug']:
        res.Messages.append("DEBUG: Result exec SQL, delete rights for vm: %s" % sqlCur.rowcount)
    sqlCur.execute("""
		select * from xvp_users
		where username = %s
		and rights != %s""", (strUser + "@" + configLab.DomainKrb, 'none',))
    if config['debug']:
        res.Messages.append("DEBUG: Result exec SQL, select any common rights for user: %s" % sqlCur.rowcount)
    if len(sqlCur.fetchall()) == 0:
        sqlCur.execute("""
			delete from xvp_users
			where username = %s""", (strUser + "@" + configLab.DomainKrb,))
        if config['debug']:
            res.Messages.append("DEBUG: Result exec SQL, delete common rights for user: %s" % sqlCur.rowcount)
    return True

def _connectDB(res):

    if config['SQLEngenie'] == "SQLite":
        if config['debug']:
            res.Messages.append("DEBUG: Connect to sqlite db: " + config['SQLiteBase'])

        SQLConnect = sqlite3.connect(config['SQLiteBase'])
        SQLConnect.isolation_level = None

    elif config['SQLEngenie'] == "MySQL":
        if config['debug']:
            res.Messages.append(
                "DEBUG: Connect to mysql db: %s, host: %s, user %s" % (config['SQLDB'], config['SQLHost'], config['SQLUser']))

        SQLConnect = MySQLdb.connect(host=config['SQLHost'], user=config['SQLUser'], passwd=config['SQLPassword'],
            db=config['SQLDB'], charset='utf8')
    else:
        res.StatusOK = False
        res.Messages.append("ERROR: No select valid DB engenie")
        return None

    return SQLConnect

global config
config = xcpconf.config