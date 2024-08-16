from typing import Text

import streamlit as st

from utils import add_custom_css, footer, validate_tenant_name, create_tenant, upload_knowledge_base, delete_tenant


# Initialize session state
if 'current_tenant' not in st.session_state:
    st.session_state.current_tenant = None
if 'tenant_files' not in st.session_state:
    st.session_state.tenant_files = None


def set_current_tenant(tenant: Text):
    st.session_state.current_tenant = tenant


def main():
    st.set_page_config(layout="wide", page_title="rag-app")
    
    add_custom_css()

    tenants = ["paypal", "dummy"] # fetch_tenants()

    with st.sidebar:
        with st.popover("Create Tenant", use_container_width=True):
            name = validate_tenant_name(st.text_input("Tenant Name: "))
            if name:
                st.info(f"Tenant name will be created as: {name}")
                st.button("**Create Tenant**", use_container_width=True, type='primary', on_click=create_tenant,
                          args=[name])

        st.caption("**Available tenants**")
        if st.session_state.current_tenant is None and tenants:
            set_current_tenant(tenants[0])

        for tenant in tenants:
            st.button(tenant, use_container_width=True, on_click=set_current_tenant,
                      args=[tenant])

    if not tenants:
        st.warning("Please select or create a tenant to continue.")
        return

    left_column, right_column = st.columns(2)

    with left_column:
        st.caption(f"Tenant: **{st.session_state.current_tenant}**")

        with st.container(height=620, border=False):
            with st.expander("**Knowledge**", expanded=True):
                knowledge_fragment()

    with right_column:
        st.caption("chat interface")
        chat_interface_fragment()

    st.button(f"Delete {st.session_state.current_tenant}", type='primary', on_click=delete_tenant,
              args=[st.session_state.current_tenant])
    st.caption(
        "**Warning:** Deleting a tenant is irreversible and will remove all associated data. Proceed with caution.")
    footer()

@st.fragment
def knowledge_fragment():
    st.subheader("Knowledge Management", anchor=False)
    st.caption("Manage your own data to chat with.")

    if st.session_state.tenant_files:
        st.write("Existing files:")
        for file in st.session_state.tenant_files:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(file)
            with col2:
                # st.button("Delete", type='primary', key=file, on_click=delete_file,
                #           args=[file, st.session_state.current_tenant])
                pass

    upload_files = st.file_uploader("Upload new knowledge base files",
                                    type=["pdf"],
                                    accept_multiple_files=True)

    if upload_files:
        st.button("**Update knowledge config**", type='primary', on_click=upload_knowledge_base,
                  args=[st.session_state.current_tenant, upload_files])


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


if __name__ == "__main__":
    main()
