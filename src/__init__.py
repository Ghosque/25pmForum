# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from werkzeug.utils import import_string

from .settings import config
from .core import JSONEncoder
from .logs.logs import setup_log

db = SQLAlchemy()
cache = Cache()
blueprints = ['src.urls:api_bp']


def create_app(config_name):
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.json_encoder = JSONEncoder  # 设置返回值编码格式
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)

    db.app = app
    db.init_app(app)

    cache.app = app
    cache.init_app(app)

    return app
