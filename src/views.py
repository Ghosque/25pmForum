# -*- coding:utf-8 -*-
import hashlib
from flask import request, jsonify, make_response
from flask_restful import Resource
from .urls import api
from .utils import Redis
from .models import User

cache = Redis.get_cache()


@api.resource('/user/', '/user/<string:user_id>/')
class UserView(Resource):
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
        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data = dict(data)
        data['password'] = password

        user = User.save_data(data)
        print(user)

        return make_response(jsonify({'msg': '注册'}), 200)

    @staticmethod
    def handle_login(data):
        username = data['username']
        password = data['password']

        print(username, password)
        return make_response(jsonify({'msg': '登录'}), 200)
