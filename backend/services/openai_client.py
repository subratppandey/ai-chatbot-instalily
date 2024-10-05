from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
CHATGPT_MODEL = "gpt-4"

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_embedding(text):
    try:
        response = openai_client.embeddings.create(input=[text], model=OPENAI_EMBEDDING_MODEL)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
       print(f"Error generating embedding: {e}")

def generate_response(conversation_history, user_query, context):
    """Generate a response using ChatGPT and maintain conversation history."""
    # Append the user query to the conversation history
    conversation_history.append({"role": "user", "content": user_query})

    # Construct the full prompt using conversation history and relevant context from Pinecone
    prompt = f"""
       You are created to assist users with detailed information for refrigerators and dishwashers from the website: PartSelect.com.
       Your tasks are to:
       1. Extract specific information from the PartSelect website, focusing on detailed data about refrigerators and dishwashers using their model numbers.
       2. Deliver in-depth knowledge of refrigerator and dishwasher components, including their functions, ability to work with or be compatible across different brands, and exact placement within the appliance.
       3. Diagnose, troubleshoot, and resolve both common and complex issues encountered with refrigerators and dishwashers.

       When interacting with users, please follow these specific guidelines:
       1. **Model Numbers Only**: When the user asks for details about a refrigerator or dishwasher, always ask for the **model number**. Do not call the model details function based on brand names like Whirlpool, Samsung, etc. Prompt the user to provide the model number.
       2. **PartSelect Numbers Only**: If the user requests information about a specific part, always ask for the **PartSelect number** (which starts with "PS"). Ask for the PartSelect number and retrieve information only when it is provided.
       3. **Troubleshooting and Repairs**: Only from the provided context; provide expert troubleshooting advice based on the user's problem description, suggest potential fixes, and provide installation instructions, video links, or other relevant information.

       If there are any relevant video links in the context provided, prioritize surfacing them to the user in your response. For example, if a video link is available for installing or troubleshooting a part or model, explicitly include it in your response. If there are no video links, offer other appropriate advice.
       Do not mention that you're limited by browsing capabilities.

       Here is the context retrieved from the PartSelect website, if available:
       {context}

       If the context does not provide the exact information needed, please use your expertise to give general advice about dishwashers and refrigerators. Always ask for the **model number** or **PartSelect number** if more specific information is required to assist the user.
       Do not mention that you're limited by training data or lack of browsing capabilities, and avoid repeating information unless explicitly requested by the user. Refrain from providing incorrect answers to your best.
       Provide a detailed and comprehensive response to the users.

       User's question: "{user_query}"
   """

    messages = [
        {
            "role": "system",
            "content": """ You are a specialized assistant that only answers questions related to refrigerators and dishwashers.
            If the user asks something outside the scope of refrigerators or dishwashers, remind them to ask a question specifically about these appliances.
            Always prioritize questions about refrigerator or dishwasher-related topics, part installations, troubleshooting.
            """
       }
   ] + conversation_history
    messages.append({"role": "user", "content": prompt})

    response = openai_client.chat.completions.create(
        model=CHATGPT_MODEL,
        messages=messages,
        temperature=0.1,
    )

    assistant_answer = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_answer})
  
    return assistant_answer
