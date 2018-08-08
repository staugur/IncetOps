# -*- coding: utf-8 -*-
"""
    libs.tool
    ~~~~~~~~~~~~~~

    工具类

    :copyright: (c) 2018 by taochengwei.
    :license: Apache2.0, see LICENSE for more details.
"""
from __future__ import absolute_import
from utils.tool import logger, get_current_timestamp, create_mysql_engine
from utils.at import KeyGenerationClass
import re
import time
import json
import MySQLdb
import MySQLdb.cursors

class IncetDB(object):
    """封装的Inception操作类"""

    def __init__(self, host, port, max_idle_time=8*3600, connect_timeout=3, **kwargs):
        #打开数据库连接
        self.db = None
        self.host = host
        self.port = port
        self.max_idle_time = float(max_idle_time)
        self.last_use_time = time.time()
        self.kwargs = dict(host=host, port=port, charset="utf8", connect_timeout=connect_timeout, cursorclass=MySQLdb.cursors.DictCursor, **kwargs)
        try:
            self.connect()
        except Exception:
            raise

    def __repr__(self):
        try:
            version = self.db.get_server_info()
        except Exception:
            return "<Server: %s, Status: disconnected>" % self.host
        else:
            return "<Server: %s, Status: connected, Version: %s>" % (self.host, version)

    def __del__(self):
        self.close()

    def __ensure_connected(self):
        if (self.db is None or (time.time() - self.last_use_time > self.max_idle_time)):
            self.connect()
        self.last_use_time = time.time()

    def connect(self):
        self.close()
        self.db = MySQLdb.connect(**self.kwargs)
        self.db.autocommit = True

    def close(self):
        """Closes this database connection."""
        if getattr(self, "db", None) is not None:
            self.db.close()
            self.db = None

    def execute(self, sql, *args, **kwargs):
        #获取操作游标
        self.__ensure_connected()
        cur = self.db.cursor()
        try:
            cur.execute(sql, kwargs or args)
            ret = cur.fetchall()
        except MySQLdb.MySQLError:
            raise
        else:
            return ret
        finally:
            cur.close()

    def get(self, sql, *args, **kwargs):
        rows = self.execute(sql, *args, **kwargs)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

def parse_inception_result(result, scene):
    """解析inception的结果集"""
    if scene == 1:
        # 获取sqlsha1列表, errlevel列表
        return dict(sqlsha1=[ i['sqlsha1'] for i in result if i and isinstance(i, dict) and i.get('sqlsha1') ], errlevel=[ i['errlevel'] for i in result if i and isinstance(i, dict) ])
    elif scene == 2:
        # 获取errlevel列表和errormessage
        return dict(errormessage=[ i['errormessage'] for i in result if i and isinstance(i, dict) and i.get('errormessage') and i.get('errormessage') != 'None' ], errlevel=[ i['errlevel'] for i in result if i and isinstance(i, dict) ], stagestatus=[ i['stagestatus'] for i in result if i and isinstance(i, dict) and i.get('stagestatus') and i.get('stagestatus') != 'None' ])
    elif scene == 3:
        # 获取执行结果中的backup_dbname, sequence, errlevel
        return dict(backup_dbname=[ i['backup_dbname'] for i in result if i and isinstance(i, dict) and i.get('backup_dbname') and i.get('backup_dbname') != 'None' ], errlevel=[ i['errlevel'] for i in result if i and isinstance(i, dict) ], sequence=[ i['sequence'].replace("'","").replace('"','') for i in result if i and isinstance(i, dict) and i.get('sequence') and "".join(i.get('sequence').replace("'","").replace('"','').split('_')[:2]) != '00' ])

def check_sql(sqlContent):
    """针对多行情况检测sql语句"""
    if sqlContent:
        for row in sqlContent.rstrip().split("\n"):
            if row[-1] != ";":
                return "SQL has no separator"
        return True
    return False

def check_ipport(connect):
    pat = re.compile(r'^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\:([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-5]{2}[0-3][0-5])$')
    if connect and pat.match(connect):
        return True

def sql_criticalddl_check(sql_content):
    """
    识别DROP DATABASE, DROP TABLE, TRUNCATE PARTITION, TRUNCATE TABLE等高危DDL操作，因为对于这些操作，inception在备份时只能备份METADATA，而不会备份数据！
    如果识别到包含高危操作，则返回“审核不通过”
    :return msg str:
        OK表示可以通过审核；
        其他字符串表示含有高危ddl，审核不通过，为具体拒绝信息。
    """
    for row in sql_content.rstrip(';').split(';'):
        if re.match(r"([\s\S]*)drop(\s+)database(\s+.*)|([\s\S]*)drop(\s+)table(\s+.*)|([\s\S]*)truncate(\s+)partition(\s+.*)|([\s\S]*)truncate(\s+)table(\s+.*)", row.lower()):
            return "Reject High Danger SQL."
    return "OK"

