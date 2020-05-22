# -*- coding:utf-8 -*-
import jwt
import hashlib
from datetime import datetime, timedelta

from flask import request, jsonify, make_response
from flask_restful import Resource

from .urls import api
from .utils import Redis
from .models import User
from .settings import BaseConfig

cache = Redis.get_cache()


@api.resource('/user/', '/user/<string:user_id>/')
class UserView(Resource):
    USER_CACHE_KEY_MODEL = 'user:token:{}'

    def get(self, user_id):
        token = request.headers.get('Authorization', None)
        user = User.get_user(user_id)
        if user:
            print(user.username)
            print(user.posts)
        response = make_response(jsonify({'msg': 'select user - {}'.format(user_id)}), 200)
        return response

    def post(self):
        type = request.args.get('type')
        if type == 'register':
            self.handle_register(request.form)
        elif type == 'login':
            self.handle_login(request.form)
        else:
            res = {
                'code': 1,
                'msg': '请求不是注册或登录'
            }
            status = 404
            response = make_response(jsonify(res), status)
            return response

    @staticmethod
    def handle_register(data):
        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data = dict(data)
        data['password'] = password
        # 保存数据
        user = User.save_data(data)
        if user:
            res = {
                'code': 0,
                'msg': '注册成功'
            }
            status = 200
        else:
            res = {
                'code': 1,
                'msg': '该用户名或手机号已被注册'
            }
            status = 200

        response = make_response(jsonify(res), status)
        return response

    @classmethod
    def handle_login(cls, data):
        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data = dict(data)
        data['password'] = password
        # 检查数据
        user = User.verify_data(data)
        if user:
            # 保存JWT
            payload = {
                "user_id": user.id,
                'exp': datetime.utcnow()+timedelta(seconds=BaseConfig.REDIS_DEFAULT_EXPIRE)
            }
            token = jwt.encode(payload, key=BaseConfig.SECRET_KEY, algorithm='HS256').decode('ascii')
            cache.set(cls.USER_CACHE_KEY_MODEL.format(user.id), token)

            res = {
                'code': 0,
                'msg': '登录成功',
                'token': token
            }
            status = 200
        else:
            res = {
                'code': 1,
                'msg': '用户名或密码错误'
            }
            status = 200

        response = make_response(jsonify(res), status)
        return response
