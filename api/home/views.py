# api/home/views.py

# universal imports
from flask import Flask, jsonify, request, make_response

# local imports
from . import home

# home route
@home.route('/')
def hello_world():
    response = jsonify({"message": "Welcome to Kejani's Garage Job Scrapper"})
    return response