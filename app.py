# Necessary Libraries/Modules
from credentials import api_key, assistant_id, assistant_url, mongodb_url
from flask import Flask, render_template, request, jsonify, redirect, url_for
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pymongo import MongoClient

# Creating flask instance
app = Flask(__name__)

# MongoDB setup
collection = MongoClient(mongodb_url)
db = collection['GingerV5']
messages_collection = db['test1']

# Authenticate and connect with IBM Watsonx.ai
authenticator = IAMAuthenticator(api_key)
assistant = AssistantV2(
    version='2023-06-15',
    authenticator=authenticator
)
assistant.set_service_url(assistant_url)

# Store session ID
session_id = None

# Create session ID
def create_session():
    session_response = assistant.create_session(
        assistant_id=assistant_id
    )
    global session_id
    session_id = session_response.get_result()['session_id']

# Root Directory [Home Page]
@app.route('/')
def index():
    create_session()
    return render_template('index.html')

# Receive user message, send response, and store messages in the MongoDB
@app.route('/message', methods=['POST'])
def message():
    user_input = request.json['message']
    
    # Send user input to Watson Assistant
    response = assistant.message(
        assistant_id=assistant_id,
        session_id=session_id,
        input={
            'message_type': 'text',
            'text': user_input
           }
    ).get_result()

    # Save incoming and outgoing messages to MongoDB
    messages_collection.insert_one({
        'user_input': user_input,
        'assistant_response': response
    })

    return jsonify(response)

# Create new session
@app.route('/new_session', methods=["GET"])
def new_session():
    create_session()

    response = assistant.message(
        assistant_id=assistant_id,
        session_id=session_id,
        input={
            'message_type': 'text',
            'text': 'start_conversation'
           }
    ).get_result()
    
    return jsonify(response)

# Run flask application
if __name__ == '__main__':
    app.run(debug=True)
