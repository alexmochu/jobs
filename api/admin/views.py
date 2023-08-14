# api/admin/views.py

# universal imports
from flask import Flask, jsonify, request, make_response
# from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from ..utilities import token_required

# local imports
from . import admin
from ..models import User, Job

# Tutoral -> https://alexmarginean.medium.com/how-to-get-website-metrics-from-google-analytics-with-flask-python-cb9a4a7e8e33

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'kejaniauth-a9d0936c18e5.json'
VIEW_ID = '356870037' #You can find this in Google Analytics > Admin > Property > View > View Settings (VIEW ID)


def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics):
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:pageviews'}],
          'dimensions': []
        }]
      }
  ).execute()


def get_visitors(response):
  visitors = 0 # in case there are no analytics available yet
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dateRangeValues = row.get('metrics', [])

      for i, values in enumerate(dateRangeValues):
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          visitors = value

  return str(visitors)

# admin route
# @admin.route('/admin')
# def admin():
#     analytics = initialize_analyticsreporting()
#     res = get_report(analytics)
#     visitors = get_visitors(res)
    
#     response = jsonify({
#         "message": "Welcome to Kejani's Garage Admin",
#         "visitors": str(visitors)})
#     return response

# @admin.route('/visitors')
# def visitors():
#   analytics = initialize_analyticsreporting()
#   response = get_report(analytics)
#   visitors = get_visitors(response)
  
#   response = jsonify({"message": str(visitors)})
#   return response

@admin.route('/admin/users', methods=['GET'])
@token_required
def get_all_user(current_user, data):
    try:
        # get all businesses created by the user currently logged in
        all_users = User.query.order_by(User.id.desc())
        users = []
        for user in all_users:
            user_data = {
            'user_id': user.id,
            'user_username': user.username, 
            'user_email' : user.email,
            'user_role': user.role,
            'user_created': user.created_at,
            'user_verified': user.verified
            }
            users.append(user_data)
        if users:
            return jsonify({'users': users}), 200
        return jsonify({
            "message": "You dont have any users",
            "users": []
            }), 201
    except Exception:
        return make_response(jsonify({"error": "Server error"})), 500

@admin.route('/admin/jobs', methods=['GET'])
@token_required
def get_all_jobs(current_user, data):
    try:
        # get all businesses created by the user currently logged in
        all_jobs = Job.query.order_by(Job.id.desc())
        jobs = []
        for job in all_jobs:
            job_data = {
            'job_id': job.id,
            'job_title': job.job_title, 
            'job_owner' : job.job_owner,
            'job_company': job.job_company,
            'job_location': job.job_location,
            'job_description': job.job_description,
            'job_url': job.job_url,
            'application_state': job.application_state,
            'job_type': job.job_type
            }
            jobs.append(job_data)
        if jobs:
            return jsonify({'jobs': jobs}), 200
        return jsonify({
            "message": "No jobs have been created",
            "jobs": []
            }), 201
    except Exception:
        return make_response(jsonify({"error": "Server error"})), 500