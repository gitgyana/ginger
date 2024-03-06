from credentials import api_key, assistant_id, assistant_url
from flask import Flask, render_template, request, jsonify, redirect, url_for
from ibm_watson import AssistantV2, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

app = Flask(__name__)

authenticator = IAMAuthenticator(api_key)
assistant = AssistantV2(
    version='2023-06-15',
    authenticator=authenticator
)
assistant.set_service_url(assistant_url)

session_id = None
db_value = {}
database = []

def create_session():
    session_response = assistant.create_session(
        assistant_id=assistant_id
    )
    global session_id
    session_id = session_response.get_result()['session_id']


def create_dict(session_id, user_input, response):
    db_value[user_input] = response
    global database
    database.append(db_value)
    # print(database)


@app.route('/')
def index():
    create_session()
    return render_template('index.html')


@app.route('/message', methods=['POST'])
def message():
    user_input = request.json['message']
    
    response = assistant.message(
        assistant_id=assistant_id,
        session_id=session_id,
        input={
            'message_type': 'text',
            'text': user_input
           }
    ).get_result()
    
    create_dict(session_id, user_input, jsonify(response))

    return jsonify(response)


@app.route('/new_session', methods=["GET"])
def new_session():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
