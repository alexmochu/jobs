# api/home/__init__.py

from flask import Blueprint

gpt = Blueprint('gpt', __name__)

from . import views