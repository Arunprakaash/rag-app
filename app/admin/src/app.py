import streamlit as st
from utils import (
    add_custom_css, footer, get_tenants, validate_tenant_name, create_tenant,
    upload_knowledge_base, delete_tenant, set_current_tenant, query_knowledge_base,
    delete_tenant_files, get_tenant_files
)

# Initialize session state
if 'current_tenant' not in st.session_state:
    st.session_state.current_tenant = None
if 'current_tenant_id' not in st.session_state:
    st.session_state.current_tenant_id = None
if 'tenant_files' not in st.session_state:
    st.session_state.tenant_files = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def refresh_tenant_data():
    st.session_state.tenants_data = get_tenants()
    if st.session_state.current_tenant_id:
        st.session_state.tenant_files = get_tenant_files(st.session_state.current_tenant_id)


def handle_create_tenant(name):
    create_tenant(name)
    refresh_tenant_data()


def handle_delete_tenant(tenant_id):
    delete_tenant(tenant_id)
    st.session_state.current_tenant = None
    st.session_state.current_tenant_id = None
    refresh_tenant_data()


def handle_upload_files(tenant_id, files):
    upload_knowledge_base(tenant_id, files)
    refresh_tenant_data()


def handle_delete_file(tenant_id, file_id):
    delete_tenant_files(tenant_id, file_id)
    refresh_tenant_data()


def main():
    st.set_page_config(layout="wide", page_title="admin")
    add_custom_css()

    if 'tenants_data' not in st.session_state:
        refresh_tenant_data()

    with st.sidebar:
        with st.popover("Create Tenant", use_container_width=True):
            name = validate_tenant_name(st.text_input("Tenant Name: "))
            if name:
                st.info(f"Tenant name will be created as: {name}")
                st.button("**Create Tenant**", use_container_width=True, type='primary', on_click=handle_create_tenant,
                          args=[name])

        st.caption("**Available tenants**")
        if st.session_state.current_tenant is None and st.session_state.tenants_data:
            set_current_tenant(st.session_state.tenants_data[0]['name'], st.session_state.tenants_data[0]['id'])

        for tenant in st.session_state.tenants_data:
            st.button(tenant['name'], use_container_width=True, on_click=set_current_tenant,
                      args=[tenant['name'], tenant['id']])

    if not st.session_state.tenants_data:
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

    st.button(f"Delete {st.session_state.current_tenant}", type='primary', on_click=handle_delete_tenant,
              args=[st.session_state.current_tenant_id])
    st.caption(
        "**Warning:** Deleting a tenant is irreversible and will remove all associated data. Proceed with caution.")
    footer()


@st.fragment
def chat_interface_fragment():
    messages = st.container(height=565)

    # Display chat history
    for message in st.session_state.chat_history:
        messages.chat_message(name=message["role"]).write(message["content"])

    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history and display it
        st.session_state.chat_history.append({"role": "human", "content": prompt})
        messages.chat_message(name="human").write(prompt)

        # Query the index
        with st.toast("Thinking..."):
            response = {"response": query_knowledge_base(st.session_state.current_tenant_id, prompt)}

        if "error" not in response:
            # Add AI response to chat history and display it
            ai_message = response.get("response", "Sorry, I couldn't generate a response.")
            st.session_state.chat_history.append({"role": "ai", "content": ai_message})
            messages.chat_message(name="ai").write(ai_message)
        else:
            error_message = f"Error: {response['error']}"
            st.session_state.chat_history.append({"role": "ai", "content": error_message})
            messages.chat_message(name="ai").write(error_message)


@st.fragment
def knowledge_fragment():
    st.subheader("Knowledge Management", anchor=False)
    st.caption("Manage your own data to chat with.")

    if st.session_state.tenant_files:
        st.write("Existing files:")
        for file in st.session_state.tenant_files:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(file['filename'])
            with col2:
                st.button("Delete", type='primary', key=file, on_click=handle_delete_file,
                          args=[st.session_state.current_tenant_id, file["id"]])

    upload_files = st.file_uploader("Upload new knowledge base files",
                                    type=["pdf"],
                                    accept_multiple_files=True, )

    if upload_files:
        st.button("**Update knowledge config**", type='primary', on_click=handle_upload_files,
                  args=[st.session_state.current_tenant_id, upload_files])


if __name__ == "__main__":
    main()
