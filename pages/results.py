import streamlit as st
import pandas as pd
import APi.scaniAPi as scaniAPI
from APi.AssetsAPi import get_asset_details
from ui.navigation import render_navigation
from ui.notification import render_notifications
render_notifications()

# Must be first
st.set_page_config(page_title="VulnScan | Scan Results", page_icon="📊", layout="wide")


# Professional Cyber-Security CSS
st.markdown("""
<style>
/* ==========================================================================
   CYBER THEME - Scan Results Page
   ========================================================================== */

/* Main Theme */
.stApp {
    background: radial-gradient(ellipse at 20% 30%, #0a0f1a, #020409);
}

.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
}

/* Cyber Header */
.cyber-header {
    font-family: 'Courier New', monospace;
    background: linear-gradient(135deg, #f3f4f6, #9ca3af);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    border-left: 4px solid #3b82f6;
    padding-left: 20px;
    margin-bottom: 25px;
    letter-spacing: 1px;
}

/* Grid Card Styling */
.scan-card {
    background: linear-gradient(135deg, #0f172a, #0a0f1a);
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 20px;
    transition: all 0.3s ease;
    margin-bottom: 20px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.scan-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, #60a5fa, transparent);
    transform: translateX(-100%);
    transition: transform 0.5s ease;
}

.scan-card:hover::before {
    transform: translateX(100%);
}

.scan-card:hover {
    border-color: #3b82f6;
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
}

/* Severity Badges */
.severity-critical {
    color: #ef4444;
    font-weight: bold;
    background: rgba(239, 68, 68, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
}

.severity-high {
    color: #f97316;
    font-weight: bold;
    background: rgba(249, 115, 22, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
}

.severity-medium {
    color: #f59e0b;
    font-weight: bold;
    background: rgba(245, 158, 11, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
}

.severity-low {
    color: #10b981;
    font-weight: bold;
    background: rgba(16, 185, 129, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
}

/* CVSS Score Circle */
.cvss-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    margin: 10px auto;
}

.cvss-critical {
    background: rgba(239, 68, 68, 0.15);
    border: 2px solid #ef4444;
    color: #ef4444;
}

.cvss-high {
    background: rgba(249, 115, 22, 0.15);
    border: 2px solid #f97316;
    color: #f97316;
}

.cvss-medium {
    background: rgba(245, 158, 11, 0.15);
    border: 2px solid #f59e0b;
    color: #f59e0b;
}

.cvss-low {
    background: rgba(16, 185, 129, 0.15);
    border: 2px solid #10b981;
    color: #10b981;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem;
    transition: all 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #9ca3af !important;
    font-family: 'Courier New', monospace !important;
}

[data-testid="stMetricValue"] {
    color: #f3f4f6 !important;
    font-family: 'Courier New', monospace !important;
    font-weight: 600 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background-color: #0f172a;
    border-radius: 8px;
    padding: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 0.4rem 1rem;
    font-family: 'Courier New', monospace;
    color: #9ca3af;
}

.stTabs [aria-selected="true"] {
    background-color: #3b82f6;
    color: white;
}

/* Expanders */
.streamlit-expanderHeader {
    background: #0f172a !important;
    border-radius: 8px !important;
    color: #9ca3af !important;
    border: 1px solid #1e293b !important;
    font-family: 'Courier New', monospace !important;
}

.streamlit-expanderHeader:hover {
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #0f172a, #0a0f1a);
    color: #9ca3af;
    border: 1px solid #1e293b;
    border-radius: 8px;
    transition: all 0.2s ease;
    font-family: 'Courier New', monospace;
}

div.stButton > button:hover {
    background: rgba(59, 130, 246, 0.1);
    border-color: #3b82f6;
    color: #3b82f6;
    transform: translateY(-1px);
}

/* Code blocks */
code {
    background: #0f172a !important;
    color: #60a5fa !important;
    padding: 0.2rem 0.5rem !important;
    border-radius: 6px !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.85rem !important;
    border: 1px solid #1e293b;
}

/* Info/Warning boxes */
.stAlert {
    border-radius: 8px !important;
    font-family: 'Courier New', monospace !important;
}

/* Container borders */
.custom-container {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    transition: all 0.2s ease;
}

.custom-container:hover {
    border-color: #3b82f6;
}

/* Divider */
hr {
    border-color: #1e293b !important;
    margin: 1.5rem 0 !important;
}
</style>
""", unsafe_allow_html=True)


