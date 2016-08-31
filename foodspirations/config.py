# -*- coding: utf-8 -*-
import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/foodspirations"
    DEBUG = True
    SECRET_KEY = os.environ.get("FOODSPIRATIONS_SECRET_KEY", os.urandom(12))
    UPLOAD_FOLDER = "uploads"

    
class TestingConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/blogful-test"
    DEBUG = False
    SECRET_KEY = "Not secret"
    UPLOAD_FOLDER = "test-uploads"
