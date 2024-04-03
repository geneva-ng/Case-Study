""" this is an alternative architecture that does not have conversational memory, 
    meaning the user must provide ample context for each query and cannot ask follow-up questions, 
    but instead can switch between topics naturally. New context is retrieved for every
    query rather than just at the start of the conversation. """

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

@app.route('/')
def hello_world():
    return render_template('index.html')

# GET MESSAGES: called after user presses "Send" on frontend
@app.route('/get-message', methods=['POST'])
def get_message():

    global memory
    data = request.json
    user_query = data.get('query', 'No query provided')

    context_response = vector_store.search_context(user_query)
    context = ' '.join(doc for doc_list in context_response['documents'] for doc in doc_list)

    # generate response based on entire current conversation memory 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who is an incredible sales representative for the online storefront PartSelect. You will be speaking to a customer who will be seeking guidance on products and installations. If the customer veers off this topic, politely decline to answer, and kindly but firmly get back on topic."},
            {"role": "user", "content": context + "\n\n" + user_query}
        ]
    )

    # extract response and append to conversation memory
    response_content = response.choices[0].message.content

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
