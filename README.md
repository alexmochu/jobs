## Kejani Jobs API

# Technology Used

The API has been built with:

- Language: Python3.8
- Framework(micro): Flask 
- Postgresql Database

### Setup
`cd jobs`

- create virtual environment `python3 -m venv venv`
- create an environment variable file `.env` and add the envrionment variables shared at the bottom of this README file
- activate virtual environment `. venv/bin/activate` or `source .env`
- run api on the development environment with the debuging flag `flask --debug run`

#### Environment Variables(to be stored in the `.env` file)

- `FLASK_APP=run.py`
- `SECRET="325f0ca3-26f1-44f7-b8b4-c2298b0c500d`
- `APP_SETTINGS=development`
- `DATABASE_URL=your_postgres_db_here`
- `MAIL_DAFAULT_SENDER=ask_from_admin`
- `OPENAI_API_KEY=your_apenai_api_here`
- `OAUTHLIB_RELAX_TOKEN_SCOPE=1`


# UI and API Documentation

- To preview the UI, proceed to https://jobs.kejanigarage.com/ .
- To access the API hosted on the Render cloud platform -->> https://jobs-api-km5w.onrender.com/api

# Features

1.  Register and login
2.  Create a resume
3.  Create a profile 
4.  Question and Answer interview questions
5.  Create a resume
6.  Search for jobs
7.  Bookmark jobs

## Database setup
- Make sure you have setup a database URI on the .env file
- Initialize the database. Run `flask db init`
- Run database migrations `flask db migrate`
- Upgrade schema. Run `flask db upgrade`
- After the running the above commands the database should be populated with the right data/tables.

# API Endpoints

| Resource URL                                 | Methods | Description                                        |
| ---------------------------------------------| ------- | -------------------------------------------------- |
| /api                                         | GET     | Home                                               |
| /admin                                       | GET     | Get analytics                                      |
| /api/v1/search                               | POST    | Search Jobs online                                 |
| /kejani-ai/question                          | POST    | Q & A for interview questions                      |
| /profile                                     | GET     | User profile                                       |
| /reset_password/<token>                      | POST    | Reset Password<Link sent through email>            |
| /reset_password                              | POST    | Reset Password<Enter email>                        |
| /api/logout                                  | POST    | Logout                                             |
| /api/login                                   | POST    | Login user                                         |
| /api/register                                | POST    | Signup as a new user                               |
