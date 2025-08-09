import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(query, documents):
    """Generate LLM answer from retrieved documents."""
    context = "\n\n".join([doc["text"] for doc in documents])
    prompt = f"Answer the question based on the context:\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return {"answer": response.choices[0].message.content, "docs_used": len(documents)}
    except Exception as e:
        return {"answer": None, "docs_used": 0, "error": str(e)}

