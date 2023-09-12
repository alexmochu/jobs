import os
import asyncio

import re

# universal imports
from flask import jsonify, request, make_response
from ..models import Letter

# local imports
from . import letters
from ..utilities import token_required

@letters.route('/api/letters/<id>')
@token_required
def get_current_user_letters(current_user, data, id):
    """GET letters created by current_user."""
    try:
        # get all businesses created by the user currently logged in
        all_letters = Letter.query.order_by(Letter.id.desc()).filter_by(id=id)
        letters = []
        for letter in all_letters:
            letter_data = {
            'letter_id': letter.id,
            'letter_title': letter.cover_title, 
            'letter_owner' : letter.cover_owner,
            'letter_description': letter.cover_letter,
            }
            letters.append(letter_data)
        if letters:
            return jsonify({'letters': letters}), 200
        return jsonify({
            "message": "You haven't created any cover letters",
            "letters": []
            }), 201
    except Exception:
        return make_response(jsonify({"error": "Server error"})), 500

@letters.route('/api/letters', methods=['POST'])
@token_required
def create_letter(current_user, data):   
    """ Method to create review."""
    letter_item = request.get_json()
    letter_title = letter_item['letter']['letterTitle']
    letter_description = letter_item['letter']['letterDescription'],
    try:
        created_letter = Letter(
            cover_title=letter_title, 
            cover_owner = data['id'],  
            cover_letter = letter_description
            )
        created_letter.save()
        response = jsonify({
            'message': 'Letter created successfully.',
            'letter': {
                'letter_id': created_letter.id,
                'letter_title': created_letter.cover_title,
                'letter_description': created_letter.cover_letter,
            }
            })
    except KeyError:
        response = {"error": "There was an error creating the letter, please try again"}
        return make_response(jsonify(response)), 500                            
    return make_response(response), 201 

@letters.route('/api/letter/<letter_id>', methods=['PUT'])
@token_required
def update_letters(current_user, data, letter_id):
    current_letter = Letter.query.filter_by(id=letter_id).first()
    owner = current_letter.cover_owner
    if data['id'] == owner:
    # Obtain the new name of the business from the request data
        letter = request.get_json()
        letter_title: letter['letter']['cover_title']
        letter_cover: letter['letter']['cover_letter']
        try:
            current_letter.cover_title = letter_title
            current_letter.cover_letter = letter_cover
            current_letter.save()
            response = {
                'message': 'Letter updated successfully.',
                'letter': {
                    'letter_id': current_letter.id,
                    'letter_title': current_letter.cover_title,
                    'letter_description': current_letter.cover_letter,
                    }
                        }
            return make_response(jsonify(response)), 200
        except KeyError:
            response = {"error": "There was an error updating the cover letter, please try again"}
            return make_response(jsonify(response)), 500
    response = {"error": "You can only update your own cover letter"}
    return jsonify(response), 401  

@letters.route('/api/letter/<letter_id>', methods=['DELETE'])
@token_required
def delete_letter_by_id(current_user, data, letter_id):
    """ Method to get letter by ID """
    letter = Letter.query.filter_by(id=letter_id).first()
    owner = letter.cover_owner
    if data['id'] == owner:
        letter.delete()
        response = {
            "result": "Letter {} deleted".format(letter.id),
            "letter": {
                'letter_id': letter.id,
                'letter_title': letter.cover_title,
                'letter_description': letter.cover_letter,
            }
            }
        return jsonify(response), 200
    response = {"error": "You can only delete your own letter"}
    return jsonify(response), 401                   
