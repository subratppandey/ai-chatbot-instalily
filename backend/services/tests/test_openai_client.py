from openai_client import get_openai_embedding

test_text = "Is this part compatible with my WDT780SAEM1 model?"

embedding = get_openai_embedding(test_text)

if embedding:
    print(f"Embedding generated successfully: {embedding[:10]}...")
else:
    print("Failed to generate embedding.")