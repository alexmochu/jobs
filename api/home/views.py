# api/home/views.py
import os

# universal imports
from flask import Flask, jsonify, request, make_response
from flask_mail import Message
from .. import create_app

# # Initialize the Flask app
# app = create_app(os.getenv('APP_SETTINGS'))

# # Access the 'mail' object from the Flask app
# mail = app.extensions['mail']

# local imports
from . import home

# home route
@home.route('/api')
def hello_world():
    response = jsonify({"message": "Welcome to Kejani's Garage Job Scrapper"})
    return response

@home.route('/api/contact-us', methods=['POST'])
def contact_us():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    msg = Message('New Contact Form Submission', sender='your-email@gmail.com', recipients=['recipient-email@example.com'])
    msg.body = f"Napiame: {name}\nEmail: {email}\nMessage: {message}"

    try:
        mail.send(msg)
        return 'Email sent successfully', 200
    except Exception as e:
        print(str(e))
        return 'Error sending email', 500