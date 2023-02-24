import os

from flask import Flask, jsonify, request, make_response, redirect, url_for
from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.contrib.linkedin import linkedin, make_linkedin_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import login_required, logout_user
from sqlalchemy.orm.exc import NoResultFound

from . import auth
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

linkedin_blueprint = make_linkedin_blueprint(
    client_id=os.getenv("LINKEDIN_CLIENT_ID"),
    client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
    scope=["openid", "profile", "email"],
)
   
# def preferred_locale_value(multi_locale_string):
#     """
#     Extract the value of the preferred locale from a MultiLocaleString
#     https://docs.microsoft.com/en-us/linkedin/shared/references/v2/object-types#multilocalestring
#     """
#     preferred = multi_locale_string["locale"]
#     locale = "{language}_{country}".format(
#         language=preferred["language"], country=preferred["country"]
#     )
#     return multi_locale_string["localized"][locale]

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    info = github.get("/user")
    if info.ok:
        account_info = info.json()
        email = account_info["email"]

        query = User.query.filter_by(email=email)
        try:
            user = query.one()
        except NoResultFound:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        
@auth.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    res = github.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on GitHub"
    
@auth.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])
    
@auth.route('/linkedin')
def linkedin_login():
    if not linkedin.authorized:
        return redirect(url_for("linkedin.login"))
    resp = linkedin.get("userinfo")
    assert resp.ok
    data = resp.json()
    name = "{first} {last}".format(
        first=data["given_name"],
        last=data["family_name"]
    )
    return "You are {name} on LinkedIn".format(name=name)

    
@auth.route("/logout")
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
        
@auth.route("/locked")
@login_required
def locked():
    return f"Locked"