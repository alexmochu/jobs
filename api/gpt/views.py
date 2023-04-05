import os

from flask import request, redirect, url_for

import openai

from . import gpt
from ..utilities import token_required

openai.api_key = os.getenv("OPENAI_API_KEY")
  
@gpt.route('/kejani-ai/question', methods=['GET', 'POST'])
@token_required
def question_gpt(current_user_data, user_id):
    if request.method == "POST":
        question = request.form["question"]
        job = request.form["job"]
        purpose = request.form["purpose"]
        position = request.form["position"]
        accountabilities = request.form["accountabilities"]
        resume = request.form["resume"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question_answer_propmt(question, job, purpose, position, accountabilities, resume),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return result, 200

def question_answer_propmt(question, job, purpose, position, accountabilities, resume):
    return """Write not more than a 300-word answer to a targeted question for job application
Targeted question= {question}
Base the answer using position {purpose} key accountabilities and resume
Position purpose = {purpose}
Key accountabilities = {accountabilities}
Resume = {resume}
Use key words from key accountabilities in the answer
Key accountabilities = {accountabilities}
"""