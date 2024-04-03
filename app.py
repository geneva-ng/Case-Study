""" This is the main Flask app that supplies responses. In this version, I've implemented 
    "memory" or converstional context awareness so the user is able to ask follow-up
    questions without having to provide detailed context for every query. """

from flask import Flask, request, jsonify, session, render_template 
from flask_cors import CORS
from openai import OpenAI  
from dotenv import load_dotenv
from vector_store import VectorStore
import os
load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  
CORS(app)

vector_store = VectorStore("PartSelect")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
memory = [{"role": "system", "content": "You are a helpful assistant who is an incredible sales representative for the online storefront PartSelect. You will be speaking to a customer who will be seeking guidance on products and installations. If a query does not pertain to dishwasher or refridgerator parts, or does not adhere to the context of the conversation, do not answer it. Say \"I can't answer that question, but I'd be happy to help you with any appliance-related concerns."}]


@app.route('/')
def hello_world():
    return render_template('index.html')

# GET MESSAGES: called after user presses "Send" on frontend
@app.route('/get-message', methods=['POST'])
def get_message():

    global memory
    data = request.json
    user_query = data.get('query', 'No query provided')

    # add embedding context to conversation memory if this is the first query of the conversation
    if len(memory)<2: 
        context_response = vector_store.search_context(user_query)
        context = ' '.join(doc for doc_list in context_response['documents'] for doc in doc_list)
        memory.append({"role": "system", "content": context})

    # append user's message to conversation memory
    memory.append({"role": "user", "content": user_query})

    # generate response based on entire current conversation memory 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=memory
    )

    # extract response and append to conversation memory
    response_content = response.choices[0].message.content
    memory.append({"role": "assistant", "content": response_content})
    # session.modified = True

    # jsonify response to send to frontend
    response = {
        "role": "assistant",
        "content": response_content
    }
    return jsonify(response)


# CLEAR MEMORY: called when user presses "new question" button on frontend or page is reloaded
@app.route('/clear-memory', methods=['GET', 'POST'])
def clear_memory():
    global memory
    memory = [{"role": "system", "content": "You are a helpful assistant."}]  
    return jsonify({"status": "Memory cleared"})


if __name__ == '__main__':
    app.run(debug=True)
