import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.contrib.linkedin import linkedin, make_linkedin_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
# from flask_dance.consumer.backend.sqla import (OAuthConsumerMixin,
#                                                SQLAlchemyBackend)

from .. import db
from ..models import OAuth, User

github_blueprint = make_github_blueprint(
    client_id=os.getenv("GITHUB_ID"),
    client_secret=os.getenv("GITHUB_SECRET"),
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)

google_blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=['https://www.googleapis.com/auth/userinfo.email',
           'https://www.googleapis.com/auth/userinfo.profile'],
    offline=True,
    reprompt_consent=True,
    # backend=SQLAlchemyBackend(OAuth, db.session, user=current_user)
)

# linkedin_blueprint = make_linkedin_blueprint(
#     client_id=os.getenv("LINKEDIN_CLIENT_ID"),
#     client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
#     scope=["r_liteprofile"],
#     # redirect_url="http://127.0.0.1:5000"
# )

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    info = github.get("/user")
    if info.ok:
        account_info = info.json()
        username = account_info["login"]

        query = User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        
