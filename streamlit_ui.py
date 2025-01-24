import streamlit as st
import os
import json
from typing import List
import asyncio
from openai import AsyncOpenAI
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI and Supabase clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

async def get_embedding(text: str) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536

async def search_docs(query: str, match_count: int = 5):
    """Search documentation using embeddings."""
    try:
        query_embedding = await get_embedding(query)
        
        # Search in Supabase
        response = supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': match_count,
                'filter': {'source': 'ultravox_docs'}
            }
        ).execute()
        
        return response.data
    except Exception as e:
        print(f"Error searching docs: {e}")
        return []

async def get_ai_response(query: str, context: str) -> str:
    """Get AI response using context."""
    try:
        response = await openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that answers questions about Ultravox documentation. Use the provided context to answer questions accurately and concisely."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return f"Error: {str(e)}"

async def process_query(query: str):
    """Process user query and return AI response."""
    # Search relevant docs
    results = await search_docs(query)
    
    if not results:
        return "I couldn't find any relevant information in the documentation."
    
    # Prepare context from search results
    context = "\n\n".join([
        f"Title: {result['title']}\nContent: {result['content']}"
        for result in results
    ])
    
    # Get AI response
    return await get_ai_response(query, context)

def main():
    st.title("Ultravox Documentation Assistant")
    st.write("Ask any question about Ultravox documentation.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if query := st.chat_input("Ask a question about Ultravox"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})

        # Display assistant response
        with st.chat_message("assistant"):
            response = asyncio.run(process_query(query))
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

