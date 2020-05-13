# -*- coding:utf-8 -*-
from flask_restful import Resource
from .urls import api


@api.resource('/')
class User(Resource):
    def get(self):
        return 'user'
