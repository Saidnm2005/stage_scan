import streamlit as st
import pandas as pd
from nmap_scan import discover_network, scan_host_auto
from ui.scan_table import display_nmap_results
from CVE_Matching import run_vuln_scan
import APi.servicesAPi as Servapi
import APi.AssetsAPi as Assetapi
import APi.vulnAPi as Vulnapi

# --- CONSTANTS ---
HEADER_HTML = """
    <div style="background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
                padding: 1.5rem; border-radius: 10px;
                border-left: 5px solid #00d4aa; margin-bottom: 2rem;">
        <h1 style="color: #00d4aa; margin: 0;">🛡️ Advanced Vulnerability Audit</h1>
        <p style="color: #b8c5d6; margin: 0.5rem 0 0 0;">
            Network Discovery, Service Mapping, and CVE Correlation
        </p>
    </div>
"""

# --- HELPER FUNCTIONS ---

def register_asset(ip, host_details):
    """Registers the host in the Asset database."""
    try:
        asset_payload = {
            "ip_address": ip,
            "mac_address": host_details.get("mac"),
            "hostname": host_details.get("hostname", "Unknown"),
            "vendor": host_details.get("vendor", "Unknown"),
            "status": "active"
        }
        resp = Assetapi.add_asset(asset_payload)
        return resp['data'].get('id') if isinstance(resp, dict) and 'data' in resp else None
    except Exception as e:
        st.error(f"Asset DB Error: {e}")
        return None

def process_vulnerabilities(vulns, name, version):
    """Normalizes and displays vulnerability data."""
    all_vulns = []
    if isinstance(vulns, dict):
        for _, v_list in vulns.items():
            if isinstance(v_list, list): all_vulns.extend(v_list)
    elif isinstance(vulns, list):
        all_vulns = vulns

    if not all_vulns:
        st.success(f"✅ {name} {version}: No vulnerabilities")
        return []

    st.warning(f"⚠️ {name} {version}: {len(all_vulns)} CVEs")
    df = pd.DataFrame(all_vulns)
    if "cvssScore" in df.columns:
        df["cvssScore"] = pd.to_numeric(df["cvssScore"], errors="coerce")
    
    cols = [c for c in ['id', 'cvssScore', 'description'] if c in df.columns]
    st.dataframe(df[cols], use_container_width=True)
    return all_vulns

def save_vulnerability_to_db(v):
    """Handles the API call to save a single CVE."""
    try:
        cve_id = v.get('id').get('value') if isinstance(v.get('id'), dict) else v.get('id')
        
        try:
            cvss = float(v.get('cvssScore'))
        except (TypeError, ValueError):
            cvss = None

        payload = {
            "cve_id": cve_id,
            "description": v.get('description'),
            "severity": v.get('severity') if v.get('severity') not in ["N/A", "", None] else None,
            "cvss_score": cvss,
            "published_date": v.get('published'),
        }
        
        if not Vulnapi.add_vulnerability(payload):
            st.error(f"❌ Insert failed: {cve_id}")
    except Exception as e:
        st.error(f"DB Insert error: {e}")

# --- MAIN APP ---

def load_vulnerability_scan():
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Scan Settings")
        ip_range = st.text_input("Target Network", "10.114.121.0/24")
        start_audit = st.button("🚀 Start Full Audit", type="primary")

    if not start_audit:
        return

    # PHASE 1: DISCOVERY
    with st.status("🔍 Phase 1: Discovering active hosts...", expanded=True) as status:
        network_results = discover_network(ip_range)
        active_hosts = [h for h in network_results if h.get("state") == "up"] if network_results else []
        
        if not active_hosts:
            st.error("No active hosts found.")
            return
        status.update(label=f"✅ Found {len(active_hosts)} active devices.", state="complete")

    progress = st.progress(0)

    # PHASE 2: SCANNING
    for idx, host in enumerate(active_hosts):
        ip = host["ip"]
        st.markdown(f"### 🖥️ Host: `{ip}`")
        progress.progress((idx + 1) / len(active_hosts))

        with st.spinner(f"Scanning {ip}..."):
            raw_data = scan_host_auto(ip)
            host_details = raw_data[0] if isinstance(raw_data, list) and raw_data else raw_data
            
        if not host_details or not isinstance(host_details, dict):
            st.warning(f"Skipping {ip}: No data returned.")
            continue

        asset_id = register_asset(ip, host_details)

        with st.expander(f"Details for {ip}", expanded=True):
            display_nmap_results(host_details)
            protocols = host_details.get('protocols', [])

            if not protocols:
                st.info("No services found.")
                continue

            st.markdown("#### 🔍 Vulnerability Matching")
            for proto in protocols:
                for port_info in proto.get('ports', []):
                    name = port_info.get('product', '').strip()
                    version = port_info.get('version', '').strip()
                    
                    if not (name and version):
                        continue

                    # Scan & Display Vulns
                    with st.spinner(f"Checking {name} {version}..."):
                        vulns = run_vuln_scan(name, version)
                        all_vulns = process_vulnerabilities(vulns, name, version)

                    # Save Service (if asset exists)
                    if asset_id:
                        service_payload = {
                            "asset_id": asset_id,
                            "port": port_info.get('port'),
                            "protocol": proto.get('protocol', 'tcp'),
                            "service_name": name,
                            "version": version
                        }
                        Servapi.add_service(service_payload)

                    # Save Vulns to DB
                    for v in all_vulns:
                        save_vulnerability_to_db(v)

    st.success("✅ Audit completed")
    st.balloons()