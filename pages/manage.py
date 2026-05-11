import streamlit as st
import pandas as pd
import time
from datetime import datetime
import APi.AssetsAPi as Assetapi
from APi.known_assets_api import check_existing_asset, add_known_asset, get_known_assets
from ui.navigation import render_navigation



# Page configuration
st.set_page_config(
    page_title="Device Management",
    page_icon="🖥️",
    layout="wide"
)

# Modern "Cyber-Grid" CSS styling
st.markdown("""
<style>
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Dark Obsidian Sidebar */
    [data-testid="stSidebar"] {
        background-color: #05070a;
        border-right: 1px solid #1f2937;
    }
    
    /* Elegant Header */
    .nav-header {
        text-align: left;
        padding: 1.5rem 1rem;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 1.5rem;
    }
    
    .nav-header h2 {
        color: #f3f4f6;
        font-family: 'Courier New', monospace;
        font-size: 1.4rem;
        letter-spacing: 2px;
        margin: 0;
    }
    
    .nav-header span {
        color: #3b82f6;
    }

    /* Known Device Card - Cyber Blue Theme */
    .known-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .known-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        border-color: #60a5fa;
    }
    
    .known-card h3 {
        color: #3b82f6;
        margin-bottom: 0.5rem;
        font-size: 1rem;
        letter-spacing: 1px;
    }
    
    .known-card h2 {
        color: #10b981;
        font-size: 2.5rem;
        text-align: center;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
    }
    
    .known-card p {
        color: #9ca3af;
        font-size: 0.8rem;
        text-align: center;
        margin: 0;
    }

    /* Unknown Device Card - Cyber Red Theme */
    .unknown-card {
        background: linear-gradient(135deg, #2d1a1a 0%, #1a0f0f 100%);
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .unknown-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.15);
        border-color: #f87171;
    }
    
    .unknown-card h3 {
        color: #ef4444;
        margin-bottom: 0.5rem;
        font-size: 1rem;
        letter-spacing: 1px;
    }
    
    .unknown-card h2 {
        color: #f97316;
        font-size: 2.5rem;
        text-align: center;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
    }
    
    .unknown-card p {
        color: #9ca3af;
        font-size: 0.8rem;
        text-align: center;
        margin: 0;
    }

    /* Device Card Styling */
    .device-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        transition: all 0.2s ease;
    }
    
    .device-card:hover {
        border-color: #3b82f6;
        background: #111827;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #0f172a;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #9ca3af;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Button Styling */
    div.stButton > button {
        background: #0f172a;
        color: #3b82f6;
        border: 1px solid #3b82f6;
        border-radius: 6px;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    div.stButton > button:hover {
        background: #3b82f6;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Form Styling */
    .stForm {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1.5rem;
    }
    
    /* Divider Styling */
    hr {
        border-color: #1e293b;
        margin: 1.5rem 0;
    }
    
    /* Info/Warning/Success Boxes */
    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: #0f172a;
        border-radius: 8px;
        color: #3b82f6;
    }
    
    /* Text Input Styling */
    .stTextInput > div > div > input {
        background-color: #0f172a;
        border-color: #1e293b;
        color: #f3f4f6;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background-color: #0f172a;
        border-color: #1e293b;
    }
    
    /* Code block styling for MAC addresses */
    code {
        background: #1e293b;
        color: #60a5fa;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'refresh_devices' not in st.session_state:
    st.session_state.refresh_devices = False

def fetch_known_devices():
    """Fetch known devices from known_assets table"""
    try:
        response = get_known_assets()
        if response and not response.get("error"):
            return response.get('data', [])
        return []
    except Exception as e:
        st.error(f"⚠️ Error fetching known devices: {e}")
        return []

def fetch_unknown_devices():
    """Fetch unknown devices - assets that exist but are not in known_assets"""
    try:
        # Get all assets
        assets_response = Assetapi.get_assets()
        if not assets_response or assets_response.get("error"):
            return []
        
        assets_data = assets_response.get("data", [])
        
        # Get all known MAC addresses from known_assets
        known_macs = set()
        try:
            known_response = get_known_assets()
            if known_response and not known_response.get("error"):
                known_assets = known_response.get("data", [])
                for known in known_assets:
                    mac = known.get('mac_address')
                    if mac:
                        known_macs.add(mac.upper())
        except Exception as e:
            st.warning(f"⚠️ Could not fetch known assets: {e}")
        
        # Filter assets that are NOT in known_macs
        unknown_devices = []
        for asset in assets_data:
            mac = asset.get('mac_address')
            
            # If asset has trust_level = 'trusted' in assets table, consider it known
            if asset.get('trust_level') == 'trusted':
                continue
                
            # Check if MAC is in known assets
            if mac and mac != "N/A":
                if mac.upper() not in known_macs:
                    unknown_devices.append(asset)
            else:
                # Devices without MAC are considered unknown
                unknown_devices.append(asset)
        
        return unknown_devices
    except Exception as e:
        st.error(f"⚠️ Error fetching unknown devices: {e}")
        return []

def update_asset_trust_level(asset_id, mac_address, ip_address):
    """Update the asset's trust level to 'trusted' in the assets table"""
    try:
        # Find asset by MAC or IP and update
        assets_response = Assetapi.get_assets()
        if assets_response and not assets_response.get("error"):
            assets_data = assets_response.get("data", [])
            for asset in assets_data:
                asset_mac = asset.get('mac_address')
                asset_ip = asset.get('ip_address')
                
                if (asset_mac and mac_address and asset_mac.upper() == mac_address.upper()) or \
                   (asset_ip and ip_address and asset_ip == ip_address):
                    # Found the asset, update its trust level
                    st.info(f"🔒 Asset {asset.get('id')} marked as trusted")
                    return True
        
        return False
    except Exception as e:
        st.error(f"⚠️ Error updating asset trust level: {e}")
        return False

def mark_device_as_known(device_id, mac_address, ip_address, hostname, vendor, owner=None, device_type=None):
    """Mark an unknown device as known in the known_assets table and update assets table"""
    try:
        if not mac_address or mac_address == "N/A":
            st.error("⚠️ Cannot mark device as known without a MAC address!")
            return False
        
        # Set default values if not provided
        owner = owner or hostname or "Unknown Owner"
        device_type = device_type or vendor or "Unknown Type"
        
        # Check if already in known_assets
        if check_existing_asset(mac_address):
            st.info(f"📌 Device with MAC {mac_address} is already in known assets!")
            update_asset_trust_level(device_id, mac_address, ip_address)
            return True
        
        # Add to known_assets table
        known_asset_payload = {
            "mac_address": mac_address.upper(),
            "owner": owner,
            "device_type": device_type
        }
        
        response = add_known_asset(known_asset_payload)
        
        if response and not response.get("error"):
            update_asset_trust_level(device_id, mac_address, ip_address)
            st.success(f"✅ Device {ip_address} ({hostname}) marked as known!")
            return True
        else:
            st.error(f"⚠️ Failed to mark device as known: {response.get('error') if response else 'Unknown error'}")
            return False
            
    except Exception as e:
        st.error(f"⚠️ Error marking device as known: {e}")
        return False

def display_device_card(device, is_known=False):
    """Display a device in a card format"""
    with st.container():
        st.markdown('<div class="device-card">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            st.markdown(f"**🖥️ {device.get('hostname', 'Unknown')}**")
            st.caption(f"🌐 IP: {device.get('ip_address', 'N/A')}")
            st.caption(f"🆔 ID: {device.get('id', 'N/A')}")
        
        with col2:
            st.markdown(f"**🔌 MAC:** `{device.get('mac_address', 'N/A')}`")
            st.markdown(f"🏭 **Vendor:** {device.get('vendor', 'Unknown')}")
            st.markdown(f"🎯 **Trust Level:** {device.get('trust_level', 'unknown')}")
        
        with col3:
            st.markdown(f"📅 **First Seen:** {device.get('first_seen', 'N/A')}")
            st.markdown(f"🕒 **Last Seen:** {device.get('last_seen', 'N/A')}")
          
        with col4:
            if not is_known:
                if device.get('mac_address') and device.get('mac_address') != "N/A":
                    if st.button("✅ Mark as Known", key=f"mark_{device.get('id')}"):
                        if mark_device_as_known(
                            device.get('id'),
                            device.get('mac_address'),
                            device.get('ip_address'),
                            device.get('hostname', 'Unknown'),
                            device.get('vendor', 'Unknown'),
                            "",
                            ""
                        ):
                            st.session_state.refresh_devices = True
                            st.rerun()
                else:
                    st.warning("⚠️ No MAC available")
        st.markdown('</div>', unsafe_allow_html=True)

def device_management_page():
    # Tech-focused Title
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #f3f4f6; font-family: 'Courier New', monospace; margin-bottom: 0.5rem;">
            🖥️ DEVICE MANAGEMENT
        </h1>
        <p style="color: #9ca3af; border-left: 3px solid #3b82f6; padding-left: 1rem;">
            Monitor and manage network assets
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Refresh button row
    col_refresh1, col_refresh2 = st.columns([6, 1])
    with col_refresh2:
        if st.button("🔄 REFRESH", use_container_width=True):
            st.session_state.refresh_devices = True
            st.rerun()
    
    st.markdown("---")
    
    # Get data
    known_devices = fetch_known_devices()
    unknown_devices = fetch_unknown_devices()
    
    # Statistics cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="known-card">
            <h3>✅ KNOWN DEVICES</h3>
            <h2>{len(known_devices)}</h2>
            <p>Approved and trusted devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="unknown-card">
            <h3>⚠️ UNKNOWN DEVICES</h3>
            <h2>{len(unknown_devices)}</h2>
            <p>Unauthorized or unrecognized devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_devices = len(known_devices) + len(unknown_devices)
        known_percentage = (len(known_devices) / total_devices * 100) if total_devices > 0 else 0
        st.markdown(f"""
        <div class="known-card" style="border-color: #10b981;">
            <h3>📊 COVERAGE RATE</h3>
            <h2>{known_percentage:.1f}%</h2>
            <p>Device visibility rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for known and unknown devices
    tab1, tab2, tab3 = st.tabs(["✅ KNOWN DEVICES", "⚠️ UNKNOWN DEVICES", "➕ ADD DEVICE"])
    
    with tab1:
        st.subheader(f"📋 Known Devices ({len(known_devices)})")
        
        if known_devices:
            search = st.text_input("🔍 Search known devices", placeholder="Search by IP, hostname, or MAC...")
            
            filtered_known = known_devices
            if search:
                filtered_known = [
                    d for d in known_devices 
                    if search.lower() in str(d.get('ip_address', '')).lower()
                    or search.lower() in str(d.get('hostname', '')).lower()
                    or search.lower() in str(d.get('mac_address', '')).lower()
                ]
            
            for device in filtered_known:
                with st.container():
                    st.markdown('<div class="device-card">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**🖥️ {device.get('hostname', 'Unknown')}**")
                        st.caption(f"🌐 IP: {device.get('ip_address', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**🔌 MAC:** `{device.get('mac_address', 'N/A')}`")
                        st.markdown(f"🏭 **Vendor:** {device.get('vendor', 'Unknown')}")
                    
                    with col3:
                        st.markdown(f"💿 **OS:** {device.get('os_guess', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("📭 No known devices found. Mark unknown devices as known to see them here.")
    
    with tab2:
        st.subheader(f"⚠️ Unknown Devices ({len(unknown_devices)})")
        
        if unknown_devices:
            search = st.text_input("🔍 Search unknown devices", placeholder="Search by IP, hostname, or MAC...", key="search_unknown")
            
            filter_option = st.selectbox(
                "🎯 Filter by",
                ["All", "Has MAC Address", "No MAC Address", "Recently Seen"],
                key="filter_unknown"
            )
            
            filtered_unknown = unknown_devices
            if search:
                filtered_unknown = [
                    d for d in unknown_devices 
                    if search.lower() in str(d.get('ip_address', '')).lower()
                    or search.lower() in str(d.get('hostname', '')).lower()
                    or search.lower() in str(d.get('mac_address', '')).lower()
                ]
            
            if filter_option == "Has MAC Address":
                filtered_unknown = [d for d in filtered_unknown if d.get('mac_address') and d.get('mac_address') != "N/A"]
            elif filter_option == "No MAC Address":
                filtered_unknown = [d for d in filtered_unknown if not d.get('mac_address') or d.get('mac_address') == "N/A"]
            elif filter_option == "Recently Seen":
                filtered_unknown = sorted(filtered_unknown, key=lambda x: x.get('last_seen', ''), reverse=True)[:10]
            
            # Bulk operations
            has_mac_devices = [d for d in filtered_unknown if d.get('mac_address') and d.get('mac_address') != "N/A"]
            if has_mac_devices:
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("⚡ Mark All as Known", type="primary", use_container_width=True):
                        success_count = 0
                        for device in has_mac_devices:
                            if mark_device_as_known(
                                device.get('id'),
                                device.get('mac_address'),
                                device.get('ip_address'),
                                device.get('hostname', 'Unknown'),
                                device.get('vendor', 'Unknown'),
                                "",
                                ""
                            ):
                                success_count += 1
                        st.success(f"✅ Marked {success_count} devices as known!")
                        st.session_state.refresh_devices = True
                        time.sleep(1)
                        st.rerun()
            
            for device in filtered_unknown:
                if not device.get('mac_address') or device.get('mac_address') == "N/A":
                    st.warning(f"⚠️ Device with NO MAC Address - {device.get('ip_address')}")
                
                display_device_card(device, is_known=False)
                st.divider()
        else:
            st.success("🎉 No unknown devices found! All devices are trusted.")
    
    with tab3:
        st.subheader("➕ Manually Add Known Device")
        
        with st.form("add_known_device_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mac_address = st.text_input("🔌 MAC Address *", placeholder="00:11:22:33:44:55").upper()
                ip_address = st.text_input("🌐 IP Address", placeholder="192.168.1.100")
                hostname = st.text_input("🖥️ Hostname", placeholder="device-name")
            
            with col2:
                vendor = st.text_input("🏭 Vendor/Manufacturer", placeholder="Cisco, Dell, HP, etc.")
                os_guess = st.text_input("💿 Operating System", placeholder="Windows, Ubuntu, Mac OS, etc.")
                owner = st.text_input("👤 System Owner", placeholder="")
            
            submitted = st.form_submit_button("✅ Add to Known Assets", type="primary", use_container_width=True)
            
            if submitted:
                if not mac_address:
                    st.error("⚠️ MAC Address is required!")
                else:
                    if check_existing_asset(mac_address):
                        st.warning(f"📌 Device with MAC {mac_address} is already in known assets!")
                    else:
                        known_payload = {
                            "mac_address": mac_address,
                            "owner": owner,
                            "device_type": os_guess
                        }
                        
                        response = add_known_asset(known_payload)
                        
                        if response and not response.get("error"):
                            st.success(f"✅ Device {hostname or mac_address} added to known assets!")
                            st.balloons()
                            st.session_state.refresh_devices = True
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"⚠️ Failed to add device: {response.get('error') if response else 'Unknown error'}")
    
    # Export functionality
    st.markdown("---")
    with st.expander("📥 Export Device Lists"):
        col1, col2 = st.columns(2)
        
        with col1:
            if known_devices:
                known_df = pd.DataFrame(known_devices)
                csv_known = known_df.to_csv(index=False)
                st.download_button(
                    label="📊 Export Known Devices CSV",
                    data=csv_known,
                    file_name=f"known_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if unknown_devices:
                unknown_df = pd.DataFrame(unknown_devices)
                csv_unknown = unknown_df.to_csv(index=False)
                st.download_button(
                    label="⚠️ Export Unknown Devices CSV",
                    data=csv_unknown,
                    file_name=f"unknown_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# Run the page
if __name__ == "__main__":
    render_navigation()
    device_management_page()