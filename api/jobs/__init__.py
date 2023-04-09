# api/jobs/__init__.py

from flask import Blueprint

jobs = Blueprint('jobs', __name__)

from . import views