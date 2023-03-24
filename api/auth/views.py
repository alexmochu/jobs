import os
import jwt
import datetime

from flask import Flask, jsonify, request, make_response, redirect, url_for, current_app
from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.contrib.linkedin import linkedin, make_linkedin_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import login_required, logout_user
from sqlalchemy.orm.exc import NoResultFound
from flask_cors import cross_origin
from functools import wraps

from . import auth
from .. import db
from ..models import OAuth, User, BlacklistToken

github_blueprint = make_github_blueprint(
    client_id=os.getenv("GITHUB_ID"),
    client_secret=os.getenv("GITHUB_SECRET"),
    redirect_to="http://localhost:5173/login/github/authorized",
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
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
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
    if not token:
        return False
    info = github.get("/user")
    if info.ok:
        data = info.json()
        email = data["email"] or f'{data["Login"]}@github.com'
        username = data["login"]

        query = User.query.filter_by(email=email)
        try:
            user = query.one()
        except NoResultFound:
            user = User(email=email, username=username, password_hash=None)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        
@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        return False
    info = google.get("/oauth2/v2/userinfo")
    if info.ok:
        account_info = info.json()
        email = account_info["email"]
        username = account_info["username"]

        query = User.query.filter_by(email=email)
        try:
            user = query.one()
        except NoResultFound:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        
@oauth_authorized.connect_via(linkedin_blueprint)
def linkedin_logged_in(blueprint, token):
    info = linkedin.get("userinfo")
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
        
# authorize and authenticate with jwt token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        access_token = request.headers['header-access-token']
        blacklisted = BlacklistToken.query.filter_by(token=access_token).first()

        if blacklisted:
            response = {"message": "Logged out. Please login again!" }
            return make_response(jsonify(response)), 401

        if 'header-access-token' in request.headers:
            token = request.headers['header-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'})

        try:
            data = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=["HS256"])
            current_user_data = User.query.filter_by(username=data['username']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired, log in again'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token. Please log in again.'}), 403
        return f(current_user_data, data, *args, **kwargs)

    return decorated
 
# @auth.route("/github")
# def github_login():
#     if not github.authorized:
#         return redirect(url_for("github.login"))
#     res = github.get("/user")
#     username = res.json()["login"]
#     return f"You are @{username} on GitHub"

@auth.route('/github')
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    
    resp = github.get('/user')
    if resp.ok:
        data = resp.json()
        email = data['email'] or f'{data["login"]}@github.com'
        username = data['login']
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user if not exists
            new_user = User(email=email, username=username, password_hash=None)
            db.session.add(new_user)
            db.session.commit()
            user = new_user
        login_user(user)
        token = user.get_token()
        return redirect(f'{request.host_url}app?token={token.decode("utf-8")}')
    else:
        return jsonify(message='Failed to retrieve user info from GitHub'), 400
    
@auth.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        data = resp.json()
        email = data['email']
        username = data['name']
        
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user if not exists
            new_user = User(email=email, username=username, password_hash=None)
            db.session.add(new_user)
            db.session.commit()
            user = new_user

        # Login user and return JWT token
        login_user(user)
        token = user.get_token()

        return redirect(f'{request.host_url}app?token={token.decode("utf-8")}')
    else:
        return jsonify(message='Failed to retrieve user info from Google'), 400
    return "You are {email} on Google".format(email=resp.json()["email"])

