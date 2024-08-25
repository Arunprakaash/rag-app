import streamlit as st
from utils import (
    add_custom_css, footer, login, query_knowledge_base,
)

# Initialize session state
if 'current_tenant_id' not in st.session_state:
    st.session_state.current_tenant_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False


def main():
    st.set_page_config(layout="wide", page_title="user")
    add_custom_css()

    if not st.session_state.is_authenticated:
        login_fragment()
    else:
        chat_interface_fragment()

    footer()


@st.fragment
def login_fragment():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            if login(username, password):
                st.session_state.is_authenticated = True


@st.fragment
def chat_interface_fragment():
    st.caption("Chat Interface")
    messages = st.container(height=650, border=False)

    # Display chat history
    for message in st.session_state.chat_history:
        messages.chat_message(message["role"]).write(message["content"])

    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history and display it
        st.session_state.chat_history.append({"role": "human", "content": prompt})
        messages.chat_message("human").write(prompt)

        # Query the index
        with st.toast("Thinking..."):
            response = {"response": query_knowledge_base(st.session_state.current_tenant_id, prompt)}

        if "error" not in response:
            # Add AI response to chat history and display it
            ai_message = response.get("response", "Sorry, I couldn't generate a response.")
            st.session_state.chat_history.append({"role": "ai", "content": ai_message})
            messages.chat_message("ai").write(ai_message)
        else:
            error_message = f"Error: {response['error']}"
            st.session_state.chat_history.append({"role": "ai", "content": error_message})
            messages.chat_message("ai").write(error_message)


if __name__ == "__main__":
    main()
