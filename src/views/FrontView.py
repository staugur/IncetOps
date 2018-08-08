# -*- coding: utf-8 -*-
"""
    IncetOps.views.FrontView
    ~~~~~~~~~~~~~~

    The blueprint for front view.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from flask import Blueprint, g, redirect, url_for
from config import SSO
from utils.web import login_required

# 初始化前台蓝图
FrontBlueprint = Blueprint("front", __name__)

@FrontBlueprint.route('/')
def index():
    # 首页
    return redirect(url_for("IncetOps.Inception"))

@FrontBlueprint.route("/setting/")
@login_required
def userSet():
    return redirect("{}/user/setting/".format(SSO["sso_server"].strip("/")))