@auth.route('/google/signup', methods=['POST'])
def google_signup():
    data = request.json
    email = data['email']
    username = data['username']
    password = data['password']

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify(message='User already exists'), 400

    # Create new user
    new_user = User(email=email, username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # Login user and return JWT token
    login_user(new_user)
    token = new_user.get_token()

    return jsonify(token=token.decode('utf-8')), 201
 
# @auth.route('/linkedin')
# def linkedin_login():
#     if not linkedin.authorized:
#         return redirect(url_for("linkedin.login"))
#     resp = linkedin.get("userinfo")
#     assert resp.ok
#     data = resp.json()
#     name = "{first} {last}".format(
#         first=data["given_name"],
#         last=data["family_name"]
#     )
#     return "You are {name} on LinkedIn".format(name=name)

    
# @auth.route("/logout")
# @login_required
# def logout():
#     if google.authorized:
#         token = google_blueprint.token['access_token']
        
#         resp = google.post("https://accounts.google.com/o/oauth2/revoke?token="+token,
#             headers={"Content-Type": "application/x-www-form-urlencoded"}
#             )
#         logout_user()
#         return f"You logged out successfully"
    
#     token = github_blueprint.token['access_token'] 
#     resp = github.post(
#         'https://api.github.com/applications/' + os.getenv('GITHUB_ID') + '/token',
#         params={"token": token},
#         headers={"Content-Type": "application/x-www-form-urlencoded"}
#     )

#     # assert resp.ok, resp.text
#     logout_user()
#     # del github_blueprint.token
#     return jsonify({'message': "You logged out successfully"}), 200


@auth.route('/register', methods=['POST'])
def register():
    userData = request.get_json()
    data = userData.get('user')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if username is None or email is None or password is None:
        return jsonify({'error': 'Missing fields'}), 400
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    
    # Send email verification email
    # msg = Message('Email Verification', recipients=[new_user.email])
    # msg.body = f'To verify your email, click on the following link: {request.host_url}auth/verify_email/{token}'
    # mail.send(msg)
    
    return jsonify({'message': 'Registration successful'}), 201

@auth.route('/api/login', methods=['POST'])
def login():
    credentials = request.get_json()
    data = credentials.get('credentials')
    username = data.get('username')
    password = data.get('password')
    
    if username is None or password is None:
        return jsonify({'error': 'Missing fields'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    login_user(user)
    header_access_token = user.get_token()
    # jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config.get('SECRET_KEY'))    
    return jsonify({
        'message': 'Login successful',
        'header_access_token': header_access_token
        }), 200

@auth.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user_data, user_id):
    # logout_user()
    header_access_token = request.headers['header-access-token']
    user = User.query.filter_by(username=user_id['username']).first()
    if user_id['username'] != user.verify_token(header_access_token):
        response = {'message': 'An error occured.'}
        return make_response(jsonify(response)), 403            
    try:
        # insert the token
        blacklist_token = BlacklistToken(token=header_access_token)
        blacklist_token.save()
        response = {
            'message': 'Successfully logged out.'
        }
        return make_response(jsonify(response)), 200
    except Exception as e:
        response = {
            'message': e
        }
        return make_response(jsonify(response)), 200 

@auth.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    
    if email is None:
        return jsonify({'error': 'Missing fields'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({'error': 'Invalid email address'}), 404
    
    token = user.generate_password_reset_token()
    
    # msg = Message('Reset Password', recipients=[user.email])
    # msg.body = f'To reset your password, click on the following link: {request.host_url}reset_password/{token}'
    
    # mail.send(msg)
    
    return jsonify({'message': 'Password reset email sent'}), 200

@auth.route('/reset_password/<token>', methods=['POST'])
def reset_password_confirm(token):
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email is None or password is None:
        return jsonify({'error': 'Missing fields'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user is None or not user.verify_password_reset_token(token):
        return jsonify({'error': 'Invalid email address or token'}), 404
    
    user.set_password(password)
    
    db.session.commit()
    
    return jsonify({'message': 'Password reset successful'}), 200

# @auth.route('/verify_email/<token>', methods=['GET'])
# def verify_email(token):
#     try:
#         # Load email from token
#         email = serializer.loads(token, salt='email-verification', max_age=3600)
#         # Find user with email
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify(message='Invalid token'), 400

#         # Mark email as verified
#         user.email_verified = True
#         db.session.commit()

#         return jsonify(message='Email verified successfully'), 200
#     except:
#         return jsonify(message='Invalid token'), 400
        
@auth.route("/profile")
@token_required
# @login_required
def locked(current_user_data, user_id):
    return jsonify({
        'message': "protected route",
        'user': user_id,
        }), 200