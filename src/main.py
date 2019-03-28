# -*- coding: utf-8 -*-
"""
    IncetOps.main
    ~~~~~~~~~~~~~~

    Entrance

    Docstring conventions:
    http://flask.pocoo.org/docs/0.10/styleguide/#docstrings

    Comments:
    http://flask.pocoo.org/docs/0.10/styleguide/#comments

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import os
import jinja2
import rq_dashboard
import rq_scheduler_dashboard
from config import GLOBAL, SSO, REDIS
from version import __version__
from utils.tool import err_logger, access_logger, plugin_logger
from utils.web import verify_sessionId, analysis_sessionId, get_redirect_url, get_userinfo
from views import FrontBlueprint
from flask import request, g, jsonify
from flask_pluginkit import Flask, PluginManager

__author__ = 'staugur'
__email__ = 'staugur@saintic.com'
__doc__ = '基于Inception，一个审计、执行、回滚、统计sql的开源系统'
__date__ = '2018-08-08'


# 初始化定义application
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24),
    REDIS_URL = REDIS,
    RQ_POLL_INTERVAL = 2500,
)

# 初始化插件管理器(自动扫描并加载运行)
plugin = PluginManager(app, logger=plugin_logger)

# 注册视图包中蓝图
app.register_blueprint(FrontBlueprint)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rqdashboard")
app.register_blueprint(rq_scheduler_dashboard.blueprint, url_prefix="/rqschedulerdashboard")

# 添加模板上下文变量
@app.context_processor
def GlobalTemplateVariables():
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__, "sso_server": SSO["sso_server"].strip("/")}
    return data


@app.before_request_top
def before_request():
    g.signin = verify_sessionId(request.cookies.get("sessionId"))
    g.sid, g.uid = analysis_sessionId(request.cookies.get("sessionId"), "tuple") if g.signin else (None, None)
    # 用户信息
    g.userinfo = get_userinfo(g.uid)
    app.logger.debug(g.userinfo)
    # 客户端IP地址
    g.ip = request.headers.get('X-Real-Ip', request.remote_addr)
    # 仅是重定向页面快捷定义
    g.redirect_uri = get_redirect_url()


@app.after_request
def after_request(response):
    data = {
        "status_code": response.status_code,
        "method": request.method,
        "ip": g.ip,
        "url": request.url,
        "referer": request.headers.get('Referer'),
        "agent": request.headers.get("User-Agent")
    }
    access_logger.info(data)
    return response


@app.errorhandler(500)
def server_error(error=None):
    if error:
        err_logger.error("500: {}".format(error), exc_info=True)
    message = {
        "msg": "Server Error",
        "code": 500
    }
    return jsonify(message), 500


@app.errorhandler(404)
def not_found(error=None):
    if error:
        err_logger.info("404: {}".format(error))
    message = {
        'code': 404,
        'msg': 'Not Found: ' + request.url,
    }
    return jsonify(message), 404


@app.errorhandler(403)
def Permission_denied(error=None):
    message = {
        "msg": "Authentication failed, permission denied.",
        "code": 403
    }
    return jsonify(message), 403


if __name__ == '__main__':
    app.run(host=GLOBAL["Host"], port=int(GLOBAL["Port"]), debug=True)
