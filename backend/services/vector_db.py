import os
from pinecone import Pinecone, ServerlessSpec
from services.openai_client import get_openai_embedding
from dotenv import load_dotenv
import logging

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST_URL = os.getenv("PINECONE_HOST_URL")
PINECONE_INDEX_NAME = "150"

# Initialize Pinecone client using the new Pinecone class
pc = Pinecone(api_key=PINECONE_API_KEY, host_url=PINECONE_HOST_URL)

# Check if the index exists, create it if not
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536, 
        metric='cosine', 
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        )
    )

# Access the Pinecone index
index = pc.Index(PINECONE_INDEX_NAME)

def get_relevant_context(query):
    """Fetch relevant data from Pinecone given a user query."""
  
    # Generate embedding for the query using OpenAI's model
    query_embedding = get_openai_embedding(query)
    query_embedding = [float(x) for x in query_embedding]  # Convert to float32

    if query_embedding is None:
        logging.error("Failed to generate an embedding. Invalid embedding for query.")
        raise ValueError("Invalid embedding for query")
  
    # Query Pinecone for most similar chunks

    result = index.query(vector=[query_embedding], top_k=3, include_metadata=True)
    print(result)
  
    # context_list = [
    #     f"Title: {match['metadata'].get('page_title', '')}\n"
    #     f"URL: {match['metadata'].get('url', '')}\n"
    #     f"Installation Video: {match['metadata'].get('video_link', 'No video available')}"
    #     for match in result['matches']
    # ]

    # Extract all relevant fields and create the context for each match
    context_list = [
        f"Title: {match['metadata'].get('page_title', 'Not available')}\n"
        f"URL: {match['metadata'].get('url', 'Not available')}\n"
        f"Part Name: {match['metadata'].get('part_name', 'Not available')}\n"
        f"Part Info: {match['metadata'].get('part_info', 'Not available')}\n"
        f"Part Price: {match['metadata'].get('part_price', 'Not available')}\n"
        f"Manufacturer Name: {match['metadata'].get('manufacturer_name', 'Not available')}\n"
        f"Manufacturer Part Number: {match['metadata'].get('manufacturer_part_num', 'Not available')}\n"
        f"Fixes: {match['metadata'].get('fixes', 'No fixes available')}\n"
        f"Compatibility with Appliances: {match['metadata'].get('compatibility_with_appliances', 'Not available')}\n"
        f"Compatibility with Brands: {match['metadata'].get('compatibility_with_brands', 'Not available')}\n"
        f"Replaceable Parts: {match['metadata'].get('replace_parts', 'No replaceable parts available')}\n"
        f"Installation Video: {match['metadata'].get('video_link', 'No video available')}\n"
        for match in result['matches']
    ]
  
    # Combine all the context chunks
    combined_context = "\n".join(context_list)

    return combined_context

