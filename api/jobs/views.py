# api/jobs/views.py
from selenium import webdriver

from bs4 import BeautifulSoup

# universal imports
from flask import jsonify, request

# local imports
from . import jobs

# search jobs route
@jobs.route('/api/v1/search', methods=['POST'])
def search_jobs():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--disable-extensions')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Web Driver\chromedriver.exe')

    search = request.get_json()
    # print(search)
    ro = search['roles']
    spe = search['speciality']
    fil = search['filter_out']
    aft = search['after_date']
    bef = search['before_date']

    url = 'https://www.google.com/search?q=site%3Alever.co+%7C+site%3Agreenhouse.io+%7C+site%3Ajobs.ashbyhq.com+%7C+site%3Aapp.dover.io'
    role_name = '+%28engineer+%7C+developer%29'
    speciality = '+%22' + spe + '%22'
    filter_out = '+-staff+-principal+-lead+-%22c%2B%2B%22'
    before_date = "+before%3A" + bef
    after_date = "+after%3A" + aft

    PAGE_URL = url + role_name + speciality + filter_out + after_date
    # print(url + role_name + speciality + filter_out + after_date)
    driver.get(PAGE_URL)
    content = driver.page_source
    # print(content)
    soup = BeautifulSoup(content, 'html.parser')

    allRoles = soup.find_all(['h3'])
    # print(allRoles)
    jobDate = soup.find_all('span', attrs={'class': 'MUxGbd wuQ4Ob WZ8Tjf'})
    div = soup.find_all("div", class_="yuRUbf")

    links = []
    for a in soup.find_all("div", class_="yuRUbf"):
        link = a.find('a', href=True)
        links.append(link['href'])
    
    summary = []
    for s in soup.find_all('div', class_='VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf'):
        all = s.find_all('span')
        summary.append(all[2].text.replace('\n', ''))

    u = list()
    # print(links)
    for i in range(0, len(links)):
        u.append({
            'role': allRoles[i+1].text.replace('\n', ''),
            'url': links[i],
            'job_date': jobDate[i].text.replace('\n', '')[:-3],
            'summary': summary[i]
            })
    # print(u)
    return u

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