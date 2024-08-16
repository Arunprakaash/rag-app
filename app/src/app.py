from typing import Text

import streamlit as st

from components import knowledge_fragment, chat_interface_fragment
from utils import add_custom_css, footer, get_tenants, validate_tenant_name, create_tenant, upload_knowledge_base, delete_tenant


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

    tenants = get_tenants()

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

if __name__ == "__main__":
    main()
