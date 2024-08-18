import streamlit as st

from utils import upload_knowledge_base, delete_tenant_files


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
                st.button("Delete", type='primary', key=file, on_click=delete_tenant_files,
                          args=[st.session_state.current_tenant_id, file["id"]])
                pass

    upload_files = st.file_uploader("Upload new knowledge base files",
                                    type=["pdf"],
                                    accept_multiple_files=True)

    if upload_files:
        st.button("**Update knowledge config**", type='primary', on_click=upload_knowledge_base,
                  args=[st.session_state.current_tenant_id, upload_files])
