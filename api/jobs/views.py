# api/jobs/views.py
from selenium import webdriver
from bs4 import BeautifulSoup

# universal imports
from flask import jsonify

# local imports
from . import jobs

# search jobs route
@jobs.route('/api/v1/search')
def search_jobs():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--disable-extensions')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Web Driver\chromedriver.exe')

    url = 'https://www.amazon.com/s?k='
    search = 'smartphone'
    # driver.get(url+search)

    response = jsonify({"message": "Search"})
    URL = "https://www.google.com/search?q=site%3Alever.co+%7C+site%3Agreenhouse.io+%7C+site%3Ajobs.ashbyhq.com+%7C+site%3Aapp.dover.io+%28engineer+%7C+developer%29+%22react%22+-staff+-principal+-lead+-%22c%2B%2B%22+after%3A2022-11-01"
    driver.get(URL)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    allRoles = soup.find_all('h3')
    u = list()
    for i in range(0, len(allRoles)):
        u.append(allRoles[i].text.replace('\n', ''))
        l ={}
    print(u)
    # print(soup.find_all('div', attrs = {'class': 'Z26q7c UK95Uc jGGQ5e'}))
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