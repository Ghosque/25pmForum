# -*- coding:utf-8 -*-
import hashlib

from flask import request
from flask_restful import Resource

from .urls import api
from .utils import Redis, create_token, auth_process, datetime_to_string
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


@api.resource('/posts/', '/posts/<string:id>/')
class PostView(Resource):

    def get(self, id=None):
        res = ResMsg()
        type = request.args.get('type')
        if type == 'single':
            post = Post.get_single_data(id)
            if not post:
                res.update(code=ResponseCode.NO_RESOURCE_FOUND, msg=ResponseMessage.NO_RESOURCE_FOUND)
            else:
                comments_data = PostComment.get_data(id)
                post.update({'commentsData': comments_data})
                res.update(data=post)
        elif type == 'user':
            posts = Post.get_single_user_all_data(id)
            res.update(data={'posts': posts})
        elif type == 'all':
            page = request.args.get('page', 1, int)
            type_id = request.args.get('typeId', None)
            if not type_id:
                res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

            posts = Post.get_all_data(page, type_id)

            res.update(data={'posts': posts})
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data

    @auth_process
    def post(self, id=None, token=None):
        """
        上传文章
        :return:
        """
        res = ResMsg()
        Post.save_data(request.form)

        if token:
            res.update(data={'token': token})

        return res.data

    def put(self):
        pass


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

    @auth_process
    def delete(self, id=None, token=None):
        res = ResMsg()
        type = request.args.get('type')
        comment_id = request.form['commentId']
        if type == 'comment':
            flag = PostComment.delete_data(comment_id, id)
            if not flag:
                res.update(code=ResponseCode.NO_RESOURCE_FOUND, msg=ResponseMessage.NO_RESOURCE_FOUND)
            else:
                if token:
                    res.update(data={'token': token})
        elif type == 'reply':
            flag = CommentReply.delete_data(comment_id, id)
            if not flag:
                res.update(code=ResponseCode.NO_RESOURCE_FOUND, msg=ResponseMessage.NO_RESOURCE_FOUND)
            else:
                if token:
                    res.update(data={'token': token})
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data


@api.resource('/userFollow/', '/userFollow/<string:user_id>/')
class UserFollowView(Resource):
    USER_FOLLOW_CACHE_KEY_MODEL = 'user:follow:{}'
    USER_FANS_CACHE_KEY_MODEL = 'user:fans:{}'
    @auth_process
    def get_follow_fans_list(self, id=None, token=None):
        res = ResMsg()
        follow_list = Redis.smembers(self.USER_FOLLOW_CACHE_KEY_MODEL.format(id))
        fans_list = Redis.smembers(self.USER_FANS_CACHE_KEY_MODEL.format(id))
        for index, follow_item in enumerate(follow_list):
            user = User.get_user(follow_item)
            follow_list[index] = {
                'id': user.id,
                'username': user.username
            }
        for index, fans_item in enumerate(fans_list):
            user = User.get_user(fans_item)
            fans_list[index] = {
                'id': user.id,
                'username': user.username
            }
        data = {
            'followList': follow_list,
            'fansList': fans_list
        }
        if token:
            data.update({'token': token})

        res.update(data=data)

        return res.data

    def get(self, user_id):
        res = ResMsg()
        type = request.args.get('type')
        if type == 'count':
            follow_num = Redis.scard(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id))
            fans_num = Redis.scard(self.USER_FANS_CACHE_KEY_MODEL.format(user_id))
            res.update(data={'followNum': follow_num, 'fansNum': fans_num})
        elif type == 'commonCount':
            common_list = Redis.sinter(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), self.USER_FOLLOW_CACHE_KEY_MODEL.format(request.form['otherId']))
            count = len(common_list)
            res.update(data={'commonCount': count})
        elif type == 'list':
            return self.get_follow_fans_list()
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data

    @auth_process
    def post(self, id=None, token=None):
        res = ResMsg()
        user_id = id
        type = request.args.get('type')
        if type == 'new':
            followed_user_id = request.form['followedId']
            Redis.sadd(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), followed_user_id)
            Redis.sadd(self.USER_FANS_CACHE_KEY_MODEL.format(followed_user_id), user_id)
        elif type == 'judge':
            other_user_id = request.form['otherId']
            flag = Redis.sismember(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), other_user_id) and Redis.sismember(self.USER_FANS_CACHE_KEY_MODEL.format(user_id), other_user_id)
            res.update(data={'flag': flag})
        else:
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        if token:
            res.update({'token': token})

        return res.data

    @auth_process
    def delete(self, id=None, token=None):
        res = ResMsg()
        user_id = id
        cancel_followed_user_id = request.form['cancelFollowedId']
        Redis.srem(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), cancel_followed_user_id)
        Redis.srem(self.USER_FANS_CACHE_KEY_MODEL.format(cancel_followed_user_id), user_id)

        if token:
            res.update({'token': token})

        return res.data


@api.resource('/postLike/', '/postLike/<string:post_id>/')
class PostLikeView(Resource):

    def get(self, article_id):
        pass

    def post(self):
        pass
