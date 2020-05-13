# -*- coding:utf-8 -*-
import os
from src import create_app


app = create_app(os.environ.get('FLASK_CONFIGS', 'default'))
app.run()
