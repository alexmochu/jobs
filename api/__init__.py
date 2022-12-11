# api/__init__.py

# third-party imports
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

# local imports
from config import app_config



def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # Reverse line 19 and 20 in production
    # app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    CORS(app)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)


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