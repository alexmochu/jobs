# api/__init__.py

import os
# third-party imports
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import login_required, logout_user
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin

# local imports
from instance.config import app_config

# db variable initialization
db = SQLAlchemy()

from .models import login_manager

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # Reverse the following 2 lines in production
    # app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    app.secret_key = "supersecretkey"

    db.init_app(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    migrate = Migrate(app, db)

    CORS(app)

    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
    
    from .auth.views import github_blueprint, google_blueprint, linkedin_blueprint    
    app.register_blueprint(github_blueprint, url_prefix="/login")
    app.register_blueprint(google_blueprint, url_prefix="/login")
    app.register_blueprint(linkedin_blueprint, url_prefix="/login")

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .jobs import jobs as jobs_blueprint
    app.register_blueprint(jobs_blueprint)

    @app.errorhandler(403)
    def forbidden(error):
        response = {"message" : "You do not have sufficient permissions to access this route."}
        return make_response(jsonify(response)), 403

    @app.errorhandler(404)
    def page_not_found(error):
        response = {"message" : "What you're looking for doesn't exist."}
        return make_response(jsonify(response)), 404

    @app.errorhandler(405)
    def page_not_found(error):
        response = {"message" : "Request method is not allowed please recheck and try again"}
        return make_response(jsonify(response)), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        response = {"message" : "The server encountered an internal error. That's all we know."}
        return make_response(jsonify(response)), 500

    return app