import re
import os
from typing import Text
import requests

import streamlit as st

API_URL = os.getenv("API_URL")

def create_tenant(tenant_name: Text):
    response = requests.post(f"{API_URL}/tenants", json={"name": tenant_name})
    st.write(response.json())

def delete_tenant(tenant_name: Text):
    response = requests.delete(f"{API_URL}/tenants/{tenant_name}")
    st.write(response.json())

def get_tenants():
    return requests.get(f"{API_URL}/tenants").json()


def upload_knowledge_base(tenant_name: Text, uploaded_files):
     for file in uploaded_files:
        files = {"file": file}
        response = requests.post(f"{API_URL}/upload/{tenant_name}", files=files)
        st.write(response.json())


# Utility functions remain unchanged
def add_custom_css():
    st.markdown("""
            <style>

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
