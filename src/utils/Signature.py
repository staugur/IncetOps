# -*- coding: utf-8 -*-
"""
    IncetOps.utils.Signature
    ~~~~~~~~~~~~~~

    Api签名认证

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from config import SYSTEM
from .tool import logger, md5, get_current_timestamp
from functools import wraps
from flask import request, jsonify


class Signature(object):
    """ 接口签名认证 """

    def __init__(self):
        self._version = SYSTEM["Sign"]["version"]
        self._accessKeys = [
            {"accesskey_id": SYSTEM["Sign"]["accesskey_id"], "accesskey_secret": SYSTEM["Sign"]["accesskey_secret"]}
        ]
        # 时间戳有效时长，单位秒
        self._timestamp_expiration = 30

    def get_signer_name(self):
        """获取签名算法"""
        return "MD5"

    def get_singer_version(self):
        """获取签名版本"""
        return self._version

    def _check_req_timestamp(self, req_timestamp):
        """ 校验时间戳
        @pram req_timestamp str,int: 请求参数中的时间戳(10位)
        """
        if len(str(req_timestamp)) == 10:
            req_timestamp = int(req_timestamp)
            now_timestamp = get_current_timestamp()
            #logger.debug("req_timestamp: {}, now_timestamp: {}, req_timestamp <= now_timestamp: {}, 30s: {}".format(req_timestamp, now_timestamp, req_timestamp <= now_timestamp, req_timestamp + self._timestamp_expiration >= now_timestamp))
            if req_timestamp <= now_timestamp and req_timestamp + self._timestamp_expiration >= now_timestamp:
                return True
        return False

    def _check_req_accesskey_id(self, req_accesskey_id):
        """ 校验accesskey_id
        @pram req_accesskey_id str: 请求参数中的用户标识id
        """
        if req_accesskey_id in [i['accesskey_id'] for i in self._accessKeys if "accesskey_id" in i]:
            return True
        return False

    def _get_accesskey_secret(self, accesskey_id):
        """ 根据accesskey_id获取对应的accesskey_secret
        @pram accesskey_id str: 用户标识id
        """
        return [i['accesskey_secret'] for i in self._accessKeys if i.get('accesskey_id') == accesskey_id][0]

    def _sign(self, parameters):
        """ MD5签名
        @param parameters dict: 除signature外请求的所有查询参数(公共参数和私有参数)
        """
        if "signature" in parameters:
            parameters.pop("signature")
        accesskey_id = parameters["accesskey_id"]
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
        canonicalizedQueryString = ''
        for (k, v) in sortedParameters:
            canonicalizedQueryString += k + "=" + v + "&"
        canonicalizedQueryString += self._get_accesskey_secret(accesskey_id)
        signature = md5(canonicalizedQueryString).upper()
        return signature

    def _verification(self, req_params):
        """ 校验请求是否有效
        @param req_params dict: 请求的所有查询参数(公共参数和私有参数)
        """
        res = dict(msg=None, success=False)
        try:
            req_version = req_params["version"]
            req_timestamp = req_params["timestamp"]
            req_accesskey_id = req_params["accesskey_id"]
            req_signature = req_params["signature"]
        except KeyError, e:
            logger.error(e, exc_info=True)
            res.update(msg="Invalid public params")
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="Unknown server error")
        else:
            # NO.1 校验版本
            if req_version == self._version:
                # NO.2 校验时间戳
                if self._check_req_timestamp(req_timestamp):
                    # NO.3 校验accesskey_id
                    if self._check_req_accesskey_id(req_accesskey_id):
                        # NO.4 校验签名
                        if req_signature == self._sign(req_params):
                            res.update(msg="Verification pass", success=True)
                        else:
                            res.update(msg="Invalid query string")
                    else:
                        res.update(msg="Invalid accesskey_id")
                else:
                    res.update(msg="Invalid timestamp")
            else:
                res.update(msg="Invalid version")
        logger.debug(res)
        return res

    def signature_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            params = request.args.to_dict()
            res = self._verification(params)
            if res["success"] is True:
                return f(*args, **kwargs)
            else:
                return jsonify(res)
        return decorated_function
