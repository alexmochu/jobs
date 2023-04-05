# api/__init__.py

import os
# third-party imports
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
from flask_login import login_required, logout_user
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin
from flask_mail import Mail

# local imports
# from instance.config import app_config

# production
from config import app_config

# db variable initialization
db = SQLAlchemy()

from .models import login_manager

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    mail = Mail(app)
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    # Reverse the following 2 lines in production
    # app.config.from_object(app_config[config_name])
    app.config.from_object(app_config[config_name])

    app.secret_key = os.getenv("SECRET")

    db.init_app(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_DEFAULT_SENDER')
    app.config['MAIL_PASSWORD'] = 'your-email-password'
    migrate = Migrate(app, db)
    
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
    CORS(app, resources={r'/*': {'origins': '*'}})    
    app.config['CORS_HEADERS'] = 'Content-Type'
   
    from .auth.views import github_blueprint, google_blueprint, linkedin_blueprint    
    app.register_blueprint(github_blueprint, url_prefix="/login")
    app.register_blueprint(google_blueprint, url_prefix="/login")
    app.register_blueprint(linkedin_blueprint, url_prefix="/login")

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .jobs import jobs as jobs_blueprint
    app.register_blueprint(jobs_blueprint)
    
    from .gpt import gpt as gpt_blueprint
    app.register_blueprint(gpt_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    @app.errorhandler(403)
    def forbidden(error):
        response = {"message" : "You do not have sufficient permissions to access this route."}
        return make_response(jsonify(response)), 403

    @app.errorhandler(404)
    def page_not_found(error):
        response = {"message" : "What you're looking for doesn't exist."}
        return make_response(jsonify(response)), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        response = {"message" : "Request method is not allowed please recheck and try again"}
        return make_response(jsonify(response)), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        response = {"message" : "The server encountered an internal error. That's all we know."}
        return make_response(jsonify(response)), 500

    return app