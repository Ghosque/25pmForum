# -*- coding:utf-8 -*-
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string

from .settings import config

# db = SQLAlchemy()
blueprints = ['src.urls:api_bp']


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)
    # db.init_app(app)

    return app
