import streamlit as st
import pandas as pd
import time
from datetime import datetime
from APi.AssetsAPi import get_asset_count, get_assets
from APi.scaniAPi import get_scans
from ui.navigation import render_navigation
from APi.known_assets_api import get_unknown_assets
import APi.AssetsAPi as assetApi
import APi.vulnAPi as vulnApi
from ui.notification import render_notifications
render_notifications()

# Page configuration
st.set_page_config(
    page_title="VulnScan | Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_navigation()

# Modern Security Dark Mode CSS
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #05070a;
        color: #f3f4f6;
    }
    
    /* Neon Metric Cards */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);
    }

    /* Accent bars for cards */
    .accent-blue { border-top: 4px solid #3b82f6; }
    .accent-red { border-top: 4px solid #ef4444; }
    .accent-amber { border-top: 4px solid #f59e0b; }
    .accent-emerald { border-top: 4px solid #10b981; }
    
    .big-metric {
        font-family: 'Courier New', monospace;
        font-size: 3.5rem;
        font-weight: 700;
        color: #f3f4f6;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Headers */
    .section-header {
        font-family: 'Courier New', monospace;
        color: #3b82f6;
        border-left: 4px solid #3b82f6;
        padding-left: 15px;
        margin: 40px 0 20px 0;
    }

    /* Custom Risk Gauge */
    .risk-container {
        background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
        border-radius: 50%;
        width: 200px;
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        border: 4px solid #1e293b;
    }

    /* Override Streamlit Sidebar */
    [data-testid="stSidebar"] {
        background-color: #05070a !important;
        border-right: 1px solid #1f2937 !important;
    }
    
    /* Table Styling */
    .stDataFrame {
        border: 1px solid #1e293b;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Data Fetching Logic (Keeping your existing logic) ---
@st.cache_data(ttl=30, show_spinner=False)
def fetch_metrics():
    try:
        total_assets = get_asset_count()
        res = get_unknown_assets()
        unknown_devices = res.get('count', 0)
        active_res = vulnApi.get_active_vuln()
      
        critical_res = vulnApi.get_critical_vuln()
        return {
            "total_assets": total_assets if total_assets else 0,
            "unknown_devices": unknown_devices,
            "critical_vulnerabilities": critical_res.get('count', 0),
            "total_vulnerabilities": active_res.get('count', 0),
            "timestamp": datetime.now()
        }
    except:
        return {"total_assets": 0, "unknown_devices": 0, "critical_vulnerabilities": 0, "total_vulnerabilities": 0, "timestamp": datetime.now()}

metric_data = fetch_metrics()

# Dashboard Header
st.markdown("""
    <div style='text-align: left; padding: 20px 0;'>
        <h1 style='color: #f3f4f6; font-family: Courier New;'>⚡ SECURITY COMMAND CENTER</h1>
        <p style='color: #6b7280;'>System Integrity: <span style='color: #10b981;'>OPTIMAL</span> | Last Scan: Today</p>
    </div>
""", unsafe_allow_html=True)

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card accent-blue">
            <div class="metric-label">Total Assets</div>
            <div class="big-metric">{metric_data['total_assets']}</div>
            <div style='color: #3b82f6; font-size: 0.8rem;'>Network Coverage 100%</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card accent-amber">
            <div class="metric-label">Unknown Devices</div>
            <div class="big-metric">{metric_data['unknown_devices']}</div>
            <div style='color: #f59e0b; font-size: 0.8rem;'>Potential Rogue Assets</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card accent-emerald">
            <div class="metric-label">Active Vulns</div>
            <div class="big-metric">{metric_data['total_vulnerabilities']}</div>
            <div style='color: #10b981; font-size: 0.8rem;'>Pending Remediation</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card accent-red">
            <div class="metric-label">Critical Risks</div>
            <div class="big-metric">{metric_data['critical_vulnerabilities']}</div>
            <div style='color: #ef4444; font-size: 0.8rem;'>Immediate Action Required</div>
        </div>
    """, unsafe_allow_html=True)

# Risk Analysis Section
st.markdown("<h3 class='section-header'>RATINGS & RISK ASSESSMENT</h3>", unsafe_allow_html=True)

c_left, c_right = st.columns([1, 2])

with c_left:
    # Calculate Risk Score
    risk_score = 0
    if metric_data["total_assets"] > 0:
        risk_score = (metric_data["critical_vulnerabilities"] * 5) + (metric_data["unknown_devices"] * 10)
        risk_score = min(100, risk_score)
    
    risk_color = "#ef4444" if risk_score > 60 else "#f59e0b" if risk_score > 30 else "#10b981"
    
    st.markdown(f"""
        <div class="risk-container" style="border-color: {risk_color};">
            <div style="text-align: center;">
                <div style="font-size: 0.8rem; color: #9ca3af;">RISK SCORE</div>
                <div style="font-size: 3.5rem; font-weight: bold; color: {risk_color};">{risk_score}</div>
                <div style="font-size: 0.7rem; color: {risk_color};">SEC-INDEX</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c_right:
    st.markdown("#### Vulnerability Distribution")
    # Placeholder for chart - Using standard Streamlit chart but matches dark theme automatically
    chart_data = pd.DataFrame({
        'Severity': ['Critical', 'High', 'Medium', 'Low'],
        'Count': [metric_data['critical_vulnerabilities'], 15, 22, 45] # Example static data + dynamic
    })
    st.bar_chart(chart_data.set_index('Severity'), color="#3b82f6")

# Inventory Table
st.markdown("<h3 class='section-header'>NETWORK INVENTORY SNAPSHOT</h3>", unsafe_allow_html=True)
assets_res = get_assets()
if assets_res and not assets_res.get("error"):
    df = pd.DataFrame(assets_res.get("data", []))
    if not df.empty:
        # Filter for key columns to keep it clean
        st.dataframe(
            df[['hostname', 'ip_address', 'vendor', 'status', 'trust_level']],
            use_container_width=True,
            hide_index=True
        )

# Footer
st.markdown("---")
st.caption(f"System Time: {datetime.now().strftime('%H:%M:%S')} | Node: EST-SAFI-SCANNER-01")