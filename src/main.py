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
from config import GLOBAL, SSO
from version import __version__
from utils.tool import err_logger, access_logger
from utils.web import verify_sessionId, analysis_sessionId, get_redirect_url
from libs.plugins import PluginManager
from views import FrontBlueprint
from flask import Flask, request, g, jsonify

__author__ = 'staugur'
__email__ = 'staugur@saintic.com'
__doc__ = '基于Inception，一个审计、执行、回滚、统计sql的开源系统'
__date__ = '2018-08-08'


# 初始化定义application
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24)
)

# 初始化插件管理器(自动扫描并加载运行)
plugin = PluginManager()

# 注册多模板文件夹
loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader([p.get("plugin_tpl_path") for p in plugin.get_enabled_plugins if os.path.isdir(os.path.join(app.root_path, p["plugin_tpl_path"]))]),
])
app.jinja_loader = loader

# 注册全局模板扩展点
for tep_name, tep_func in plugin.get_all_tep.iteritems():
    app.add_template_global(tep_func, tep_name)

# 注册蓝图扩展点
for bep in plugin.get_all_bep:
    prefix = bep["prefix"]
    app.register_blueprint(bep["blueprint"], url_prefix=prefix)

# 注册视图包中蓝图
app.register_blueprint(FrontBlueprint)

# 添加模板上下文变量
@app.context_processor
def GlobalTemplateVariables():
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__, "sso_server": SSO["sso_server"].strip("/")}
    return data


@app.before_request
def before_request():
    g.signin = verify_sessionId(request.cookies.get("sessionId"))
    g.sid, g.uid = analysis_sessionId(request.cookies.get("sessionId"), "tuple") if g.signin else (None, None)
    g.ip = request.headers.get('X-Real-Ip', request.remote_addr)
    # 仅是重定向页面快捷定义
    g.redirect_uri = get_redirect_url()
    # 上下文扩展点之请求后(返回前)
    before_request_hook = plugin.get_all_cep.get("before_request_hook")
    for cep_func in before_request_hook():
        cep_func(request=request, g=g)


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
    # 上下文扩展点之请求后(返回前)
    after_request_hook = plugin.get_all_cep.get("after_request_hook")
    for cep_func in after_request_hook():
        cep_func(request=request, response=response, data=data)
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
