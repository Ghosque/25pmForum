# -*- coding:utf-8 -*-
import hashlib
import logging

from flask import request
from flask_restful import Resource

from src import cache
from .urls import api
from .utils import Redis, create_token, auth_process
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
        logging.debug("用户id=【{}】 请求获取个人数据".format(user_id))
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
            logging.debug("User.post接口请求失败，参数type={}不存在".format(type))
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
            logging.debug("新用户注册失败，用户名：{}，密码：{}，绑定手机：{}".format(data['username'], data['password'], data['phone']))
        logging.debug("新用户 {} 注册成功".format(data['username']))

        return res.data

    @classmethod
    def handle_login(cls, data, res):
        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        data = dict(data)
        data['password'] = password
        logging.info("用户 {} 登录".format(data['username']))
        # 检查数据
        user = User.verify_data(data)
        if user:
            # 保存JWT
            token = create_token(user.id)

            res.update(data={'token': token})
        else:
            logging.debug("账号或密码错误")
            res.update(code=ResponseCode.ACCOUNT_OR_PASS_WORD_ERR, msg=ResponseMessage.ACCOUNT_OR_PASS_WORD_ERR)

        return res.data


@api.resource('/postType/')
class PostTypeView(Resource):

    def post(self):
        """
        添加新的帖子类型
        :return:
        """
        res = ResMsg()
        data = request.form
        if not int(data['isChild']):
            PostParentType.save_data(data)
            logging.info('新增一类帖子类型：【{}】'.format(data['typeName']))
        else:
            PostChildType.save_data(data)
            logging.info('新增二类帖子类型：【{}】'.format(data['typeName']))

        return res.data


@api.resource('/posts/', '/posts/<string:id>/')
class PostView(Resource):

    @cache.cached()
    def get(self, id=None):
        res = ResMsg()
        type = request.args.get('type')
        if type == 'single':
            logging.info('获取帖子id=【{}】的详细内容'.format(id))
            post = Post.get_single_data(id)
            if not post:
                res.update(code=ResponseCode.NO_RESOURCE_FOUND, msg=ResponseMessage.NO_RESOURCE_FOUND)
            else:
                comments_data = PostComment.get_data(id)
                post.update({'commentsData': comments_data})
                res.update(data=post)
        elif type == 'user':
            logging.info('获取用户id=【{}】的全部帖子'.format(id))
            posts = Post.get_single_user_all_data(id)
            res.update(data={'posts': posts})
        elif type == 'all':
            logging.info('获取所有帖子')
            page = request.args.get('page', 1, int)
            type_id = request.args.get('typeId', None)
            if not type_id:
                res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

            posts = Post.get_all_data(page, type_id)

            res.update(data={'posts': posts})
        else:
            logging.debug('Post.post接口请求失败，参数type={}不存在'.format(type))
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data

    @auth_process
    def post(self, id=None, token=None):
        """
        新增帖子
        :return:
        """
        res = ResMsg()
        Post.save_data(request.form)

        if token:
            res.update(data={'token': token})

        logging.info('新增帖子，类型：【{}】，用户id：【{}】'.format(request.form['typeId'], request.form['userId']))

        return res.data

    def put(self):
        pass


@api.resource('/comments/', '/comments/<string:id>/')
class CommentView(Resource):

    def get(self, id):
        @auth_process
        def get_user_comment(id=None, token=None):
            comments = PostComment.get_user_data(id)
            replies = CommentReply.get_user_data(id)
            user_comments = sorted(comments+replies, key=lambda x:x['ct'], reverse=True)

            return user_comments, token

        res = ResMsg()
        type = request.args.get('type')
        if type == 'post':
            logging.info('获取帖子id=【{}】的所有评论'.format(id))
            comments_data = PostComment.get_data(id)
            data = {'commentsData': comments_data}
            res.update(data=data)
        elif type == 'user':
            logging.info('获取用户id=【{}】的所有评论'.format(id))
            comments_data, token = get_user_comment()
            data = {'commentsData': comments_data}
            if token:
                data.update({'token': token})
            res.update(data=data)
        else:
            logging.debug('Comment.get接口请求失败，参数type={}不存在'.format(type))
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
        logging.info('用户id=【{}】在帖子id=【{}】发表评论，类型为【{}】'.format(request.form['userId'], request.form['postId'], type))
        if type == 'comment':
            PostComment.save_data(request.form)
        elif type == 'reply':
            CommentReply.save_data(request.form)
        else:
            logging.debug('Comment.post接口请求失败，参数type={}不存在'.format(type))
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        if token:
            res.update({'token': token})

        return res.data

    @auth_process
    def delete(self, id=None, token=None):
        res = ResMsg()
        type = request.args.get('type')
        comment_id = request.form['commentId']
        logging.info('用户id=【{}】在帖子id=【{}】删除评论，评论id=【{}】，类型为【{}】'.format(request.form['userId'], request.form['postId'], comment_id, type))
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
            logging.debug('Comment.delete接口请求失败，参数type={}不存在'.format(type))
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data


@api.resource('/userFollow/', '/userFollow/<string:user_id>/')
class UserFollowView(Resource):
    USER_FOLLOW_CACHE_KEY_MODEL = 'user:follow:{}'
    USER_FANS_CACHE_KEY_MODEL = 'user:fans:{}'
    @auth_process
    def get_follow_fans_list(self, id=None, token=None):
        logging.info('用户id=【{}】获取关注、粉丝列表'.format(id))
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
            logging.info('获取用户id=【{}】关注数和粉丝数'.format(user_id))
            follow_num = Redis.scard(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id))
            fans_num = Redis.scard(self.USER_FANS_CACHE_KEY_MODEL.format(user_id))
            res.update(data={'followNum': follow_num, 'fansNum': fans_num})
        elif type == 'commonCount':
            logging.info('用户id=【{}】获取与另一用户id=【{}】的共同关注数'.format(user_id, request.form['otherId']))
            common_list = Redis.sinter(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), self.USER_FOLLOW_CACHE_KEY_MODEL.format(request.form['otherId']))
            count = len(common_list)
            res.update(data={'commonCount': count})
        elif type == 'list':
            return self.get_follow_fans_list()
        else:
            logging.debug('UserFollow.get接口请求失败，参数type={}不存在'.format(type))
            res.update(code=ResponseCode.INVALID_PARAMETER, msg=ResponseMessage.INVALID_PARAMETER)

        return res.data

    @auth_process
    def post(self, id=None, token=None):
        res = ResMsg()
        user_id = id
        type = request.args.get('type')
        if type == 'new':
            followed_user_id = request.form['followedId']
            logging.info('用户id=【{}】关注用户id=【{}】'.format(user_id, followed_user_id))
            Redis.sadd(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), followed_user_id)
            Redis.sadd(self.USER_FANS_CACHE_KEY_MODEL.format(followed_user_id), user_id)
        elif type == 'judge':
            other_user_id = request.form['otherId']
            logging.info('判断用户id=【{}】和id=【{}】是否互相关注'.format(user_id, other_user_id))
            flag = Redis.sismember(self.USER_FOLLOW_CACHE_KEY_MODEL.format(user_id), other_user_id) and Redis.sismember(self.USER_FANS_CACHE_KEY_MODEL.format(user_id), other_user_id)
            res.update(data={'flag': flag})
        else:
            logging.debug('UserFollow.post接口请求失败，参数type={}不存在'.format(type))
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
        logging.info('用户id=【{}】取消关注用户id=【{}】'.format(user_id, cancel_followed_user_id))

        if token:
            res.update({'token': token})

        return res.data
