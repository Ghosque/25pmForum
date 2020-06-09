# -*- coding:utf-8 -*-
import os
import logging


class BaseConfig:
    SECRET_KEY = 'ashdo*i$hsf819y@3hr893h43'
    # MySQL
    HOST = 'localhost'
    PORT = '3366'
    DATABASE = 'forum'
    USERNAME = 'root'
    PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME, password=PASSWORD, host=HOST, port=PORT, db=DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Redis
    REDIS_HOST = 'localhost'
    REDIS_PORT = '6699'
    REDIS_DB = '6'
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_DEFAULT_EXPIRE = 7 * 24 * 60 * 60
    # Token
    TOKEN_EXPIRE = 2 * 60 * 60
    USER_CACHE_KEY_MODEL = 'user:token:{}'
    # 每次获取N个帖子
    POST_PER_NUM = 50
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    # Log
    LOG_LEVEL = logging.DEBUG


class DevelopConfig(BaseConfig):
    DEBUG = True


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class ProductConfig(BaseConfig):
    DEBUG = False
    LOG_LEVEL = logging.WARNING


config = {
    'development': DevelopConfig,
    'testing': TestConfig,
    'production': ProductConfig,
    'default': DevelopConfig
}
