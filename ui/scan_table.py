import streamlit as st
import pandas as pd

def display_nmap_results(scan_data):
    # Ensure scan_data is a list even if a single dict is passed
    if isinstance(scan_data, dict):
        scan_data = [scan_data]
        
    if not scan_data:
        st.info("No scan data to display.")
        return

    flattened_rows = []

    for host_entry in scan_data:
        # Extra safety check: skip if host_entry isn't a dict
        if not isinstance(host_entry, dict):
            continue
            
        ip = host_entry.get("host", "N/A")
        hostname = host_entry.get("hostname", "N/A")
        mac = host_entry.get("mac", "N/A")
        vendor = host_entry.get("vendor", "N/A")
        
        protocols = host_entry.get("protocols", [])
        if not protocols:
            flattened_rows.append({
                "IP Address": ip, "Hostname": hostname, "MAC": mac, "Vendor": vendor,
                "Port": "N/A", "Service": "N/A", "Product": "N/A", "Version": "N/A", "State": host_entry.get("state", "up")
            })
            continue

        for proto in protocols:
            proto_name = proto.get("protocol", "tcp")
            for port in proto.get("ports", []):
                flattened_rows.append({
                    "IP Address": ip,
                    "Hostname": hostname,
                    "MAC": mac,
                    "Vendor": vendor,
                    "Port": f"{port.get('port')}/{proto_name}",
                    "Service": port.get("name", "unknown"),
                    "Product": port.get("product", "N/A"),
                    "Version": port.get("version", "N/A"),
                    "State": port.get("state", "open")
                })

    df = pd.DataFrame(flattened_rows)

    st.subheader("🔍 Network Discovery Results")
    
    col1, col2 = st.columns(2)
    col1.metric("Hosts Up", len(scan_data))
    col2.metric("Open Ports", len(df[df["Port"] != "N/A"]))

    st.dataframe(df, use_container_width=True, hide_index=True)