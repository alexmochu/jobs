# api/resumes/__init__.py

from flask import Blueprint

resumes = Blueprint('resumes', __name__)

from . import views