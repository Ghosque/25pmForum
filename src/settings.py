# -*- coding:utf-8 -*-
import os


class BaseConfig:
    SECRET_KEY = 'ashdo*i$hsf819y@3hr893h43'
    # MySQL
    HOST = 'localhost'
    PORT = '3306'
    DATABASE = 'forum'
    USERNAME = 'root'
    PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME, password=PASSWORD, host=HOST, port=PORT, db=DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Redis
    REDIS_HOST = 'localhost'
    REDIS_PORT = '6379'
    REDIS_DB = '6'
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_DEFAULT_EXPIRE = 7 * 24 * 60 * 60
    # token
    TOKEN_EXPIRE = 2 * 60 * 60
    USER_CACHE_KEY_MODEL = 'user:token:{}'
    # 每次获取N个帖子
    POST_PER_NUM = 50


class DevelopConfig(BaseConfig):
    DEBUG = True


class TestConfig(BaseConfig):
    TESTING = True


class ProductConfig(BaseConfig):
    pass


config = {
    'development': DevelopConfig,
    'testing': TestConfig,
    'production': ProductConfig,
    'default': DevelopConfig
}
