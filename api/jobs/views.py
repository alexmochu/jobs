import os
import asyncio
from langchain.agents import initialize_agent
from langchain.agents import load_tools,initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain.agents.agent_toolkits import PlayWrightBrowserToolkit
# from langchain.tools.playwright.utils import (
#     create_async_playwright_browser,
# )
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from playwright.async_api import async_playwright
import re
from playwright.sync_api import Page, expect
from langchain.chat_models import ChatAnthropic

os.environ["GOOGLE_CSE_ID"] = ""
os.environ["GOOGLE_API_KEY"] = "AIzaSyAPMkDsSq80BMrOwrreedFzr6lTeGQO-UY"
os.environ["SERPAPI_API_KEY"] = "adcce69ae1aadbc78fe655089b91e21a65f5fbcda3e98d3e04f00f4b8c42770a"
os.environ["OPENAI_API_KEY"] = "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"

# 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

# api/jobs/views.py

# universal imports
from flask import jsonify, request, make_response
from ..models import Job

# local imports
from . import jobs
from ..utilities import token_required

# search jobs route
# @jobs.route('/api/v1/search', methods=['POST'])
# def search_jobs():
#     options = webdriver.ChromeOptions()
#     options.add_argument('--ignore-certificate-errors')
#     options.add_argument('--incognito')
#     options.add_argument('--headless')
#     options.add_argument('--disable-extensions')
#     options.add_argument('start-maximized')
#     options.add_argument('disable-infobars')
#     driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Web Driver\chromedriver.exe')

#     search = request.get_json()
#     ro = search['roles']
#     spe = search['speciality']
#     fil = search['filter_out']
#     aft = search['after_date']
#     bef = search['before_date']

#     url = 'https://www.google.com/search?q=site%3Alever.co+%7C+site%3Agreenhouse.io+%7C+site%3Ajobs.ashbyhq.com+%7C+site%3Aapp.dover.io'
#     role_name = '+%28engineer+%7C+developer%29'
#     speciality = '+%22' + spe + '%22'
#     filter_out = '+-staff+-principal+-lead+-%22c%2B%2B%22'
#     before_date = "+before%3A" + bef
#     after_date = "+after%3A" + aft

#     PAGE_URL = url + role_name + speciality + filter_out + after_date
#     driver.get(PAGE_URL)
#     content = driver.page_source
#     soup = BeautifulSoup(content, 'html.parser')

#     allRoles = soup.find_all(['h3'])
#     jobDate = soup.find_all('span', attrs={'class': 'MUxGbd wuQ4Ob WZ8Tjf'})
#     div = soup.find_all("div", class_="yuRUbf")

#     links = []
#     for a in soup.find_all("div", class_="yuRUbf"):
#         link = a.find('a', href=True)
#         links.append(link['href'])
    
#     summary = []
#     for s in soup.find_all('div', class_='VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf'):
#         all = s.find_all('span')
#         summary.append(all[2].text.replace('\n', ''))

#     u = list()
#     for i in range(0, len(links)):
#         u.append({
#             'role': allRoles[i+1].text.replace('\n', ''),
#             'url': links[i],
#             'job_date': jobDate[i].text.replace('\n', '')[:-3],
#             'summary': summary[i]
#             })
#     return u

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

@jobs.route('/api/jobs/<userName>')
@token_required
def get_current_user_jobs(current_user, data, userName):
    """GET jobs created by current_user."""
    try:
        # get all businesses created by the user currently logged in
        all_jobs = Job.query.order_by(Job.id.desc()).filter_by(job_owner=userName)
        jobs = []
        print(all_jobs)
        for job in all_jobs:
            job_data = {
            'job_id': job.id,
            'job_title': job.job_title, 
            'job_owner' : job.job_owner,
            'job_company': job.job_company,
            'job_location': job.job_location,
            'job_description': job.job_description,
            'job_url': job.job_url,
            'job_state': job.application_state,
            'job_type': job.job_type
            }
            jobs.append(job_data)
        if jobs:
            return jsonify({'jobs': jobs}), 200
        return jsonify({"message": "You haven't created any jobs"}), 404
    except Exception:
        return make_response(jsonify({"error": "Server error"})), 500


    # id = db.Column(db.Integer, primary_key=True)
    # job_title = db.Column(db.String(128))
    # job_company = db.Column(db.String(128))
    # job_location = db.Column(db.String(50))
    # job_description = db.Column(db.String(500))
    # job_owner = db.Column(db.String, db.ForeignKey('users.username'))
    # job_url = db.Column(db.String(128))
    # application_state = db.Column(db.String(50))

