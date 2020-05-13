# -*- coding:utf-8 -*-
import os


class BaseConfig:
    # MySQL
    HOST = '47.107.183.166'
    PORT = '3306'
    DATABASE = 'forum'
    USERNAME = 'root'
    PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME, password=PASSWORD, host=HOST, port=PORT, db=DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Redis


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
