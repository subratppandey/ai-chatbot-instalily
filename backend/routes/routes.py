from flask import Blueprint, request, jsonify
from services.conversation import Conversation  
from services.vector_db import get_relevant_context  
from services.openai_client import generate_response  

api_blueprint = Blueprint('api', __name__)  # Create a Blueprint for your routes
conversation = Conversation() 

@api_blueprint.route('/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get("question", "")

    if not user_query:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Fetch relevant context from Pinecone
        context = get_relevant_context(user_query)

        # Generate response using ChatGPT and context from Pinecone
        answer = generate_response(conversation.get_conversation(), user_query, context)

        # Add the query and response to conversation history
        conversation.add_user_message(user_query)
        conversation.add_assistant_message(answer)

        return jsonify({"question": user_query, "answer": answer})
  
    except Exception as e:
        print(f"Error during query processing: {e}")
        return jsonify({"error": "There was an error processing your request"}), 500