@jobs.route('/api/jobs', methods=['POST'])
@token_required
def create_job(current_user, data):   
    """ Method to create review."""
    job_item = request.get_json()
    job_title = job_item['job']['jobTitle']
    job_company = job_item['job']['jobCompany']
    job_location = job_item['job']['jobLocation'],
    job_description = job_item['job']['jobDescription'],
    job_type = job_item['job']['jobType'],
    job_url = job_item['job']['jobUrl'],
    application_state = job_item['job']['applicationState']
    try:
        created_job = Job(
            job_title=job_title, 
            job_owner = data['username'], 
            job_company=job_company, 
            job_location = job_location, 
            job_description = job_description,
            job_url = job_url,
            job_type = job_type,
            application_state = application_state) 
        created_job.save()
        response = jsonify({'message': 'Job created successfully.'})
    except KeyError:
        response = {"error": "There was an error creating the job, please try again"}
        return make_response(jsonify(response)), 500                            
    return make_response(response), 201 

@jobs.route('/api/job/<job_id>', methods=['PUT'])
@token_required
def update_business(current_user, data, job_id):
    current_job = Job.query.filter_by(id=job_id).first()
    owner = current_job.job_owner
    if data['username'] == owner:
    # Obtain the new name of the business from the request data
        job_item = request.get_json()
        job_title = job_item['job']['job_title']
        job_company = job_item['job']['job_company']
        job_location = job_item['job']['job_location'],
        job_description = job_item['job']['job_description'],
        job_type = job_item['job']['job_type'],
        job_url = job_item['job']['job_url'],
        application_state = job_item['job']['job_state']
        try:
            current_job.job_title = job_title
            current_job.job_company = job_company
            current_job.job_location = job_location
            current_job.job_description = job_description
            current_job.job_type = job_type
            current_job.job_url = job_url
            current_job.application_state = application_state
            current_job.save()
            response = {'message': 'Job updated successfully.'}
            return make_response(jsonify(response)), 200
        except KeyError:
            response = {"error": "There was an error updating the Job, please try again"}
            return make_response(jsonify(response)), 500
    response = {"error": "You can only update your own job"}
    return jsonify(response), 401  

@jobs.route('/api/job/<job_id>', methods=['DELETE'])
@token_required
def delete_business_by_id(current_user, data, job_id):
    """ Method to get job by ID """
    job = Job.query.filter_by(id=job_id).first()
    print('job id', job_id)
    owner = job.job_owner
    if data['username'] == owner:
        job.delete()
        response = {"result": "Job {} deleted".format(job.id)}
        return jsonify(response), 200
    response = {"error": "You can only delete your own job"}
    return jsonify(response), 401                   


response_schemas = [
    ResponseSchema(name="job_title", description="job title from the users question"),
    ResponseSchema(name="job_company", description="job company name from the users question"),
    ResponseSchema(name="job_company", description="job link from the users question")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

format_instructions = output_parser.get_format_instructions()
# prompt = PromptTemplate(
#     template="{question}"
    # answer the users question as best as possible.\n{format_instructions}\n{question}",
    # input_variables=["question"],
    # partial_variables={"format_instructions": format_instructions}
# )

# _input = prompt.format_prompt(question="results of 10 recent remote react jobs that accept worldwide applicants in 2023")
                            #   . List this jobs. The list should in json format containg the company name, job title and the url of the job description. Return this list as following")


@jobs.route('/api/v1/openai', methods=['GET'])
def openai_jobs():
    llm = OpenAI(temperature=0, model='text-davinci-003')
    tool_names = ["serpapi"]
    tools = load_tools(tool_names)
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
    # Browse to blog.langchain.dev and summarize the text
    # return agent.run("Explore google and find 10 recent remote react jobs that accept worldwide applicants. List this jobs. The list should in json format containg the company name, job title and the url of the job description. Return this list as following {job_title: the job title, job_company: company name of the job, job_url: url of the job}")
    # return agent.run("what is langchain")
    return agent.run("search results of job url links of 10 recent remote react jobs that accept worldwide applicants in 2023")

async def create_async_playwright_browser(loop):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Perform browser actions here

        await browser.close()

@jobs.route('/api/job_summary', methods=['GET'])
async def job_summary():
    loop = asyncio.get_running_loop()
    # async_browser = await create_async_playwright_browser(loop)
    # # async_browser = await create_async_playwright_browser(loop)
    # browser_toolkit = PlayWrightBrowserToolkit(async_browser=async_browser, sync_browser=None)
    # tools = browser_toolkit.get_tools()
    # llm = ChatOpenAI(temperature=0) # Also works well with Anthropic models
    # agent_chain = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    # response = agent_chain.arun(input="Browse to https://jobs.kejanigarage.com/ and summarize the text, please.")
    # return make_response(jsonify({
    #     'summary': response
    # }))
    async_browser = create_async_playwright_browser(loop)
    toolkit = PlayWrightBrowserToolkit(sync_browser=None, async_browser=None)
    tools = toolkit.get_tools()
    llm = ChatAnthropic(temperature=0)  # or any other LLM, e.g., ChatOpenAI(), OpenAI()

    agent_chain = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    result = await agent_chain.arun("What are the headers on langchain.com?")
    print(result)