def details_page(scan_id):
    st.markdown(f"<h1 class='cyber-header'>🔍 AUDIT ANALYSIS: SCAN #{scan_id}</h1>", unsafe_allow_html=True)
    
    # Summary Dashboard for the Scan
    results = scaniAPI.get_scan_results(scan_id)
    scan_data = results.get("data", [])

    if not scan_data:
        st.warning("No host data associated with this scan session.")
        return

    # Tabs for modern layout
    tab_summary, tab_assets, tab_vulns = st.tabs(["📊 Executive Summary", "🖥️ Detected Hosts", "⚠️ Vulnerability Details"])

    with tab_summary:
        # Calculate totals
        total_hosts = len(scan_data)
        all_vulns = []
        for item in scan_data:
            d = get_asset_details(item.get('asset', {}).get('id'))
            if d.get('data'):
                for svc in d['data'].get('services', []):
                    all_vulns.extend(svc.get('vulnerabilities', []))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Assets Scanned", total_hosts)
        col2.metric("Total Vulnerabilities", len(all_vulns))
        col3.metric("Critical Risks", len([v for v in all_vulns if v.get('severity') == 'CRITICAL']))

    with tab_assets:
        # (Keep your existing asset list logic here)
        pass

    with tab_vulns:
        st.markdown("### 📋 Detailed Vulnerability Log")
        
        # Displaying rich details for every vulnerability found in the scan
        for v in all_vulns:
            severity = v.get('severity', 'UNKNOWN').upper()
            sev_color = "#ef4444" if severity == "CRITICAL" else "#f97316" if severity == "HIGH" else "#f59e0b"
            
            with st.expander(f"📌 {v.get('cve_id')} - {severity}", expanded=(severity == "CRITICAL")):
                v_col1, v_col2 = st.columns([2, 1])
                
                with v_col1:
                    st.markdown(f"#### Description")
                    st.write(v.get('description', 'No description provided by NVD.'))
                    
                    st.markdown("#### 🛠️ Remediation Guidance")
                    if severity in ["CRITICAL", "HIGH"]:
                        st.error("Priority: Patch immediately. Check vendor for security advisories.")
                    else:
                        st.info("Priority: Plan for next maintenance window.")

                with v_col2:
                    st.markdown(f"""
                        <div style="background: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid {sev_color};">
                            <p style="margin:0; font-size: 0.8rem; color: #9ca3af;">CVSS BASE SCORE</p>
                            <h2 style="margin:0; color: {sev_color};">{v.get('cvss_score', 'N/A')}</h2>
                            <hr style="border-color: #334155; margin: 10px 0;">
                            <p style="margin:0; font-size: 0.7rem; color: #9ca3af;">VECTOR STRING</p>
                            <code style="font-size: 0.7rem; word-wrap: break-word;">{v.get('vector_string', 'N/A')}</code>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.caption(f"Published: {v.get('published_date', 'N/A')[:10]}")

def asset_details_page(asset_id, scan_id):
    # (Existing Logic...)
    # In the vulnerabilities loop, add the "Technical Breakdown"
    asset_details = get_asset_details(asset_id)
    asset_data = asset_details.get("data")
    
    st.markdown(f"<h2 class='cyber-header'>HOST SECURITY PROFILE: {asset_data.get('ip_address')}</h2>", unsafe_allow_html=True)
    
    for svc in asset_data.get('services', []):
        if svc.get('vulnerabilities'):
            st.markdown(f"### 🛡️ Vulnerabilities on Port {svc.get('port')}")
            for v in svc.get('vulnerabilities'):
                with st.container(border=True):
                    # Metric style layout
                    c1, c2, c3 = st.columns([1, 3, 1])
                    c1.metric("CVSS", v.get('cvss_score'), delta_color="inverse")
                    c2.markdown(f"**{v.get('cve_id')}**")
                    c2.caption(v.get('description')[:150] + "...")
                    if c3.button("NVD Ref", key=f"link_{v.get('id')}"):
                        st.write(f"Redirecting to: https://nvd.nist.gov/vuln/detail/{v.get('cve_id')}")

# ... (rest of the main logic)

def main_page():
    st.markdown("<h1 class='cyber-header'>📊 SCAN REPOSITORY</h1>", unsafe_allow_html=True)
    
    results = scaniAPI.get_scans()
    
    if results.get("error"):
        st.error("🚨 API Connection Error: Could not retrieve scan logs.")
    elif not results or not results.get("data"):
        st.info("📡 No scan data found. Initialize a new network audit to see results.")
    else:
        # Search & Sort Bar
        s_col1, s_col2 = st.columns([3, 1])
        with s_col1:
            search_term = st.text_input("🔍 Search Scan ID or Name", placeholder="e.g. Subnet_Scan_01")
        with s_col2:
            sort_by = st.selectbox("Sort Order", ["Latest First", "Oldest First", "Asset Count"])
        
        scans = results.get("data")
        
        # Filtering logic
        if search_term:
            scans = [s for s in scans if search_term.lower() in str(s.get('name', '')).lower() or search_term in str(s.get('id'))]
        
        # Grid Display
        cols_per_row = 3
        for i in range(0, len(scans), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col in enumerate(row_cols):
                if i + j < len(scans):
                    scan = scans[i + j]
                    with col:
    # 1. Corrected the .get() syntax and the status comparison
                        status = scan.get('status', 'unknown')
                        
                        # 2. Used valid CSS 'color' property
                        status_color = "#10b981" if status == 'completed' else "#ef4444"
                        
                        # 3. Applied the style to the markdown
                        st.markdown(f"""
                            <div class="scan-card" style="border-left: 4px solid {status_color};">
                                <p style='color: #64748b; font-size: 0.8rem; margin-bottom: 5px;'>ID: #{scan.get('id')}</p>
                                <h3 style='margin-top: 0; color: #f3f4f6;'>{scan.get('name', 'Quick Scan')[:25]}</h3>
                                <h4 style="color: {status_color}; margin: 5px 0;">{status.upper()}</h4>
                                <p style='font-size: 0.8rem; color: #9ca3af;'>📅 {scan.get('started_at', 'N/A')}</p>
                            </div>
                        """, unsafe_allow_html=True)
                                            
                        if st.button("Analyze Data", key=f"btn_{scan.get('id')}", use_container_width=True):
                            st.query_params["scan_id"] = str(scan.get('id'))
                            st.rerun()

def details_page(scan_id):
    st.markdown(f"<h1 class='cyber-header'>🔍 AUDIT ANALYSIS: SCAN #{scan_id}</h1>", unsafe_allow_html=True)
    
    if st.button("← Return to Repository"):
        st.query_params.clear()
        st.rerun()

    results = scaniAPI.get_scan_results(scan_id)
    scan_data = results.get("data", [])

    if not scan_data:
        st.warning("No host data associated with this scan session.")
        return

    # Tabs for modern layout
    tab_assets, tab_vulns = st.tabs(["🖥️ Detected Hosts", "⚠️ Global Vulnerabilities"])

    with tab_assets:
        for item in scan_data:
            asset = item.get('asset', {})
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"**Hostname:** `{asset.get('hostname')}`")
                c1.markdown(f"**IP:** `{asset.get('ip_address')}`")
                
                c2.markdown(f"**Status:** {'🟢 Active' if asset.get('status') == 'active' else '🔴 Offline'}")
                c2.markdown(f"**Vendor:** {asset.get('vendor', 'Generic')}")
                
                if c3.button("View Details", key=f"as_{asset.get('id')}"):
                    st.query_params["asset_id"] = str(asset.get('id'))
                    st.query_params["scan_id"] = str(scan_id)
                    st.rerun()

    with tab_vulns:
        # Aggregate logic
        all_vulns = []
        severity_map = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for item in scan_data:
            details = get_asset_details(item.get('asset', {}).get('id'))
            if details.get('data'):
                for svc in details['data'].get('services', []):
                    for v in svc.get('vulnerabilities', []):
                        v['host'] = item.get('asset', {}).get('ip_address')
                        all_vulns.append(v)
                        sev = v.get('severity', 'UNKNOWN').upper()
                        if sev in severity_map: severity_map[sev] += 1

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Critical", severity_map['CRITICAL'])
        m2.metric("High", severity_map['HIGH'])
        m3.metric("Medium", severity_map['MEDIUM'])
        m4.metric("Low", severity_map['LOW'])

        # Vuln List
        for v in all_vulns:
            sev = v.get('severity', 'UNKNOWN').upper()
            color_class = f"sev-{sev.lower()}"
            with st.expander(f"[{sev}] {v.get('cve_id')} — Found on {v.get('host')}"):
                st.markdown(f"<span class='{color_class}'>{v.get('description')}</span>", unsafe_allow_html=True)
                st.write(f"**CVSS:** {v.get('cvss_score')}")

def asset_details_page(asset_id, scan_id):
    # This keeps your logic but fits the new CSS
    asset_details = get_asset_details(asset_id)
    asset_data = asset_details.get("data")
    
    if st.button("← Back to Audit"):
        st.query_params["scan_id"] = str(scan_id)
        st.query_params.pop("asset_id", None)
        st.rerun()
        
    st.markdown(f"<h2 class='cyber-header'>HOST PROFILE: {asset_data.get('hostname')}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Primary IP:** {asset_data.get('ip_address')}")
        st.info(f"**MAC Address:** {asset_data.get('mac_address')}")
    with col2:
        st.info(f"**Operating System:** {asset_data.get('vendor', 'Detected via Nmap')}")
        st.info(f"**Last Seen:** {asset_data.get('last_seen')}")

    st.subheader("Open Ports & Services")
    for svc in asset_data.get('services', []):
        with st.container(border=True):
            st.markdown(f"### Port {svc.get('port')} ({svc.get('service_name')})")
            st.text(f"Version: {svc.get('version')}")
            if svc.get('vulnerabilities'):
                st.warning(f"Found {len(svc.get('vulnerabilities'))} CVEs")

def main():
    scan_id = st.query_params.get("scan_id")
    asset_id = st.query_params.get("asset_id")
    
    if asset_id and scan_id:
        asset_details_page(asset_id, scan_id)
    elif scan_id:
        details_page(scan_id)
    else:
        main_page()

if __name__ == "__main__":
    render_navigation()
    main()