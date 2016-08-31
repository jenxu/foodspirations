# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import url_for

from . import app

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flask_login import UserMixin

class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    posts = relationship("Post", backref="author")

class Post(Base):
    __tablename__="posts"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    pic_filename = Column(String)
    ingredients = Column(String)
    steps = Column(String)
    ethnic_region = Column(String)
    likes = Column(Integer, default=0)
    
    comments = relationship("Comment", backref="post")

    author_id = Column(Integer, ForeignKey('users.id'))
    picturefile_id = Column(Integer, ForeignKey('picturefiles.id'), nullable=False)
    
class PictureFile(Base):
    __tablename__="picturefiles"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    
    post = relationship("Post", uselist=False, backref="picturefile")
    
    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.filename,
            "path": url_for("uploaded_file", filename=self.filename)
        }
        
class Comment(Base):
    __tablename__="comments"
    id = Column(Integer, primary_key=True)
    author = Column(String)
    content = Column(String)

    post_id = Column(Integer, ForeignKey('posts.id'))
    
class Like(Base):
    __tablename__="likes"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    user_id = Column(Integer)

Base.metadata.create_all(engine)
