import streamlit as st

@st.fragment
def chat_interface_fragment():
    messages = st.container(height=565)

    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        messages.chat_message(name=message["role"]).write(message["content"])

    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history and display it
        st.session_state.chat_history.append({"role": "human", "content": prompt})
        messages.chat_message(name="human").write(prompt)

        # Query the index
        with st.toast("Thinking..."):
            response =  {"response": "hi!"}# query_index(st.session_state.current_tenant, prompt)

        if "error" not in response:
            # Add AI response to chat history and display it
            ai_message = response.get("response", "Sorry, I couldn't generate a response.")
            st.session_state.chat_history.append({"role": "ai", "content": ai_message})
            messages.chat_message(name="ai").write(ai_message)
        else:
            error_message = f"Error: {response['error']}"
            st.session_state.chat_history.append({"role": "ai", "content": error_message})
            messages.chat_message(name="ai").write(error_message)