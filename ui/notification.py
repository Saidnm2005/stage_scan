# ui/notification.py
import streamlit as st
from datetime import datetime
import APi.alert_api as AlertApi

def get_unresolved_alert_count():
    """Get count of unresolved alerts"""
    try:
        alerts_response = AlertApi.get_alerts()
        if alerts_response and not alerts_response.get("error"):
            alerts = alerts_response.get("data", [])
            return sum(1 for alert in alerts if not alert.get('resolved', False))
        return 0
    except Exception as e:
        print(f"Error fetching alert count: {e}")
        return 0

def render_notifications():
    """Render the notification bell"""
    alert_count = get_unresolved_alert_count()
    
    # Custom CSS for notification bell
    st.markdown("""
        <style>
        .notification-bell-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            cursor: pointer;
        }
        .bell-icon {
            font-size: 20px;
            position: relative;
            display: inline-block;
            background: white;
            padding: 10px;
            border-radius: 50%;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            margin-top: 60px;
        }
        .bell-icon:hover {
            transform: scale(1.1);
        }
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ff4444;
            color: white;
            border-radius: 50%;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: bold;
            min-width: 20px;
            text-align: center;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display bell with badge
    badge = f'<span class="notification-badge">{alert_count}</span>' if alert_count > 0 else ''
    
    # Use HTML/CSS for bell - JavaScript navigation
    st.markdown(f"""
        <div class="notification-bell-container" onclick=>
            <div class="bell-icon">🔔{badge}
            </div>
        </div>
    """, unsafe_allow_html=True)




    