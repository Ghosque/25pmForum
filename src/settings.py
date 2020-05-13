# -*- coding:utf-8 -*-
import os


class BaseConfig:
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
    REDIS_DEFAULT_EXPIRE = 100 * 365 * 24 * 60 * 60


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
