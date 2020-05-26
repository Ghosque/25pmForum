# -*- coding:utf-8 -*-
import hashlib

from flask import request
from flask_restful import Resource

from .urls import api
from .utils import create_token, auth_process, datetime_to_string
from .models import User, PostParentType, PostChildType, Post, PostComment, CommentReply
from .code import ResponseCode, ResponseMessage
from .response import ResMsg


@api.resource('/user/', '/user/<string:user_id>/')
class UserView(Resource):
    USER_CACHE_KEY_MODEL = 'user:token:{}'

    @auth_process
    def get(self, user_id, id=None, token=None):
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
            return self.handle_register(request.form, res)
        elif type == 'login':
            return self.handle_login(request.form, res)
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
        print(password)
        data = dict(data)
        data['password'] = password
        # 检查数据
        user = User.verify_data(data)
        if user:
            # 保存JWT
            token = create_token(user.id)
            print(token)

            res.update(data={'token': token})
        else:
            res.update(code=ResponseCode.ACCOUNT_OR_PASS_WORD_ERR, msg=ResponseMessage.ACCOUNT_OR_PASS_WORD_ERR)

        return res.data


@api.resource('/postType/')
class PostTypeView(Resource):

    def post(self):
        """
        添加新的文章类型
        :return:
        """
        res = ResMsg()
        data = request.form
        if not int(data['isChild']):
            PostParentType.save_data(data)
        else:
            PostChildType.save_data(data)

        return res.data


@api.resource('/posts/', '/post/<string:id>/')
class PostView(Resource):

    def get(self, id):
        res = ResMsg()
        type = request.args.get('type')
        if type == 'single':
            post = Post.get_single_data(id)
            data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'type': post.type.type_name,
                'ct': datetime_to_string(post.create_time),
                'ut': datetime_to_string(post.update_time)
            }
            res.update(data=data)
        elif type == 'all':
            posts = Post.get_all_data(id)
            data = list()
            for post in posts:
                data.append({
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'author': post.author.username,
                    'type': post.type.type_name,
                    'ct': datetime_to_string(post.create_time),
                    'ut': datetime_to_string(post.update_time)
                })
            res.update(data=data)
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data

    def post(self):
        """
        上传文章
        :return:
        """
        res = ResMsg()
        Post.save_data(request.form)

        return res.data


@api.resource('/comments/', '/comments/<string:id>/')
class CommentView(Resource):

    def get(self, id):
        @auth_process
        def get_user_comment():
            pass

        res = ResMsg()
        type = request.args.get('type')
        if type == 'post':
            comments_data = PostComment.get_data(id)
            res.update(data=comments_data)
        elif type == 'user':
            pass
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data

    @auth_process
    def post(self, id=None, token=None):
        """
        发表评论或楼中楼回复
        :return:
        """
        res = ResMsg()
        type = request.args.get('type')
        if type == 'comment':
            PostComment.save_data(request.form)
        elif type == 'reply':
            CommentReply.save_data(request.form)
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        if token:
            res.update({'token': token})

        return res.data
