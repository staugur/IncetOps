# -*- coding: utf-8 -*-
"""
    IncetOps.config
    ~~~~~~~~~~~~~~

    The program configuration file, the preferred configuration item, reads the system environment variable first.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from os import getenv

GLOBAL = {

    "ProcessName": "IncetOps",
    #自定义进程名.

    "Host": getenv("incetops_host", "0.0.0.0"),
    #监听地址

    "Port": getenv("incetops_port", 16000),
    #监听端口

    "LogLevel": getenv("incetops_loglevel", "DEBUG"),
    #应用日志记录级别, 依次为 DEBUG, INFO, WARNING, ERROR, CRITICAL.
}


SSO = {

    "app_name": getenv("incetops_sso_app_name", GLOBAL["ProcessName"]),
    # Passport应用管理中注册的应用名

    "app_id": getenv("incetops_sso_app_id", "app_id"),
    # Passport应用管理中注册返回的`app_id`

    "app_secret": getenv("incetops_sso_app_secret", "app_secret"),
    # Passport应用管理中注册返回的`app_secret`

    "sso_server": getenv("incetops_sso_server", "YourPassportFQDN"),
    # Passport部署允许的完全合格域名根地址，例如作者的`https://passport.saintic.com`
}


MYSQL = getenv("incetops_mysql_url")
#MYSQL数据库连接信息
#mysql://host:port:user:password:database?charset=&timezone=


REDIS = getenv("incetops_redis_url")
#Redis数据库连接信息，格式：
#redis://[:password]@host:port/db
#host,port必填项,如有密码,记得密码前加冒号,比如redis://localhost:6379/0


# 系统配置
SYSTEM = {

    "HMAC_SHA256_KEY": getenv("incetops_hmac_sha256_key", "273d32c8d797fa715190c7408ad73811"),
    # hmac sha256 key

    "AES_CBC_KEY": getenv("incetops_aes_cbc_key", "YRRGBRYQqrV1gv5A"),
    # utils.aes_cbc.CBC类中所用加密key

    "JWT_SECRET_KEY": getenv("incetops_jwt_secret_key", "WBlE7_#qDf2vRb@vM!Zw#lqrg@rdd3A6"),
    # utils.jwt.JWTUtil类中所用加密key

    "Sign": {
        "version": getenv("incetops_sign_version", "v1"),
        "accesskey_id": getenv("incetops_sign_accesskeyid", "accesskey_id"),
        "accesskey_secret": getenv("incetops_sign_accesskeysecret", "accesskey_secret"),
    }
    # utils.Signature.Signature类中所有签名配置
}


#插件配置段
PLUGINS = {

    "IncetOps": {
        "DefaultBackupDatabase": getenv("incetops_defaultbackupdatabase", MYSQL)
        # 默认备份库地址
    }
}