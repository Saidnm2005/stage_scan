import streamlit as st
import pandas as pd
def display_vulnerability_table(json_data):
    all_cves = []
    
    # 1. Check if the data is a list or a dictionary
    if isinstance(json_data, list):
        # If it's a direct list of CVEs
        cve_list_to_process = json_data
    elif isinstance(json_data, dict):
        # If it's a dictionary keyed by product (e.g., {"jquery:1.11.3": [...]})
        # We take all the lists and combine them
        cve_list_to_process = []
        for product_key, cve_list in json_data.items():
            cve_list_to_process.extend(cve_list)
    else:
        st.error("Unexpected data format received from scanner.")
        return

    # 2. Flatten the list
    for cve in cve_list_to_process:
        row = {
            "CVE ID": cve.get("id", {}).get("value", "N/A"),
            "Severity": cve.get("severity", "N/A"),
            "CVSS": cve.get("cvssScore", "N/A"),
            "Published": cve.get("published", "N/A"),
            "Description": cve.get("description", "No description available."),
            "URL": cve.get("id", {}).get("url", "")
        }
        all_cves.append(row)

    # 3. Create DataFrame and display
    if all_cves:
        df = pd.DataFrame(all_cves)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No vulnerabilities found.")