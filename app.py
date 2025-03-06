import streamlit as st
import sqlite3
from datetime import datetime
from ollama import Client
import database

# Initialize Ollama client
client = Client(host='http://localhost:11434')

def get_ai_response(prompt, context=None):
    """Get response from Ollama's Mistral model with context"""
    messages = []
    
    if context:
        messages.append({
            'role': 'system',
            'content': f"Previous relevant interaction: {context}"
        })
    
    messages.append({
        'role': 'user',
        'content': prompt
    })
    
    response = client.chat(model='mistral', messages=messages)
    return response['message']['content']

def save_feedback(message_id, is_positive):
    """Save user feedback to database"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_history 
        SET feedback = ? 
        WHERE id = ?
    """, (1 if is_positive else 0, message_id))
    conn.commit()
    conn.close()

def save_curated_response(message_id, curated_response):
    """Save a curated response for a negative feedback"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_history 
        SET curated_response = ? 
        WHERE id = ?
    """, (curated_response, message_id))
    conn.commit()
    conn.close()

def main():
    st.title("AI Chat Assistant")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'awaiting_curation' not in st.session_state:
        st.session_state.awaiting_curation = None

    # Handle curation if needed
    if st.session_state.awaiting_curation:
        st.info("This response received negative feedback. Please provide a better response:")
        message_id, question = st.session_state.awaiting_curation
        curated_response = st.text_area("Curated response:", key="curation_input")
        if st.button("Submit Curated Response"):
            save_curated_response(message_id, curated_response)
            st.session_state.awaiting_curation = None
            st.success("Curated response saved!")
            st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                col1, col2 = st.columns([1, 15])
                with col1:
                    if st.button("👍", key=f"up_{message['id']}"):
                        save_feedback(message['id'], True)
                        st.toast("Thanks for your feedback!")
                    if st.button("👎", key=f"down_{message['id']}"):
                        save_feedback(message['id'], False)
                        st.session_state.awaiting_curation = (message['id'], message['content'])
                        st.toast("Thanks for your feedback! Please provide a better response.")
                        st.rerun()

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check for similar previous questions
        context = database.find_similar_question(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if context:
                    st.info("Using previous successful interaction as context")
                response = get_ai_response(prompt, context)
                st.markdown(response)
                
                # Add feedback buttons immediately after response
                col1, col2 = st.columns([1, 15])
                with col1:
                    # Save to database first to get message_id
                    conn = database.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO chat_history (timestamp, user_message, ai_response)
                        VALUES (?, ?, ?)
                    """, (datetime.now(), prompt, response))
                    message_id = cursor.lastrowid
                    conn.commit()
                    conn.close()

                    if st.button("👍", key=f"up_{message_id}"):
                        save_feedback(message_id, True)
                        st.toast("Thanks for your feedback!")
                    if st.button("👎", key=f"down_{message_id}"):
                        save_feedback(message_id, False)
                        st.session_state.awaiting_curation = (message_id, prompt)
                        st.toast("Thanks for your feedback! Please provide a better response.")
                        st.rerun()

        # Add assistant message to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "id": message_id
        })

if __name__ == "__main__":
    database.init_db()
    main() 