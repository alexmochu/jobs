import os
from flask import jsonify, request, make_response
from flask_login import login_user

from . import auth
from .. import db
from ..models import User, BlacklistToken
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
    try:
        credentials = request.get_json()
        data = credentials.get('credentials')
        username = data.get('username')
        password = data.get('password')
        
        if username is None or password is None:
            return jsonify({'error': 'Missing fields'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user and user.check_password(password):
            login_user(user)
            header_access_token = user.get_token()
            # jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config.get('SECRET_KEY'))    
            return jsonify({
                'message': 'You logged in successfully.',
                'header_access_token': header_access_token
                }), 200
        else:
            # User does not exist. Therefore, we return an error message
            response = {'error': 'Invalid username or password, Please try again'}
            return make_response(jsonify(response)), 401

    except Exception as e:
        # Create a response containing an string error message
        response = {'error': str(e)}
        # Return a server error using the HTTP Error Code 500 (Internal Server Error)
        return make_response(jsonify(response)), 500

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
    
@auth.route('/api/change-password', methods=['PUT'])
@token_required
def change_password(current_user, data):
    passwords = request.get_json()
    items = passwords['passwords']
    user = User.query.filter_by(username=data['username']).first()
    req = request.get_json()
    old_password = items['current_password']
    new_password = items['new_password']
    confirm_password = items['confirm_password']

    user = User.query.filter_by(username=data['username']).first()

    if not user.check_password(old_password):
        return jsonify({'error': 'Invalid password'}), 401
    
    if (new_password!=confirm_password):
        # Verify passwords are matching
        response = {'error':'The passwords should match!'}
        return make_response(jsonify(response)), 302
    try:
        # Edit the password
        user.set_password(new_password)
        db.session.add(user)
        db.session.commit()
        response = {'message': 'Password changed successfully.'}
    except Exception as e:
        # Create a response containing an string error message
        response = {'message': str(e)}
        # Return a server error using the HTTP Error Code 500 (Internal Server Error)
        return make_response(jsonify(response)), 500
    return make_response(jsonify(response)), 200

@auth.route('/api/reset-password', methods=['POST'])
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
    
    return jsonify({
        'message': 'Password reset email sent',
        'token': token
        }), 200

@auth.route('/api/reset-password/<token>', methods=['PUT'])
def reset_password_confirm(token):
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({'error': 'Invalid email address'}), 404        

    if (password!=confirm_password):
        # Verify passwords are matching
        response = {'error':'The passwords should match!'}
        return make_response(jsonify(response)), 302

    if not user.verify_password_reset_token(token):
        return jsonify({'error': 'Invalid token'}), 404
    
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Password has been reseted successful'}), 200

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
#         user.verified = True
        
#         db.session.add(user)
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