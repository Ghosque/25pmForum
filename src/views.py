# -*- coding:utf-8 -*-
from flask import request, jsonify, make_response
from flask_restful import Resource
from .urls import api
from .utils import Redis

cache = Redis.get_cache()


@api.resource('/user/', '/user/<string:user_id>/')
class User(Resource):
    def get(self, user_id):
        return make_response(jsonify({'msg': 'select user - {}'.format(user_id)}), 200)

    def post(self):
        type = request.args.get('type')
        if type == 'register':
            self.handle_register(request.form)
        elif type == 'login':
            self.handle_login(request.form)
        else:
            return make_response(jsonify({'msg': '请求不是注册或登录'}), 404)

    @staticmethod
    def handle_register(data):
        pass

    @staticmethod
    def handle_login(data):
        pass
