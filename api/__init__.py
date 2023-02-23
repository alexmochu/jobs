# api/__init__.py

import os
# third-party imports
from flask import Flask, jsonify, request, make_response, redirect, url_for
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
from .auth.views import github_blueprint, google_blueprint
# google_blueprint, linkedin_blueprint

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # Reverse line 19 and 20 in production
    app.config.from_object(app_config[config_name])
    # app.config.from_pyfile('config.py')

    app.secret_key = "supersecretkey"

    db.init_app(app)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    migrate = Migrate(app, db)
    
    # blueprint = make_github_blueprint()
    app.register_blueprint(github_blueprint, url_prefix="/login")
    app.register_blueprint(google_blueprint, url_prefix="/login")
    # app.register_blueprint(linkedin_blueprint)

    CORS(app)

    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        
    
    def preferred_locale_value(multi_locale_string):
        """
        Extract the value of the preferred locale from a MultiLocaleString
        https://docs.microsoft.com/en-us/linkedin/shared/references/v2/object-types#multilocalestring
        """
        preferred = multi_locale_string["preferredLocale"]
        locale = "{language}_{country}".format(
            language=preferred["language"], country=preferred["country"]
        )
        return multi_locale_string["localized"][locale]


    @app.route("/github")
    def github_login():
        if not github.authorized:
            return redirect(url_for("github.login"))
        res = github.get("/user")
        username = res.json()["login"]
        return f"You are @{username} on GitHub"
    
    @app.route('/google')
    def google_login():
        if not google.authorized:
            return redirect(url_for("google.login"))
        resp = google.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        return "You are {email} on Google".format(email=resp.json()["email"])
    
    # @app.route('/linkedin')
    # def linkedin_login():
    #     if not linkedin.authorized:
    #         return redirect(url_for("linkedin.login"))
    #     resp = linkedin.get("me")
    #     assert resp.ok, resp.text
    #     data = resp.json()
    #     name = "{first} {last}".format(
    #         first=preferred_locale_value(data["firstName"]),
    #         last=preferred_locale_value(data["lastName"]),
    #     )
    #     return "You are {name} on LinkedIn".format(name=name)

    
    @app.route("/logout")
    @login_required
    def logout():
        token = github_blueprint.token['access_token']
        resp = github.post(
            'https://api.github.com/applications/' + os.getenv('GITHUB_ID') + '/token',
            params={"token": token},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # assert resp.ok, resp.text
        logout_user()
        # del github_blueprint.token
        return f"You logged out successfully"
    
    @app.route("/locked")
    @login_required
    def locked():
        return f"Locked"

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