def sql_inceptionpre_check(sql_content):
    """
    在提交给inception之前，预先识别一些Inception不能正确审核的SQL
    比如"alter table t1;"或"alter table test.t1;"
    以免导致inception core dump
    :param sql_content:
    :return: msg str:
        OK是预检测通过；
        其他信息不通过。
        2. msg str: false是提示信息
    """
    for row in sql_content.rstrip(';').split(';'):
        if re.match(r"(\s*)alter(\s+)table(\s+)(\S+)(\s*);|(\s*)alter(\s+)table(\s+)(\S+)\.(\S+)(\s*);", row.lower() + ";"):
            return "Pre-detect sql syntax error."
    return "OK"

def InceptionProxy(Action, sqlContent, dbData, inception, **kwargs):
    """Inception代理器-通过参数使用Inception服务处理SQL
    @kwargs:
        sd(str), 任务描述
        applicant(str)，申请人
        autoviewResult(list)，自动审核结果
        enableRemoteBackup,enableIgnoreWarnings(int)，启用备份、禁用警告
    """
    res = dict(code=1, msg=None)
    aes = KeyGenerationClass("XingkaOps.AT.Key")
    if True:
        #检查参数
        if Action in ("Check", "Execute") and sqlContent and inception and check_sql(sqlContent) == True and check_ipport(inception):
            sqlContent = sqlContent.rstrip().replace("\n", "")
            logger.debug(sqlContent)
            #高危sql检测
            scc = sql_criticalddl_check(sqlContent)
            if scc == "OK":
                # 未发现高危sql; 执行预检测
                sic = sql_inceptionpre_check(sqlContent)
                if sic == "OK":
                    # 预检测通过; 先通过dbId查出mysql
                    if dbData and isinstance(dbData, dict) and "host" in dbData and "user" in dbData and "port" in dbData and "passwd" in dbData:
                        dbData["passwd"] = aes.decrypt(dbData["passwd"])
                        # 根据不同Action，使用inception执行
                        idb = IncetDB(host=inception.split(":")[0], port=int(inception.split(":")[-1]))
                        mysql = create_mysql_engine()
                        if Action == "Check":
                            # 通过Inception检查任务中sql
                            sql = '/*--user=%s;--password=%s;--host=%s;--port=%s;--enable-check;*/\
                                inception_magic_start;\
                                %s\
                                inception_magic_commit;' %(dbData["user"], dbData["passwd"], dbData["host"], dbData["port"], sqlContent)
                            result = idb.execute(sql)
                            logger.debug(result)
                            if result is None or len(result) == 0:
                                res.update(code=2, msg="The return of Inception is null. May be something wrong with the SQL")
                            else:
                                res.update(data=result, code=0)
                        elif Action == "Execute":
                            # 通过Inception立即执行任务中sql，请先执行Check后再使用Execute
                            ebiw, taskId = "", kwargs["taskId"]
                            if int(kwargs.get("enableRemoteBackup", 1)) == 1:
                                ebiw += "--enable-remote-backup;"
                            else:
                                ebiw += "--disable-remote-backup;"
                            if int(kwargs.get("enableIgnoreWarnings", 0)) == 1:
                                ebiw += "--enable-ignore-warnings;"
                            sql = '/*--user=%s;--password=%s;--host=%s;--port=%s;--enable-execute;%s*/\
                                inception_magic_start;\
                                %s\
                                inception_magic_commit;' %(dbData["user"], dbData["passwd"], dbData["host"], dbData["port"], ebiw, sqlContent)
                            logger.debug(sql)
                            if taskId:
                                # 设置状态为执行中，并设置执行时间
                                mysql.update("update incetops_task set status=3,ftime=%s where taskId=%s", get_current_timestamp(), taskId)
                                result = idb.execute(sql)
                                logger.debug(result)
                                if result is None or len(result) == 0:
                                    status, statusMsg = 4, "Execution result is empty"
                                    res.update(code=2, msg="The return of Inception is null. May be something wrong with the SQL")
                                else:
                                    # 分析执行结果
                                    pir = parse_inception_result(result, 2)
                                    statusMsg = "\n".join(pir["errormessage"]) + "\n"
                                    if 2 in pir["errlevel"]:
                                        status = 4
                                    elif 1 in pir["errlevel"]:
                                        statusMsg += "\n".join(pir["stagestatus"])
                                        status = 4 if int(kwargs.get("enableIgnoreWarnings", 0)) == 0 else 0
                                    else:
                                        status, statusMsg = 0, "\n".join(pir["stagestatus"])
                                    res.update(data=result, code=0)
                                mysql.update("update incetops_task set status=%s,statusMsg=%s,executeResult=%s where taskId=%s", status, statusMsg, json.dumps(result), taskId)
                            else:
                                res.update(msg="Invalid taskId")
                    else:
                        res.update(msg="Invaild dbId")
                else:
                    # 预检测出sql通过inception执行可能会core dump，拒绝审核通过
                    res.update(msg=sic)
            else:
                # 发现高危sql，拒绝审核通过
                res.update(msg=scc)
        else:
            cs = check_sql(sqlContent)
            res.update(msg="There are invalid parameters" if cs == False else cs)
    return res

