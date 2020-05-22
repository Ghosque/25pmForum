# -*- coding:utf-8 -*-
import datetime

from src import db


class Base(object):
    # 创建时间
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    # 更新时间
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)


class User(db.Model, Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    avatar = db.Column(db.String(255), nullable=True)

    @classmethod
    def save_data(cls, data):
        user = cls.query.filter_by(username=data['username'], phone=data['phone']).first()

        if user:
            return None
        else:
            user = cls(username=data['username'], password=data['password'], phone=data['phone'])
            db.session.add(user)
            db.session.commit()
            return user

    @classmethod
    def verify_data(cls, data):
        user = cls.query.filter_by(username=data['username'], password=data['password']).first()

        return user


class PostType(db.Model, Base):
    __tablename__ = 'post_type'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False)


class Post(db.Model, Base):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)

    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('post_type.id'), nullable=False)

    # 给这个 post 模型添加一个 poster 属性（关系表），User为要连接的表，backref为定义反向引用
    poster = db.relationship('User', backref=db.backref('posts'), lazy='select')
    type = db.relationship('PostType', backref=db.backref('posts'), lazy='select')


class PostComment(db.Model, Base):
    __tablename__ = 'post_comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    isDelete = db.Column(db.Boolean, default=False, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    commenter = db.relationship('User', backref=db.backref('comments'), lazy='select')


class CommentReply(db.Model, Base):
    __tablename__ = 'comment_reply'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    reply_to_floor = db.Column(db.Boolean, nullable=False)  # 判断是直接评论还是楼中楼

    comment_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
