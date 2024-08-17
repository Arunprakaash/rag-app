import re
import os
from typing import Text, List, Optional, Any
import requests
import streamlit as st

API_URL = 'http://localhost:8000'  # os.getenv("API_URL")


def set_current_tenant(tenant_name: Text, tenant_id: Text) -> None:
    st.session_state.current_tenant = tenant_name
    st.session_state.current_tenant_id = tenant_id


def create_tenant(tenant_name: Text) -> None:
    try:
        response = requests.post(f"{API_URL}/tenants", json={"name": tenant_name})
        response.raise_for_status()
        st.toast("Tenant created successfully!")
        set_current_tenant(tenant_name, response.json()["id"])
    except requests.exceptions.RequestException as e:
        st.toast(f"Error creating tenant: {e}", icon="🚨")


def delete_tenant(tenant_id: Text) -> None:
    try:
        response = requests.delete(f"{API_URL}/tenants/{tenant_id}")
        response.raise_for_status()
        st.toast("Tenant deleted successfully!")
    except requests.exceptions.RequestException as e:
        st.toast(f"Error deleting tenant: {e}", icon="🚨")


def get_tenants() -> Optional[Any]:
    try:
        response = requests.get(f"{API_URL}/tenants")
        response.raise_for_status()
        tenants_data = response.json()
        return tenants_data if tenants_data else []
    except requests.exceptions.RequestException as e:
        st.toast(f"Error retrieving tenants: {e}", icon="🚨")
        return None


def upload_knowledge_base(tenant_id: Text, uploaded_files: List[Any]) -> None:
    for file in uploaded_files:
        try:
            files = {"file": file}
            response = requests.post(f"{API_URL}/upload/{tenant_id}", files=files)
            response.raise_for_status()
            st.toast(f"File {file.name} uploaded successfully.")
        except requests.exceptions.RequestException as e:
            st.toast(f"Error uploading file {file.name}: {e}", icon="🚨")
        except Exception as e:
            st.toast(f"Unexpected error: {e}", icon="🚨")


def add_custom_css():
    st.markdown("""
            <style>
            /* Add your custom CSS here */
            </style>
        """, unsafe_allow_html=True)


def footer():
    st.caption("---------")
    st.markdown(
        """
        <div style="text-align: center;">
            <p>Questions, feature requests, or found a bug? Open an issue on
                <a href="https://github.com/Arunprakaash/rag-app/issues/new" target="_blank">GitHub</a>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def validate_tenant_name(name: Text) -> Text:
    name = name.lower().replace(' ', '_')
    return re.sub(r'[^a-z0-9_]', '', name)
