# -*- coding: utf-8 -*-
import os

from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
config_path = os.environ.get("CONFIG_PATH", "foodspirations.config.DevelopmentConfig")
app.config.from_object(config_path)

from . import views
from . import filters
from . import login