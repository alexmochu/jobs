# api/letters/__init__.py

from flask import Blueprint

letters = Blueprint('letters', __name__)

from . import views