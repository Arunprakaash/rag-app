import streamlit as st

from utils import (
    add_custom_css, footer, login, query_knowledge_base
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


def login_fragment():
    with st.form("login_form", clear_on_submit=True, border=False):
        st.markdown(
            """
            <div style="text-align: center;">
                <h5>Please enter your credentials to login</h5>
            </div>
            """,
            unsafe_allow_html=True
        )
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button = st.form_submit_button("Login", type="primary")
        if login_button:
            if login(username, password):
                st.rerun()


@st.fragment
def chat_interface_fragment():
    st.caption("Interact with your documents using AI!")

    messages = st.container(height=600, border=False)

    messages.chat_message("ai").write(
        "Hello! I am an AI developed by RockerFrog. Start chatting with your documents now!")

    for message in st.session_state.chat_history:
        messages.chat_message(message["role"]).write(message["content"])

    if prompt := st.chat_input("Ask a question about your documents"):
        st.session_state.chat_history.append({"role": "human", "content": prompt})
        messages.chat_message("human").write(prompt)

        with st.toast("Thinking..."):
            response = {"response": query_knowledge_base(st.session_state.current_tenant_id, prompt)}

        if "error" not in response:
            ai_message = response.get("response", "Sorry, I couldn't generate a response.")
            st.session_state.chat_history.append({"role": "ai", "content": ai_message})
            messages.chat_message("ai").write(ai_message)
        else:
            error_message = f"Error: {response['error']}"
            st.session_state.chat_history.append({"role": "ai", "content": error_message})
            messages.chat_message("ai").write(error_message)


if __name__ == "__main__":
    main()
