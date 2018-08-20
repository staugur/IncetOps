# -*- coding: utf-8 -*-
"""
    libs.service
    ~~~~~~~~~~~~~~

    服务类

    :copyright: (c) 2018 by taochengwei.
    :license: Apache2.0, see LICENSE for more details.
"""
from __future__ import absolute_import
from libs.base import PluginBase
import json
from utils.tool import logger, create_mysql_engine, ip_check, number_check, get_current_timestamp, datetime_to_timestamp, timestamp_to_utcdatetime, timestamp_datetime, timestamp_after_timestamp
from utils.aes_cbc import CBC as KeyGenerationClass
from torndb import IntegrityError
from config import PLUGINS
from .tool import InceptionProxy, InceptionOSC, QueryRollbackSQL, parse_inception_result


class TimingLimitError(Exception):
    pass


class InceptionService(PluginBase):
    """Inception服务管理与连接"""

    def GetList(self):
        """获取列表"""
        res = dict(msg=None, code=1)
        sql = "SELECT id,sd,host,port,ctime FROM incetops_inception"
        try:
            data = self.mysql.query(sql)
        except:
            res.update(msg="System exception")
        else:
            res.update(code=0, data=data, count=len(data))
        return res

    def Add(self, connect, sd):
        """添加一个服务
        @param connect str: 地址:端口，例如127.0.0.1:6669，端口默认6669可以省略
        @param sd str: 这个连接的描述
        """
        res = dict(msg=None, code=1)
        if sd and connect:
            host, port = connect.split(":") if ":" in connect else (connect, 6669)
            if ip_check(host) and number_check(port):
                sql = "INSERT INTO incetops_inception (sd,host,port,ctime) VALUES(%s,%s,%s,%s)"
                try:
                    self.mysql.insert(sql, sd, host, port, get_current_timestamp())
                except IntegrityError:
                    res.update(msg="Inception connection already exists")
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System exception")
                else:
                    res.update(code=0)
            else:
                res.update(msg="Invaild connect")
        else:
            res.update(msg="Invaild params")
        return res

    def Del(self, cid):
        """删除一个服务，cid即主键id"""
        res = dict(msg=None, code=1)
        sql = "DELETE FROM incetops_inception WHERE id=%s"
        try:
            self.mysql.execute(sql, cid)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="Delte fail")
        else:
            res.update(code=0)
        return res


class DBService(PluginBase):
    """数据库服务管理与连接"""

    def __init__(self):
        super(DBService, self).__init__()
        self.aes = KeyGenerationClass()

    def Encrypt(self, text):
        """加密字符串"""
        return self.aes.encrypt(text)

    def Decrypt(self, text):
        """解密字符串"""
        return self.aes.decrypt(text)

    def Get(self, dbId):
        """通过dbId获取MySQL实例数据"""
        sql = "select host,port,user,passwd from incetops_db where id=%s"
        try:
            data = self.mysql.get(sql, dbId)
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            return data

    def GetList(self):
        """获取列表"""
        res = dict(msg=None, code=1)
        sql = "SELECT id,sd,host,port,user,ris,ctime FROM incetops_db"
        try:
            data = self.mysql.query(sql)
        except:
            res.update(msg="System exception")
        else:
            res.update(code=0, data=data, count=len(data))
        return res

    def Add(self, host, port, user, passwd, sd, ris=''):
        """添加一个服务
        @param host,port,user,passwd，分别对应db的地址:端口:用户:密码
        @param sd str: 这个db的描述
        @param ris str: 即推荐的inception的地址:端口，例如127.0.0.1:6669，端口默认6669
        """
        res = dict(msg=None, code=1)
        if ris:
            ihost, iport = ris.split(":") if ":" in ris else (ris, 6669)
            if not ip_check(ihost) or not number_check(iport):
                res.update(msg="Invaild ris")
                return res
        if sd and host and port and user and passwd:
            if " " in passwd or "%" in passwd:
                res.update(msg="Password has spaces or %")
                return res
            if number_check(port):
                sql = "INSERT INTO incetops_db (sd,host,port,user,passwd,ris,ctime) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                try:
                    self.mysql.insert(sql, sd, host, port, user, self.Encrypt(passwd), ris, get_current_timestamp())
                except IntegrityError:
                    res.update(msg="DB connection already exists")
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="System exception")
                else:
                    res.update(code=0)
            else:
                res.update(msg="Invaild db port")
        else:
            res.update(msg="Invaild params")
        return res

    def Del(self, cid):
        """删除一个服务，cid即主键id"""
        res = dict(msg=None, code=1)
        sql = "DELETE FROM incetops_db WHERE id=%s"
        try:
            self.mysql.execute(sql, cid)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="Delte fail")
        else:
            res.update(code=0)
        return res


