from flask import Blueprint, request, jsonify
from services.conversation import Conversation  # Import the conversation handler
from services.vector_db import get_relevant_context  # Import Pinecone context retriever
from services.openai_client import generate_response  # Import the OpenAI response generator

api_blueprint = Blueprint('api', __name__)  # Create a Blueprint for your routes
conversation = Conversation()  # Initialize the conversation handler

# # Route to handle user query
# @api_blueprint.route('/query', methods=['POST'])
# def query():
#     data = request.json  # Get the JSON payload from the frontend
#     user_query = data.get("question", "")  # Extract the question from the request


#     if not user_query:
#         return jsonify({"error": "No question provided"}), 400  # Handle empty query


#     # Fetch relevant context from Pinecone
#     context = get_relevant_context(user_query)


#     # Generate response using ChatGPT and context from Pinecone
#     answer = generate_chatgpt_response(conversation.get_conversation(), user_query, context)


#     # Add the query and response to conversation history
#     conversation.add_user_message(user_query)
#     conversation.add_assistant_message(answer)


#     # Send back the question and answer as a JSON response
#     return jsonify({"question": user_query, "answer": answer})


# # Route to clear the conversation history
# @api_blueprint.route('/clear_history', methods=['GET'])
# def clear_history():
#     conversation.clear_history()  # Clear the conversation history
#     return jsonify({"message": "Conversation history cleared successfully"})

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