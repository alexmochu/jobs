import os
import asyncio

import re

# universal imports
from flask import jsonify, request, make_response
from ..models import Resume

# local imports
from . import resumes
from ..utilities import token_required

@resumes.route('/api/resumes/<id>')
@token_required
def get_current_user_resumes(current_user, data, id):
    """GET resumes created by current_user."""
    try:
        # get all businesses created by the user currently logged in
        all_resumes = Resume.query.order_by(Resume.id.desc()).filter_by(resume_owner=id)
        resumes = []
        for resume in all_resumes:
            resume_data = {
            'resume_id': resume.id,
            'resume_title': resume.resume_title, 
            'resume_owner' : resume.resume_owner,
            'resume_details': resume.resume_details,
            'resume_template': resume.resume_template
            }
            resumes.append(resume_data)
        if resumes:
            return jsonify({'resumes': resumes}), 200
        return jsonify({
            "message": "You haven't created any resumes",
            "resumes": []
            }), 201
    except Exception:
        return make_response(jsonify({"error": "Server error"})), 500

@resumes.route('/api/resumes', methods=['POST'])
@token_required
def create_resume(current_user, data):   
    """ Method to create resume."""
    resume_item = request.get_json()
    resume_title = resume_item['resume']['resumeTitle']
    resume_template = resume_item['resume']['resumeTemplate']
    resume_details = resume_item['resume']['resumeDetails'],
    try:
        created_resume = Resume(
            resume_title=resume_title, 
            resume_owner = data['id'],  
            resume_details = resume_details,
            resume_template = resume_template
            )
        created_resume.save()
        response = jsonify({
            'message': 'Resume created successfully.',
            'resume': {
                'resume_id': created_resume.id,
                'resume_title': created_resume.resume_title,
                'resume_details': created_resume.resume_details,
                'resume_template': created_resume.resume_template
            }
            })
    except KeyError:
        response = {"error": "There was an error creating the resume, please try again"}
        return make_response(jsonify(response)), 500                            
    return make_response(response), 201 

@resumes.route('/api/resume/<resume_id>', methods=['PUT'])
@token_required
def update_resume(current_user, data, resume_id):
    current_resume = Resume.query.filter_by(id=resume_id).first()
    owner = current_resume.resume_owner
    if data['id'] == owner:
    # Obtain the new name of the business from the request data
        resume = request.get_json()
        resume_title = resume['resume']['resume_title']
        resume_details = resume['resume']['resume_details']
        resume_template = resume['resume']['resume_template']
        try:
            current_resume.resume_title = resume_title
            current_resume.resume_details = resume_details
            current_resume.resume_template = resume_template
            current_resume.save()
            response = {
                'message': 'Resume updated successfully.',
                'resume': {
                    'resume_id': current_resume.id,
                    'resume_title': current_resume.resume_title,
                    'resume_details': current_resume.resume_details,
                    'resume_template': current_resume.resume_template
                    }
                        }
            return make_response(jsonify(response)), 200
        except KeyError:
            response = {"error": "There was an error updating the resume, please try again"}
            return make_response(jsonify(response)), 500
    response = {"error": "You can only update your own resume"}
    return jsonify(response), 401  

@resumes.route('/api/resume/<resume_id>', methods=['DELETE'])
@token_required
def delete_resume_by_id(current_user, data, resume_id):
    """ Method to get resume by ID """
    resume = Resume.query.filter_by(id=resume_id).first()
    owner = resume.resume_owner
    if data['id'] == owner:
        resume.delete()
        response = {
            "result": "Resume {} deleted".format(resume.id),
            "resume": {
                'resume_id': resume.id,
                'resume_title': resume.resume_title,
                'resume_details': resume.resume_details,
                'resume_template': resume.resume_template
            }
            }
        return jsonify(response), 200
    response = {"error": "You can only delete your own resume"}
    return jsonify(response), 401                   
