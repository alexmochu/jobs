# api/jobs/views.py

# universal imports
from flask import Flask, jsonify, request, make_response

# local imports
from . import jobs

# search jobs route
@jobs.route('/api/v1/search')
def search_jobs():
    response = jsonify({"message": "Search"})
    return response

# @business.route('/api/v2/search', methods=['GET'])
# def search(limit=6, page=1):
#     """Search for business in the system"""
#     role = request.args.get("location")
#     speciality = request.args.get("category")
#     before = this.date
#     after = this.date
#     # get q search value and use if available
#     q = request.args.get("q")

#     if q and location:
#         found_businesses = Business.query.filter(Business.business_location.ilike('%{}%'.format(location)), Business.business.ilike('%{}%'.format(q))).paginate(page, per_page = limit, error_out=False).items
#         found_business_list = []
#         if not found_businesses:
#             return jsonify({'message': 'No existing businesses have been found'}), 404
#         for business_item in found_businesses:
#             available_business = {'business_name': business_item.business, 'business_category_id': business_item.category, 'business_location': business_item.business_location, 'owner':business_item.owner}
#             found_business_list.append(available_business)
#         return jsonify({'Businesses': found_business_list}), 200 
#     elif location:
#         location_businesses = Business.query.filter(Business.business_location.ilike('%{}%'.format(location))).paginate(page, per_page = limit, error_out=False).items
#         business_list = []
#         if not location_businesses:
#             return jsonify({'message': 'There are no existing business in this location'}), 404
#         for business_item in location_businesses:
#             found_business = {'business_name': business_item.business, 'business_category': business_item.category, 'business_location': business_item.business_location, 'owner':business_item.owner}
#             business_list.append(found_business)
#         return jsonify({'Businesses': business_list}), 200        
#     elif q:
#         name_business = Business.query.filter(Business.business.ilike('%{}%'.format(q))).paginate(page, per_page = limit, error_out=False).items
#         business_list = []
#         if not name_business:
#             return jsonify({'message': 'No existing businesses'}), 404
#         for business_item in name_business:
#             found_business = {'business_name': business_item.business, 'business_category': business_item.category, 'business_location': business_item.business_location, 'owner':business_item.owner}
#             business_list.append(found_business)
#         return jsonify({'Businesses': business_list}), 200
#     else:
#         return jsonify({'Warning': 'Cannot comprehend the given search parameter'})