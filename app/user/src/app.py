import streamlit as st
from streamlit_authenticator import Authenticate

from utils import add_custom_css, footer, query_knowledge_base, load_config, get_tenant_id


@st.cache_data
def get_cached_config():
    return load_config()


config = get_cached_config()

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)


def initialize_state():
    if 'user' not in st.session_state:
        st.session_state.user = {"id": None, 'chat_history': []}


def main():
    add_custom_css()
    initialize_state()
    name, authentication_status, username = authenticator.login(captcha=True)

    if authentication_status:
        st.session_state.user.update({'id': get_tenant_id(username)})
        chat_interface_fragment()
        footer(authenticator)
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    else:
        st.warning('Please enter your username and password')


@st.fragment
def chat_interface_fragment():
    messages = st.container(height=550, border=False)

    messages.chat_message("ai").write(
        "Interact with your documents using AI!")

    for message in st.session_state.user['chat_history']:
        messages.chat_message(message["role"]).write(message["content"])

    if prompt := st.chat_input("Ask a question about your documents"):
        st.session_state.user['chat_history'].append({"role": "human", "content": prompt})
        messages.chat_message("human").write(prompt)

        with st.toast("Thinking..."):
            response = {"response": query_knowledge_base(st.session_state.user['id'], prompt)}

        if "error" not in response:
            ai_message = response.get("response", "Sorry, I couldn't generate a response.")
            st.session_state.user['chat_history'].append({"role": "ai", "content": ai_message})
            messages.chat_message("ai").write(ai_message)
        else:
            error_message = f"Error: {response['error']}"
            st.session_state.user['chat_history'].append({"role": "ai", "content": error_message})
            messages.chat_message("ai").write(error_message)


if __name__ == "__main__":
    main()
