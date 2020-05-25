# -*- coding:utf-8 -*-
import hashlib

from flask import request
from flask_restful import Resource

from .urls import api
from .utils import create_token, auth_process
from .models import User, ArticleParentType, ArticleChildType
from .code import ResponseCode, ResponseMessage
from .response import ResMsg


@api.resource('/user/', '/user/<string:user_id>/')
class UserView(Resource):
    USER_CACHE_KEY_MODEL = 'user:token:{}'

    @auth_process
    def get(self, user_id, token=None):
        """
        获取个人信息
        :param user_id:
        :param token:
        :return:
        """
        res = ResMsg()
        user = User.get_user(user_id)
        if user:
            data = {
                'id': user.id,
                'username': user.username,
                'password': user.password,
                'phone': user.phone,
                'avatar': user.avatar,
                'token': token
            }
            res.update(data=data)

        return res.data

    def post(self):
        """
        注册与登录接口
        :return:
        """
        type = request.args.get('type')
        res = ResMsg()
        if type == 'register':
            self.handle_register(request.form, res)
        elif type == 'login':
            self.handle_login(request.form, res)
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseCode.INVALID_PARAMETER)
            return res.data

    @staticmethod
    def handle_register(data, res):
        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data = dict(data)
        data['password'] = password
        # 保存数据
        user = User.save_data(data)
        if not user:
            res.update(code=ResponseCode.FAIL, msg=ResponseMessage.FAIL)

        return res.data

    @classmethod
    def handle_login(cls, data, res):
        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data = dict(data)
        data['password'] = password
        # 检查数据
        user = User.verify_data(data)
        if user:
            # 保存JWT
            token = create_token(user.id)

            res.update(data={'token': token})
        else:
            res.update(code=ResponseCode.ACCOUNT_OR_PASS_WORD_ERR, msg=ResponseMessage.ACCOUNT_OR_PASS_WORD_ERR)

        return res.data


@api.resource('/postType/')
class ArticleTypeView(Resource):

    def post(self):
        """
        添加新的文章类型
        :return:
        """
        res = ResMsg()
        data = request.form
        print(data['isChild'], type(data['isChild']))
        if not int(data['isChild']):
            ArticleParentType.save_data(data)
        else:
            ArticleChildType.save_data(data)

        return res.data


@api.resource('/post/', '/post/<string:post_id>/')
class ArticleView(Resource):

    def get(self, post_id):
        pass

    def post(self):
        """
        上传文章
        :return:
        """
        data = request.form

    def put(self):
        pass
