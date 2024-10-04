from vector_db import get_relevant_context

test_query = "What is the most common dishwasher issue?"

try:
    context = get_relevant_context(test_query)
    if context:
        print("Relevant context retrieved successfully:")
    else:
        print("No relevant context found.")
except Exception as e:
    print(f"Error querying Pinecone: {e}")