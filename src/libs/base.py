# -*- coding: utf-8 -*-
"""
    IncetOps.libs.base
    ~~~~~~~~~~~~~~

    Base class: dependent services, connection information, and public information.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from utils.tool import plugin_logger, create_mysql_engine
from config import REDIS
from redis import from_url
from rq import Queue
from rq_scheduler import Scheduler


class ServiceBase(object):
    """ 所有服务的基类 """

    def __init__(self):
        #设置全局超时时间(如连接超时)
        self.timeout= 2
        # 建立redis单机连接
        if REDIS:
            self.redis = from_url(REDIS)
        else:
            raise RedisURLError("The value of the REDIS in the config.py file is not valid.")
        # 建立mysql连接
        self.mysql = create_mysql_engine()
        self.asyncQueueHigh = Queue(name='high', connection=self.redis)
        self.asyncScheduler = Scheduler(queue=self.asyncQueueHigh, connection=self.redis, interval=1)


class PluginBase(ServiceBase):
    """ 插件基类: 提供插件所需要的公共接口与扩展点 """
    
    def __init__(self):
        super(PluginBase, self).__init__()
        self.logger = plugin_logger
