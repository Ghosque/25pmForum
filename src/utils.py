# -*- coding:utf-8 -*-
import jwt
import redis
from functools import wraps
from datetime import datetime, timedelta
from flask import request

from .settings import BaseConfig
from .response import ResMsg
from .code import ResponseCode, ResponseMessage


class Redis(object):

    @staticmethod
    def get_cache():
        cache = redis.StrictRedis(BaseConfig.REDIS_HOST, BaseConfig.REDIS_PORT, BaseConfig.REDIS_DB, BaseConfig.REDIS_PASSWORD)
        return cache

    @classmethod
    def write(cls, key, value, expire=None):
        """
        写入键值对
        """
        # 判断是否有过期时间，没有就设置默认值
        if expire:
            expire_in_seconds = expire
        else:
            expire_in_seconds = BaseConfig.REDIS_DEFAULT_EXPIRE

        r = cls.get_cache()
        r.set(key, value, ex=expire_in_seconds)

    @classmethod
    def read(cls, key):
        """
        读取键值对内容
        """
        r = cls.get_cache()
        value = r.get(key)
        return value.decode('utf-8') if value else value

    @classmethod
    def hset(cls, name, key, value):
        """
        写入hash表
        """
        r = cls.get_cache()
        r.hset(name, key, value)

    @classmethod
    def hmset(cls, key, *value):
        """
        读取指定hash表的所有给定字段的值
        """
        r = cls.get_cache()
        value = r.hmset(key, *value)
        return value

    @classmethod
    def hget(cls, name, key):
        """
        读取指定hash表的键值
        """
        r = cls.get_cache()
        value = r.hget(name, key)
        return value.decode('utf-8') if value else value

    @classmethod
    def hgetall(cls, name):
        """
        获取指定hash表所有的值
        """
        r = cls.get_cache()
        return r.hgetall(name)

    @classmethod
    def delete(cls, *names):
        """
        删除一个或者多个
        """
        r = cls.get_cache()
        r.delete(*names)

    @classmethod
    def hdel(cls, name, key):
        """
        删除指定hash表的键值
        """
        r = cls.get_cache()
        r.hdel(name, key)

    @classmethod
    def expire(cls, name, expire=None):
        """
        设置过期时间
        """
        if expire:
            expire_in_seconds = expire
        else:
            expire_in_seconds = BaseConfig.REDIS_DEFAULT_EXPIRE
            r = cls.get_cache()
            r.expire(name, expire_in_seconds)


def auth_process(view_func):
    @wraps(view_func)
    def verify_token(*args, **kwargs):
        # 在请求头上拿到token
        token = request.headers.get('Authorization', None)
        if not token:
            return ResMsg(code=ResponseCode.TOKEN_ERR, msg=ResponseMessage.TOKEN_ERR).data

        try:
            payload = jwt.decode(token, key=BaseConfig.SECRET_KEY, algorithm='HS256')
        except jwt.exceptions.ExpiredSignatureError:  # token过期
            cache_token = Redis.read(BaseConfig.USER_CACHE_KEY_MODEL.format(request.base_url.rsplit('/', 2)[-2]))
            if cache_token and cache_token==token:
                new_token = create_token(request.base_url.rsplit('/', 2)[-2])
                print('new:', new_token)
                return view_func(*args, **kwargs, token=new_token)
            else:
                return ResMsg(code=ResponseCode.TOKEN_ERR, msg=ResponseMessage.TOKEN_ERR).data
        except jwt.exceptions.InvalidSignatureError:  # token无效
            return ResMsg(code=ResponseCode.TOKEN_ERR, msg=ResponseMessage.TOKEN_ERR).data
        else:
            return view_func(*args, **kwargs, token=token)

    return verify_token


def create_token(user_id):
    payload = {
        "user_id": user_id,
        'exp': datetime.utcnow() + timedelta(seconds=BaseConfig.TOKEN_EXPIRE)
    }
    token = jwt.encode(payload, key=BaseConfig.SECRET_KEY, algorithm='HS256').decode('ascii')
    Redis.write(BaseConfig.USER_CACHE_KEY_MODEL.format(user_id), token)

    return token
