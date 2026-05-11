import streamlit as st
import time
import threading
from datetime import datetime
import APi.alert_api as AlertApi

def monitor_alerts():
    """Background thread to monitor for new alerts"""
    if 'alert_monitor_running' not in st.session_state:
        st.session_state.alert_monitor_running = False
        st.session_state.last_check = datetime.now()
        st.session_state.known_alert_ids = set()
        
        # Load existing alert IDs
        try:
            alerts = AlertApi.get_alerts()
            if alerts and not alerts.get("error"):
                for alert in alerts.get("data", []):
                    st.session_state.known_alert_ids.add(alert.get('id'))
        except:
            pass

def start_alert_monitor():
    """Start the alert monitoring thread"""
    if 'alert_monitor' not in st.session_state:
        monitor_alerts()
        
        def check_loop():
            while True:
                time.sleep(10)  # Check every 10 seconds
                try:
                    alerts_response = AlertApi.get_alerts()
                    if alerts_response and not alerts_response.get("error"):
                        current_alerts = alerts_response.get("data", [])
                        current_ids = {a.get('id') for a in current_alerts if not a.get('resolved')}
                        
                        # Check for new alerts
                        new_alerts = current_ids - st.session_state.known_alert_ids
                        if new_alerts:
                            st.session_state.new_alerts = len(new_alerts)
                            st.session_state.known_alert_ids = current_ids
                except:
                    pass
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
        st.session_state.alert_monitor = thread