class TaskService(PluginBase):

    def __init__(self):
        super(TaskService, self).__init__()
        self.dbService = DBService()

    def Get(self, taskId):
        """通过taskId获取任务数据"""
        if not isinstance(taskId, int):
            return
        sql = "select taskId,timer,timer_id from incetops_task where taskId=%s"
        try:
            data = self.mysql.get(sql, taskId)
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            return data

    def GetList(self, page=1, limit=10, sort="desc"):
        """ 获取任务列表 
        分页参数：
        @param page int: 请求页数，从1开始
        @param limit int: 每页数据量
        @param sort str: 排序，可选值asc正序、desc倒序
        """
        res = dict(code=1, msg=None)
        # 检查参数
        try:
            page = int(page)
            limit = int(limit)
            sort = sort.upper()
            if page < 1 or limit < 1 or not sort in ("ASC", "DESC"):
                raise
        except:
            res.update(code=2, msg="There are invalid parameters")
        else:
            # mysql处分页
            # select * from xxx where xxx order by xx sort limit offset(page不为0时=(page-1)*limit),rows(limit);
            sql1 = "SELECT taskId,dbId,t.sd taskSd,inception,applicant,t.ctime,status,statusMsg,timer,timer_id,sqlContent,autoviewResult,autoviewSQLSHA1,enableIgnoreWarnings,enableRemoteBackup,executeResult,ftime,d.sd dbSd,host,port,user FROM incetops_task t LEFT JOIN incetops_db d ON t.dbId = d.id ORDER BY taskId {} LIMIT {},{}".format(sort, (page-1)*limit, limit)
            sql2 = "SELECT count(*) as count FROM incetops_task"
            try:
                data1 = self.mysql.query(sql1)
                data2 = self.mysql.get(sql2)
            except Exception, e:
                logger.error(e, exc_info=True)
                res.update(msg="System is abnormal", code=3)
            else:
                res.update(data=data1, code=0, count=data2.get("count"))
        return res

    def AutoCheck(self, sqlContent, dbId, inception):
        """自动检查SQL"""
        return InceptionProxy("Check", sqlContent, self.dbService.Get(dbId), inception)

    def AddExecuteTask(self, sqlContent, dbId, inception, **kwargs):
        """添加记录并执行任务，流程：
        通过代理器执行Check获取结果，code为0并且检查参数通过则继续；判断立即执行或定时执行
        # 立即执行
            #  以下是准备写入到MySQL的数据
            1. 解析Check结果，判断errlevel，如果有2，status=1(自动审核失败)；如果有1，且不忽略警告status=1，忽略警告则status=2
            2. status=2时写入mysql，成功后提交给rq去执行，
            3. status=1不允许提交
        # 定时执行
            1. 定时执行时，解析定时时间放到rqscheduler执行，所需函数及参数同2
        """
        # 获取其他需要参数，必须项有sd、dbId、inception、applicant，可选默认项
        res = self.AutoCheck(sqlContent, dbId, inception)
        if res["code"] == 0:
            sqlContent = sqlContent.rstrip().replace("\n", "")
            autoviewResult = res["data"]
            res = dict(code=1, msg=None)
            sd = kwargs["sd"]
            applicant = kwargs["applicant"]
            enableRemoteBackup = int(kwargs.get("enableRemoteBackup", 1))
            enableIgnoreWarnings = int(kwargs.get("enableIgnoreWarnings", 0))
            executeNow = int(kwargs.pop("executeNow", 1))
            timer = kwargs.pop("timer") or 0
            if sd and applicant and autoviewResult and isinstance(autoviewResult, (list, tuple)):
                # 参数验证完毕，解析Check结果获取sqlsha1、errlevel
                pir, status = parse_inception_result(autoviewResult, 1), 0
                if 2 in pir["errlevel"]:
                    status = 1
                elif 1 in pir["errlevel"]:
                    status = 1 if enableIgnoreWarnings == 0 else 2
                else:
                    status = 2
                if status == 2:
                    # 立即执行与定时执行
                    oldtimer = timer
                    if executeNow == 0:
                        # timer指秒数，且不能小于5分钟，表示当前时间多少秒后执行
                        status = 7
                        try:
                            timer = datetime_to_timestamp(timer) - get_current_timestamp()
                            if timer < 300:
                                raise TimingLimitError
                        except TimingLimitError:
                            res.update(msg="Invaild timing")
                            return res
                        except Exception:
                            res.update(msg="Invaild timer")
                            return res
                        logger.debug("now:{}, timer param string: {}, seconds: {}, execute at {}, utc: {}".format(timestamp_datetime(get_current_timestamp()), oldtimer, timer, timestamp_datetime(timestamp_after_timestamp(seconds=timer)), timestamp_to_utcdatetime(timestamp_after_timestamp(seconds=timer))))
                    else:
                        timer = 0
                    try:
                        sql = 'insert into incetops_task (dbId,sd,inception,applicant,ctime,status,timer,sqlContent,autoviewResult,autoviewSQLSHA1,enableIgnoreWarnings,enableRemoteBackup) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                        taskId = self.mysql.insert(sql, dbId, sd, inception, applicant, get_current_timestamp(), status, timer, sqlContent, json.dumps(autoviewResult), ",".join(pir['sqlsha1']), enableIgnoreWarnings, enableRemoteBackup)
                    except Exception,e:
                        logger.error(e, exc_info=True)
                        res.update(msg="System is abnormal")
                    else:
                        kwargs["taskId"] = taskId
                        kwargs["timeout"] = 3600
                        if executeNow == 1:
                            self.asyncQueueHigh.enqueue_call(func=InceptionProxy, args=("Execute", sqlContent, self.dbService.Get(dbId), inception), kwargs=kwargs, timeout=kwargs["timeout"])
                        else:
                            job = self.asyncScheduler.enqueue_at(timestamp_to_utcdatetime(timestamp_after_timestamp(seconds=timer)), InceptionProxy, "Execute", sqlContent, self.dbService.Get(dbId), inception, **kwargs)
                            self.mysql.update("update incetops_task set timer_id=%s where taskId=%s", job.id, taskId)
                            logger.debug(self.asyncScheduler.get_jobs())
                            logger.debug(job.to_dict())
                        res.update(code=0, taskId=taskId)
                else:
                    res.update(msg="Automatic review rejection")
            else:
                res.update(msg="There are invalid parameters")
        return res

    def QueryOSC(self, sqlsha1, inception):
        """查询osc进度"""
        return InceptionOSC("Query", sqlsha1, inception)

    def StopOSC(self, sqlsha1, inception):
        """中止osc"""
        return InceptionOSC("Stop", sqlsha1, inception)

    def QueryRollback(self, taskId, backup_mysql_url):
        """查询任务中产生的回滚语句"""
        return QueryRollbackSQL(taskId, backup_mysql_url)

    def CancelTimerTask(self, taskId):
        """取消定时任务
        @param taskId int: 任务id
        """
        res = dict(code=1, msg=None)
        data = self.Get(taskId)
        if data and isinstance(data, dict) and len(data.get("timer_id", "")) == 36:
            try:
                self.asyncScheduler.cancel(data.timer_id)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg=str(e))
            else:
                self.mysql.update("update incetops_task set status=5 where taskId=%s", taskId)
                res.update(code=0)
        else:
            res.update(msg="Invaild taskId")
        return res

