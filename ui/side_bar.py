import streamlit as st
def render_sidebar():
    st.sidebar.title("Vulnerability Scanner")
    st.sidebar.markdown("Use this sidebar to navigate through the app.")
    st.sidebar.markdown("Select a tool from the dropdown below:")
    tool = st.sidebar.selectbox("Select Tool", ["CVE Matching", "full scan with vuln","full scan with services"])
    return tool
   
