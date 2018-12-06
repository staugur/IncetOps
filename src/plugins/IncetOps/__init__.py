# -*- coding: utf-8 -*-
"""
    IncetOps.plugins.IncetOps
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    基于Inception，一个审计、执行、回滚、统计sql的开源系统，做的sql上线平台

    :copyright: (c) 2018 by taochengwei.
    :license: MIT, see LICENSE for more details.
"""

#: Importing these two modules is the first and must be done.
#: 首先导入这两个必须模块
from __future__ import absolute_import
from libs.base import PluginBase
#: Import the other modules here, and if it's your own module, use the relative Import. eg: from .lib import Lib
#: 在这里导入其他模块, 如果有自定义包目录, 使用相对导入, 如: from .lib import Lib
from flask import Blueprint, request, render_template, g
from flask_restful import Api, Resource
from version import __version__ as version
from config import PLUGINS
from utils.tool import DO, logger
from utils.web import login_required
from .libs.service import InceptionService, DBService, TaskService, MiscService
#：Your plug-in name must be consistent with the plug-in directory name.
#：你的插件名称，必须和插件目录名称等保持一致.
__plugin_name__ = "IncetOps"
#: Plugin describes information. What does it do?
#: 插件描述信息,什么用处.
__description__ = "SQL审计、执行、回滚系统"
#: Plugin Author
#: 插件作者
__author__      = "taochengwei <staugur@saintic.com>"
#: Plugin Version
#: 插件版本
__version__     = version
#: Plugin Url
#: 插件主页
__url__         = "https://github.com/staugur/IncetOps"
#: Plugin License
#: 插件许可证
__license__     = "MIT"
#: Plugin License File
#: 插件许可证文件
__license_file__= "LICENSE"
#: Plugin Readme File
#: 插件自述文件
__readme_file__ = "README"
#: Plugin state, enabled or disabled, default: enabled
#: 插件状态, enabled、disabled, 默认enabled
__state__       = "enabled"


plugin_blueprint = Blueprint("IncetOps", "IncetOps")
@plugin_blueprint.route("/statistics")
@login_required
def statistics():
    return render_template("IncetOps/statistics/index.html")

@plugin_blueprint.route("/Inception")
@login_required
def Inception():
    return render_template("IncetOps/Inception/index.html")

@plugin_blueprint.route("/db")
@login_required
def db():
    return render_template("IncetOps/db/index.html")

@plugin_blueprint.route("/task")
@login_required
def task():
    View = request.args.get("View")
    if View == "TaskOSC":
        return render_template("IncetOps/task/osc.html")
    return render_template("IncetOps/task/index.html")

@plugin_blueprint.route("/help")
@login_required
def help():
    return render_template("IncetOps/help/index.html")


class IncetOpsApi(Resource):

    @login_required
    def get(self):
        res = dict(msg=None)
        Action = request.args.get("Action")
        if Action == "InceptionGetList":
            #获取inception服务列表
            res = g.incetops.inception.GetList()
        elif Action == "DBGetList":
            #获取db服务列表
            res = g.incetops.db.GetList()
        elif Action == "TaskGetList":
            #获取任务列表
            sort = request.args.get("sort") or "desc"
            page = request.args.get("page") or 1
            limit = request.args.get("limit") or 10
            res = g.incetops.task.GetList(page=page, limit=limit, sort=sort)
        elif Action == "MiscGetApplicants":
            res = g.incetops.misc.get_applicants()
        elif Action == "MiscGetStatistic":
            res = g.incetops.misc.get_statistic()
        return res

    @login_required
    def post(self):
        res = dict(msg=None)
        Action = request.args.get("Action")
        if Action == "InceptionAdd":
            #添加inception服务
            connect = request.form.get("connect")
            sd = request.form.get("sd")
            res = g.incetops.inception.Add(connect, sd)
        elif Action == "DBAdd":
            #添加DB服务
            host = request.form.get("host")
            port = request.form.get("port", 3306)
            user = request.form.get("user", "root")
            passwd = request.form.get("passwd")
            sd = request.form.get("sd")
            ris = request.form.get("ris", "")
            res = g.incetops.db.Add(host, port, user, passwd, sd, ris)
        elif Action == "TaskCheck":
            #检查任务中SQL
            dbId = int(request.form.get("dbId"))
            inception = request.form.get("inception")
            sqlContent = request.form.get("sqlContent")
            res = g.incetops.task.AutoCheck(sqlContent, dbId, inception)
        elif Action == "TaskAdd":
            #提交任务
            #必须项
            sd = request.form.get("sd")
            dbId = int(request.form.get("dbId"))
            inception = request.form.get("inception")
            sqlContent = request.form.get("sqlContent")
            applicant = request.form.get("applicant")
            #可选默认项
            enableRemoteBackup = int(request.form.get("enableRemoteBackup", 0))
            enableIgnoreWarnings = int(request.form.get("enableIgnoreWarnings", 0))
            executeNow = int(request.form.get("executeNow", 0))
            # timer是日期字符串，要符合格式
            timer = request.form.get("timer") or 0
            res = g.incetops.task.AddExecuteTask(sqlContent, dbId, inception, sd=sd, enableRemoteBackup=enableRemoteBackup, enableIgnoreWarnings=enableIgnoreWarnings, executeNow=executeNow, timer=timer, applicant=applicant)
        elif Action == "TaskQueryOSC":
            #获取任务中pt-osc执行进度
            res = g.incetops.task.QueryOSC(request.form.get("sqlsha1"), request.form.get("inception"))
        elif Action == "TaskStopOSC":
            #中止osc执行
            res = g.incetops.task.StopOSC(request.form.get("sqlsha1"), request.form.get("inception"))
        elif Action == "TaskRollback":
            taskId = int(request.form.get("taskId"))
            backup_mysql_url = request.form.get("backup_mysql_url") or PLUGINS["IncetOps"]["DefaultBackupDatabase"]
            res = g.incetops.task.QueryRollback(taskId, backup_mysql_url)
        return res

    @login_required
    def delete(self):
        res = dict(msg=None)
        Action = request.args.get("Action")
        if Action == "InceptionDel":
            #删除inception服务
            res = g.incetops.inception.Del(request.form.get("id"))
        elif Action == "DBDel":
            #删除DB服务
            res = g.incetops.db.Del(request.form.get("id"))
        elif Action == "TaskCancel":
            #取消定时任务
            res = g.incetops.task.CancelTimerTask(int(request.form.get("taskId")))
        return res


api = Api(plugin_blueprint)
api.add_resource(IncetOpsApi, '/api', '/api/', endpoint='IncetOpsApi')

#: 返回插件主类
def getPluginClass():
    return IncetOpsMain

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class IncetOpsMain(PluginBase):
    """ 继承自PluginBase基类 """

    def __init__(self):
        super(IncetOpsMain, self).__init__()
        self.inception = InceptionService()
        self.db = DBService()
        self.task = TaskService()
        self.misc = MiscService()

    def _bindHook(self):
        g.incetops = DO({
            "inception": self.inception,
            "db": self.db,
            "task": self.task,
            "misc": self.misc,
        })

    def register_hep(self):
        """注册上下文入口, 返回扩展点名称及执行的函数"""
        cep = {"before_request_hook": self._bindHook}
        return cep

    def register_bep(self):
        """注册蓝图入口, 返回蓝图路由前缀及蓝图名称"""
        bep = {"prefix": "/IncetOps", "blueprint": plugin_blueprint}
        return bep
