# -*- coding:utf-8 -*-
import datetime
from src import db


class Base(object):
    # 创建时间
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    # 更新时间
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class User(db.Model, Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20), unique=True)
    avatar = db.Column(db.String(255), nullable=True)


class Post(db.Model, Base):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 给这个 post 模型添加一个author属性（关系表），User为要连接的表，backref为定义反向引用
    poster = db.relationship('User', backref=db.backref('posts'), lazy='dynamic')  # lazy表示禁止自动查询
