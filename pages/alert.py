import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import APi.alert_api as AlertApi
from APi.AssetsAPi import get_asset_details
from ui.navigation import render_navigation
from ui.notification import render_notifications

# Page configuration MUST be first
st.set_page_config(
    page_title="Security Alerts",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Render navigation and notifications
render_navigation()
render_notifications()

# Modern Professional CSS Design
st.markdown("""
    <style>
    /* Modern Dark/Light Theme Variables */
    :root {
        --primary-dark: #0f0f1a;
        --primary-card: #1a1a2e;
        --critical: #ff4444;
        --high: #ff6b35;
        --medium: #ffd700;
        --low: #00c9ff;
        --success: #00ff88;
    }
    
    /* Animated Header */
    .hero-header {
        position: relative;
        overflow: hidden;
        border-radius: 30px;
        margin-bottom: 40px;
        background: linear-gradient(135deg, rgba(255,68,68,0.1) 0%, rgba(255,107,53,0.1) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,68,68,0.3) 0%, transparent 70%);
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
        padding: 60px 40px;
        text-align: center;
    }
    
    .hero-title {
        font-size: 56px;
        font-weight: 800;
        background: linear-gradient(135deg, #ff4444 0%, #ff6b35 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(255,68,68,0.3); }
        50% { text-shadow: 0 0 40px rgba(255,68,68,0.6); }
    }
    
    .hero-subtitle {
        font-size: 18px;
        color: rgba(255,255,255,0.7);
    }
    
    /* Modern Stat Cards */
    .stat-card-modern {
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
        cursor: pointer;
    }
    
    .stat-card-modern:hover {
        transform: translateY(-5px);
        background: rgba(26, 26, 46, 0.9);
        border-color: rgba(255,255,255,0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .stat-icon {
        font-size: 40px;
        margin-bottom: 15px;
    }
    
    .stat-value {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    
    .stat-label-modern {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: rgba(255,255,255,0.6);
    }
    
    /* Alert Cards */
    .alert-card-modern {
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin-bottom: 20px;
        overflow: hidden;
        transition: all 0.3s ease;
        border-left: 4px solid;
        cursor: pointer;
    }
    
    .alert-card-modern:hover {
        transform: translateX(10px);
        background: rgba(26, 26, 46, 0.95);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .alert-header {
        padding: 20px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .alert-badge-modern {
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .alert-content {
        padding: 20px 25px;
    }
    
    .alert-message {
        font-size: 16px;
        color: rgba(255,255,255,0.9);
        margin-bottom: 15px;
        line-height: 1.5;
    }
    
    .alert-meta {
        display: flex;
        gap: 20px;
        font-size: 12px;
        color: rgba(255,255,255,0.5);
        margin-top: 10px;
    }
    
    /* Filter Bar */
    .filter-bar {
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
        background: rgba(26, 26, 46, 0.5);
        border-radius: 30px;
        margin: 40px 0;
    }
    
    .empty-state-icon {
        font-size: 80px;
        margin-bottom: 20px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    /* Timeline Chart */
    .timeline-container {
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 20px;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'refresh_alerts' not in st.session_state:
    st.session_state.refresh_alerts = False
if 'selected_alert' not in st.session_state:
    st.session_state.selected_alert = None
if 'last_alert_count' not in st.session_state:
    st.session_state.last_alert_count = 0

def parse_alert_date(date_string):
    """Safely parse date strings from API"""
    if not date_string or date_string == 'N/A':
        return None
    
    try:
        # Handle different date formats
        if 'Z' in date_string:
            # ISO format with Zulu timezone
            return datetime.fromisoformat(date_string.replace('Z', '+00:00')).replace(tzinfo=None)
        elif 'T' in date_string:
            # ISO format without timezone
            return datetime.fromisoformat(date_string.split('.')[0])
        else:
            # Standard format
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return None

def get_alerts_with_details():
    """Fetch alerts with asset details"""
    try:
        alerts_response = AlertApi.get_alerts()
        if not alerts_response or alerts_response.get("error"):
            return []
        
        alerts = alerts_response.get("data", [])
        unresolved_alerts = [a for a in alerts if not a.get('resolved', False)]
        
        for alert in unresolved_alerts:
            asset_id = alert.get('asset_id')
            if asset_id:
                try:
                    asset_details = get_asset_details(asset_id)
                    if asset_details and not asset_details.get("error"):
                        alert['asset'] = asset_details.get('data', {})
                except Exception:
                    pass
        
        return unresolved_alerts
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return []

def get_alert_statistics(alerts):
    """Calculate alert statistics"""
    stats = {
        'total': len(alerts),
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'by_type': {}
    }
    
    for alert in alerts:
        severity = alert.get('severity', 'UNKNOWN').upper()
        alert_type = alert.get('type', 'unknown')
        
        if severity == 'CRITICAL':
            stats['critical'] += 1
        elif severity == 'HIGH':
            stats['high'] += 1
        elif severity == 'MEDIUM':
            stats['medium'] += 1
        elif severity == 'LOW':
            stats['low'] += 1
        
        stats['by_type'][alert_type] = stats['by_type'].get(alert_type, 0) + 1
    
    return stats

def resolve_alert(alert_id):
    """Mark alert as resolved"""
    try:
        update_payload = {
            "resolved": True,
            "resolved_at": datetime.now().isoformat(),
            "resolved_by": st.session_state.get('username', 'System')
        }
        response = AlertApi.update_alert(alert_id, update_payload)
        
        if response and not response.get("error"):
            st.success(f"✅ Alert #{alert_id} resolved successfully!")
            st.session_state.refresh_alerts = True
            st.session_state.last_alert_count = max(0, st.session_state.last_alert_count - 1)
            return True
        else:
            st.error(f"Failed to resolve alert")
            return False
    except Exception as e:
        st.error(f"Error resolving alert: {e}")
        return False

def resolve_all_alerts(alerts):
    """Resolve all alerts"""
    success_count = 0
    for alert in alerts:
        if resolve_alert(alert.get('id')):
            success_count += 1
    return success_count

def alerts_page():
    # Hero Header
    st.markdown("""
        <div class="hero-header">
            <div class="hero-content">
                <div class="hero-title">🚨 SECURITY COMMAND CENTER</div>
                <div class="hero-subtitle">Real-time threat intelligence & incident response platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Fetch alerts
    alerts = get_alerts_with_details()
    stats = get_alert_statistics(alerts)
    
    # Statistics Row - Modern Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    stat_configs = [
        (col1, "📊", stats['total'], "TOTAL ALERTS", "#ff4444"),
        (col2, "🔴", stats['critical'], "CRITICAL", "#ff4444"),
        (col3, "🟠", stats['high'], "HIGH", "#ff6b35"),
        (col4, "🟡", stats['medium'], "MEDIUM", "#ffd700"),
        (col5, "🔵", stats['low'], "LOW", "#00c9ff")
    ]
    
    for col, icon, value, label, color in stat_configs:
        with col:
            st.markdown(f"""
                <div class="stat-card-modern">
                     <div class="stat-icon">{icon}</div>
                    <div class="stat-value" style="color: {color};">{value}</div>
                    <div class="stat-label-modern">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Action Buttons - FIXED: use width instead of use_container_width
    col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     if st.button("🔄 Refresh Alerts", use_container_width=True, type="primary"):
    #         st.rerun()
    
    # Filter Bar
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        st.markdown("### 🔍 Filter & Search")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.multiselect(
                "Severity Level",
                options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                key="severity_filter"
            )
        with col2:
            if stats['by_type']:
                type_filter = st.multiselect(
                    "Alert Type",
                    options=list(stats['by_type'].keys()),
                    default=list(stats['by_type'].keys()),
                    key="type_filter"
                )
            else:
                type_filter = []
        with col3:
            search_term = st.text_input("🔎 Search Alerts", placeholder="Search by message, IP, or hostname...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply Filters
    filtered_alerts = alerts
    if severity_filter:
        filtered_alerts = [a for a in filtered_alerts if a.get('severity', 'UNKNOWN').upper() in severity_filter]
    if type_filter:
        filtered_alerts = [a for a in filtered_alerts if a.get('type', 'unknown') in type_filter]
    if search_term:
        filtered_alerts = [
            a for a in filtered_alerts 
            if search_term.lower() in a.get('message', '').lower()
            or search_term.lower() in str(a.get('asset', {}).get('ip_address', '')).lower()
            or search_term.lower() in a.get('asset', {}).get('hostname', '').lower()
        ]
    
    # Bulk Actions - FIXED: use width instead of use_container_width
    if filtered_alerts:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("✅ Resolve All Visible Alerts", use_container_width=False, type="primary"):
                success_count = resolve_all_alerts(filtered_alerts)
                if success_count > 0:
                    st.success(f"✅ Resolved {success_count} alerts!")
                    st.rerun()
    
    # Alerts List
    if filtered_alerts:
        st.markdown(f"### 📋 Active Alerts ({len(filtered_alerts)})")
        
        for alert in filtered_alerts:
            severity = alert.get('severity', 'UNKNOWN').upper()
            alert_id = alert.get('id')
            message = alert.get('message', 'No message')
            created_at = alert.get('created_at', 'N/A')
            alert_type = alert.get('type', 'unknown')
            asset = alert.get('asset', {})
            
            # Color mapping
            colors = {
                "CRITICAL": {"border": "#ff4444", "badge": "#ff4444"},
                "HIGH": {"border": "#ff6b35", "badge": "#ff6b35"},
                "MEDIUM": {"border": "#ffd700", "badge": "#ffd700"},
                "LOW": {"border": "#00c9ff", "badge": "#00c9ff"}
            }
            color = colors.get(severity, colors["LOW"])
            
            # Format time - FIXED: handle timezone issues
            time_str = "Unknown time"
            parsed_time = parse_alert_date(created_at)
            if parsed_time:
                time_diff = datetime.now() - parsed_time
                if time_diff.total_seconds() < 60:
                    time_str = f"{int(time_diff.total_seconds())} seconds ago"
                elif time_diff.total_seconds() < 3600:
                    time_str = f"{int(time_diff.total_seconds() // 60)} minutes ago"
                elif time_diff.total_seconds() < 86400:
                    time_str = f"{int(time_diff.total_seconds() // 3600)} hours ago"
                else:
                    time_str = parsed_time.strftime("%Y-%m-%d %H:%M")
            
            with st.container():
                st.markdown(f"""
                    <div class="alert-card-modern" style="border-left-color: {color['border']};">
                        <div class="alert-header">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <span style="font-size: 32px;">{'🔴' if severity == 'CRITICAL' else '🟠' if severity == 'HIGH' else '🟡' if severity == 'MEDIUM' else '🔵'}</span>
                                <div>
                                    <h3 style="margin: 0; color: white;">{severity} Alert</h3>
                                    <span style="font-size: 12px; color: rgba(255,255,255,0.5);">#{alert_id}</span>
                                </div>
                            </div>
                            <span class="alert-badge-modern" style="background: {color['badge']}; color: {'#000' if severity == 'MEDIUM' else '#fff'}">
                                {alert_type.replace('_', ' ').upper()}
                            </span>
                        </div>
                        <div class="alert-content">
                            <div class="alert-message">{message}</div>
                            <div class="alert-meta">
                                <span>📅 {time_str}</span>
                                <span>🖥️ Asset ID: {alert.get('asset_id', 'N/A')}</span>
                            </div>
                """, unsafe_allow_html=True)
                
                # Expandable asset details
                with st.expander(f"📋 Asset Details - {asset.get('hostname', 'Unknown')}"):
                    if asset:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**IP Address:** `{asset.get('ip_address', 'N/A')}`")
                            st.markdown(f"**Hostname:** {asset.get('hostname', 'N/A')}")
                            st.markdown(f"**MAC Address:** `{asset.get('mac_address', 'N/A')}`")
                        with col2:
                            st.markdown(f"**Vendor:** {asset.get('vendor', 'N/A')}")
                            st.markdown(f"**OS Guess:** {asset.get('os_guess', 'N/A')}")
                            st.markdown(f"**Trust Level:** {asset.get('trust_level', 'N/A')}")
                    else:
                        st.info("No asset details available")
                
                # Action buttons - FIXED: use width instead of use_container_width
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button(f"✅ Resolve", key=f"resolve_{alert_id}"):
                        if resolve_alert(alert_id):
                            st.rerun()
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    else:
        # Empty State
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🛡️</div>
                <h2 style="color: #00ff88; margin-bottom: 10px;">No Active Alerts!</h2>
                <p style="color: rgba(255,255,255,0.7);">All systems are secure. No threats detected.</p>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()
    
    # Timeline Chart - FIXED: better error handling and data preparation
    if alerts:
        with st.expander("📈 Alert Timeline & Analytics", expanded=False):
            st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
            
            # Create timeline data with proper date parsing
            timeline_data = []
            for alert in alerts:
                created_at = alert.get('created_at')
                if created_at and created_at != 'N/A':
                    parsed_time = parse_alert_date(created_at)
                    if parsed_time:
                        # Only include alerts from last 7 days
                        if (datetime.now() - parsed_time).days < 7:
                            timeline_data.append({
                                'timestamp': parsed_time,
                                'severity': alert.get('severity', 'LOW')
                            })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                df_timeline.set_index('timestamp', inplace=True)
                df_timeline['count'] = 1
                
                try:
                    # Resample by hour (using 'h' instead of 'H')
                    timeline_counts = df_timeline.resample('h').count()
                    st.line_chart(timeline_counts['count'], width='stretch')
                    st.caption("Alert frequency over time (last 7 days)")
                except Exception as e:
                    st.warning(f"Unable to display timeline chart: {str(e)}")
            else:
                st.info("Not enough data for timeline visualization")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Run the page
if __name__ == "__main__":
    alerts_page()