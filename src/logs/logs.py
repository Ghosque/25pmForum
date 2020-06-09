# -*- coding:utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from src.settings import config


def setup_log(config_name):
    """

    :param config_name: 传入日志等级
    :return:
    """
    # 设置日志的的登记
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    # 创建日志记录器，设置日志的保存路径和每个日志的大小和日志的总大小
    file_log_handler = RotatingFileHandler("./src/logs/log", maxBytes=1024*1024*100,backupCount=100)
    # 创建日志记录格式，日志等级，输出日志的文件名 行数 日志信息
    formatter = logging.Formatter("%(asctime)s [%(threadName)s:%(thread)d] [%(pathname)s:%(lineno)d] [%(funcName)s] [%(levelname)s] - %(message)s")
    # 为日志记录器设置记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flaks app使用的）加载日志记录器
    logging.getLogger().addHandler(file_log_handler)
