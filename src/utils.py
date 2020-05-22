# -*- coding:utf-8 -*-
import redis
from .settings import BaseConfig


class Redis(object):

    @staticmethod
    def get_cache():
        cache = redis.StrictRedis(BaseConfig.REDIS_HOST, BaseConfig.REDIS_PORT, BaseConfig.REDIS_DB, BaseConfig.REDIS_PASSWORD)
        return cache