def InceptionOSC(Action, sqlsha1, inception):
    """查询pt-osc执行进度"""
    res = dict(code=1, msg=None)
    if Action in ("Query", "Stop") and sqlsha1 and inception and check_ipport(inception) and len(sqlsha1) == 41 and sqlsha1.startswith('*'):
        if Action == "Query":
            # 通过Inception查询osc
            sql = 'inception get osc_percent %s;'
            idb = IncetDB(host=inception.split(":")[0], port=int(inception.split(":")[-1]))
            result = idb.get(sql, sqlsha1)
            if not result:
                res.update(code=2, msg="No query to OSC progress")
            else:
                res.update(data=result, code=0)
        elif Action == "Stop":
            # 通过Inception中止OSC执行
            sql = 'inception stop alter %s;'
            idb = IncetDB(host=inception.split(":")[0], port=int(inception.split(":")[-1]))
            try:
                result = idb.get(sql, sqlsha1)
                logger.debug("stop osc result " + result)
            except Exception,e:
                res.update(msg=str(e))
            else:
                if not result:
                    res.update(code=2, msg="No query to OSC progress")
                else:
                    res.update(data=result, code=0)
    else:
        res.update(msg="There are invalid parameters")
    return res

def QueryRollbackSQL(taskId, backup_mysql_url):
    """查询任务执行成功后的SQL回滚语句"""
    res = dict(code=1, msg=None)
    if taskId and isinstance(taskId, int) and backup_mysql_url:
        dbbackup = create_mysql_engine(backup_mysql_url)
        dblocal = create_mysql_engine()
        sql = "SELECT executeResult FROM incetops_task WHERE taskId=%s AND status=0"
        data = dblocal.get(sql, taskId)
        if data and isinstance(data, dict) and data.get("executeResult"):
            result = json.loads(data["executeResult"])
            rollback_sqls = []
            for row in result:
                if row.get('backup_dbname') and row.get('backup_dbname') != 'None':
                    backup_dbname = row.get("backup_dbname")
                    opid_time = row.get("sequence").replace("'", "")
                    rowdata = dict(opid_time=opid_time, backup_dbname=backup_dbname, sql=None, rollback=None, errmsg=None)
                    # 以下是实际查询操作
                    sql_table = "select sql_statement,tablename from {}.$_$Inception_backup_information$_$ where opid_time=%s".format(backup_dbname)
                    try:
                        table_data = dbbackup.get(sql_table, opid_time)
                    except Exception,e:
                        logger.warning(e)
                        res.update(msg=str(e))
                    else:
                        if not table_data:
                            rowdata["errmsg"] = "Get table data error"
                        else:
                            rowdata["sql"] = table_data["sql_statement"]
                            sql_back = "select rollback_statement from {}.{} where opid_time=%s".format(backup_dbname, table_data['tablename'])
                            back_data = dbbackup.query(sql_back, opid_time)
                            if not back_data:
                                rowdata["errmsg"] = "Get rollback data error"
                            else:
                                rowdata["rollback"] = "\n".join([ i["rollback_statement"]  for i in back_data if isinstance(i, dict) and "rollback_statement" in i ])
                        rollback_sqls.append(rowdata)
                else:
                    continue
            if rollback_sqls:
                res.update(code=0, data=rollback_sqls)
            else:
                res.update(code=2, msg=res["msg"] or "No rollback sql")
        else:
            res.update(msg="Invaild task")
    else:
        res.update(msg="Invaild params")
    return res
