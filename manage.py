# -*- coding:utf-8 -*-
import os
from flask_script import Manager
from src import create_app
from src.models import *


app = create_app(os.environ.get('FLASK_CONFIGS', 'default'))
manager = Manager(app)


@manager.command
def init_db():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    manager.run()
