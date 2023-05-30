import os
import jwt
import datetime

from flask import Flask, jsonify, request, make_response, redirect, url_for, current_app
from flask_login import current_user, login_user
from flask_login import login_required, logout_user
from flask_cors import cross_origin
from functools import wraps

from . import auth
from .. import db
from ..models import OAuth, User, BlacklistToken
from ..utilities import token_required

@auth.route('/api/register', methods=['POST'])
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