class MiscService(PluginBase):
    """其他杂项管理"""


    def get_applicants(self):
        sql = "SELECT applicant FROM incetops_task"
        data = self.mysql.query(sql)
        data = list(set([ i['applicant'] for i in data ]))
        return dict(code=0, data=data)

    def get_statistic(self):
        """统计数据
        # 直接mysql计算各类型百分比，返回4位float
            select format(sum((usedb)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) usedb_rate, format(sum((deleting)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) deleting_rate, format(sum((inserting)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) inserting_rate, format(sum((updating)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) updating_rate, format(sum((selecting)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) selecting_rate, format(sum((altertable)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) altertable_rate, format(sum((createtable)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) createtable_rate, format(sum((droptable)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) droptable_rate, format(sum((createdb)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) createdb_rate, format(sum((truncating)/(usedb+deleting+inserting+updating+selecting+altertable+createtable+droptable+createdb+truncating))/count(1), 4) truncating_rate from inception.statistic;

        # 查询各类型总数量
            select format(sum(usedb), 0) usedb,format(sum(deleting), 0) deleting,format(sum(inserting), 0) inserting,format(sum(updating), 0) updating,format(sum(selecting), 0) selecting,format(sum(altertable), 0) altertable,format(sum(createtable), 0) createtable,format(sum(droptable), 0) droptable,format(sum(createdb), 0) createdb,format(sum(truncating), 0) truncating from inception.statistic;

        # 暂时只统计了大分类，alter子分类图表参考http://echarts.baidu.com/examples/editor.html?c=pie-nest
        """
        res = dict(code=1, msg=None)
        sql = 'select format(sum(usedb), 0) usedb,format(sum(deleting), 0) deleting,format(sum(inserting), 0) inserting,format(sum(updating), 0) updating,format(sum(selecting), 0) selecting,format(sum(altertable), 0) altertable,format(sum(createtable), 0) createtable,format(sum(droptable), 0) droptable,format(sum(createdb), 0) createdb,format(sum(truncating), 0) truncating,format(sum(renaming), 0) renaming,format(sum(createindex), 0) createindex,format(sum(dropindex), 0) dropindex,format(sum(addcolumn), 0) addcolumn,format(sum(dropcolumn), 0) dropcolumn,format(sum(changecolumn), 0) changecolumn,format(sum(alteroption), 0) alteroption,format(sum(alterconvert), 0) alterconvert from inception.statistic'
        try:
            backup_mysql = create_mysql_engine(PLUGINS["IncetOps"]["DefaultBackupDatabase"])
            data = backup_mysql.get(sql)
        except Exception,e:
            res.update(msg=str(e))
            logger.warning(e, exc_info=True)
        else:
            if data and isinstance(data, dict):
                FirstType = ["usedb", "deleting", "inserting", "updating", "selecting", "altertable", "createtable", "droptable", "createdb", "truncating"]
                SecondType = ["renaming", "createindex", "dropindex", "addcolumn", "dropcolumn", "changecolumn", "alteroption", "alterconvert"]
                data = dict(first=[ {"name": k, "value": int(v)} for k,v in data.iteritems() if k in FirstType ], second=[ {"name": k, "value": int(v)} for k,v in data.iteritems() if k in SecondType ])
                res.update(code=0, data=data, catalogs=data.keys())
        return res
