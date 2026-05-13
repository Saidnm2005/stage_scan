import streamlit as st
from pages.login import check_authentication, get_current_user, logout
from ui.theme import apply_app_theme

def render_navigation():
    """
    Renders the navigation sidebar with persistent cyber-tech styling
    that applies to all pages automatically.
    """
    # Check if user is authenticated
    is_authenticated = check_authentication()
    
    # Persistent CSS styling - applied globally to all pages
    st.markdown("""
    <style>
    /* ==========================================================================
       PERSISTENT CYBER-GRID THEME - Applied to ALL Pages
       ========================================================================== */
    
    /* Dark Obsidian Sidebar - Consistent across all pages */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #05070a 0%, #0a0f1a 100%);
        border-right: 1px solid #1f2937;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Global Background for main content */
    .stApp {
        background: radial-gradient(ellipse at 20% 30%, #0a0f1a, #020409);
    }
    
    /* Main content area styling */
    .main .block-container {
        padding: 2rem 2.5rem;
        max-width: 1400px;
    }
    
    /* Scrollbar styling for all pages */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0d1726;
    }
    ::-webkit-scrollbar-thumb {
        background: #3b82f6;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #60a5fa;
    }
    
    /* Elegant Header in Sidebar */
    .nav-header {
        text-align: left;
        padding: 1.5rem 1rem;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .nav-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, #3b82f6, transparent);
    }
    
    .nav-header h2 {
        color: #f3f4f6;
        font-family: 'Courier New', monospace;
        font-size: 1.4rem;
        letter-spacing: 2px;
        margin: 0;
        background: linear-gradient(135deg, #f3f4f6, #9ca3af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .nav-header span {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Modern Button Styling - Consistent across all pages */
    div.stButton > button {
        background-color: #05070a;
        color: #9ca3af;
        border: 1px solid transparent;
        border-radius: 8px;
        text-align: left;
        height: 45px;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 4px;
        padding: 0 1rem;
        cursor: pointer;
        font-family: 'Courier New', monospace;
        letter-spacing: 0.5px;
    }
    
    div.stButton > button:hover {
        background-color: #111827;
        color: #3b82f6;
        border: 1px solid #3b82f6;
        box-shadow: 0px 0px 15px rgba(59, 130, 246, 0.25);
        transform: translateX(4px);
    }
    
    div.stButton > button:active {
        background-color: #3b82f6 !important;
        color: white !important;
        transform: scale(0.98);
    }
    
    /* Active page indicator - highlights current page button */
    div.stButton > button[data-active="true"] {
        background-color: #1e293b;
        color: #3b82f6;
        border-left: 3px solid #3b82f6;
    }
    
    /* Section Labels */
    .section-label {
        color: #4b5563;
        font-size: 0.7rem;
        font-weight: 700;
        margin: 1.5rem 0 0.8rem 1rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-family: 'Courier New', monospace;
    }
    
    /* User Info Card */
    .user-info-card {
        background: linear-gradient(135deg, #0f172a, #0a0f1a);
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .user-info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.8rem;
    }
    
    .user-name {
        color: #f3f4f6;
        font-size: 0.9rem;
        font-weight: 600;
        font-family: 'Courier New', monospace;
    }
    
    .user-role {
        color: #3b82f6;
        font-size: 0.7rem;
        letter-spacing: 1px;
        margin-top: 0.2rem;
    }
    
    /* Sidebar Footer */
    .sidebar-footer {
        position: fixed;
        bottom: 1rem;
        left: 1rem;
        color: #374151;
        font-size: 0.7rem;
        font-family: 'Courier New', monospace;
        letter-spacing: 0.5px;
    }
    
    /* Glowing dot animation for status */
    @keyframes glowPulse {
        0%, 100% { opacity: 1; text-shadow: 0 0 2px #10b981; }
        50% { opacity: 0.6; text-shadow: 0 0 8px #10b981; }
    }
    
    .sidebar-footer span {
        animation: glowPulse 2s ease-in-out infinite;
    }
    
    /* Headers styling for all pages */
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
    }
    
    h1 {
        background: linear-gradient(135deg, #f3f4f6, #9ca3af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Card styling for all pages */
    .metric-card, .info-card {
        background: rgba(5, 7, 10, 0.8);
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover, .info-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    /* Table styling */
    .stDataFrame {
        border: 1px solid #1f2937 !important;
        border-radius: 8px !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #0f172a !important;
        border-radius: 6px !important;
        color: #9ca3af !important;
        border: 1px solid #1f2937 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }
    
    /* Alert/Message styling */
    .stAlert {
        border-radius: 8px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 3px solid #10b981 !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 3px solid #f59e0b !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 3px solid #ef4444 !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 3px solid #3b82f6 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 0.8rem;
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
    
    /* Code blocks */
    code {
        background: #0f172a !important;
        color: #60a5fa !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 0.85rem !important;
        border: 1px solid #1f2937;
    }
    
    /* Divider */
    hr {
        border-color: #1f2937 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Tab styling */
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
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #3b82f6;
    }
    
    /* Button focus state */
    div.stButton > button:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
    }
    
    /* Dataframe styling */
    .dataframe {
        font-family: 'Courier New', monospace !important;
    }
    
    /* Tooltip styling */
    [data-tooltip] {
        position: relative;
        cursor: help;
    }
    
    [data-tooltip]:before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 4px 8px;
        background: #3b82f6;
        color: white;
        font-size: 11px;
        border-radius: 4px;
        white-space: nowrap;
        display: none;
        z-index: 1000;
    }
    
    [data-tooltip]:hover:before {
        display: block;
    }
    </style>
    
    <script>
    // Optional: Add active page detection
    document.addEventListener('DOMContentLoaded', function() {
        const currentPath = window.location.pathname;
        const buttons = document.querySelectorAll('div.stButton button');
        buttons.forEach(button => {
            const buttonText = button.innerText.toLowerCase();
            if (currentPath.includes('running_scan') && buttonText.includes('active')) {
                button.setAttribute('data-active', 'true');
            } else if (currentPath.includes('results') && buttonText.includes('results')) {
                button.setAttribute('data-active', 'true');
            } else if (currentPath.includes('manage') && buttonText.includes('asset')) {
                button.setAttribute('data-active', 'true');
            } else if (currentPath.includes('alert') && buttonText.includes('alert')) {
                button.setAttribute('data-active', 'true');
            } else if (currentPath.includes('dashboard') && buttonText.includes('analysis')) {
                button.setAttribute('data-active', 'true');
            } else if (currentPath.includes('settings') && buttonText.includes('settings')) {
                button.setAttribute('data-active', 'true');
            }
        });
    });
    </script>
    """, unsafe_allow_html=True)
    apply_app_theme()
    
    # Render the sidebar navigation
    with st.sidebar:
        # Tech-focused Title with cyber effect
        st.markdown("""
        <div class="nav-header">
            <h2>VULN<span>SCAN</span></h2>
        </div>
        """, unsafe_allow_html=True)
        
        # If authenticated, show user info and full navigation
        if is_authenticated:
            user_info = get_current_user()
            username = user_info.get('username', 'User')
            role = user_info.get('role', 'viewer')
            
            # Get first letter for avatar
            avatar_letter = username[0].upper() if username else "U"
            
            # Role color
            role_colors = {
                'admin': '#ef4444',
                'analyst': '#f59e0b',
                'viewer': '#10b981'
            }
            role_color = role_colors.get(role, '#64748b')
           
            # --- CORE OPERATIONS ---
            st.markdown('<p class="section-label">⚡ CORE OPERATIONS</p>', unsafe_allow_html=True)
            
            # # Dashboard (main app)
            # if st.button("⌬ &nbsp; Dashboard", use_container_width=True):
            #     st.switch_page("app.py")
            
            # Live Analysis
            if st.button("⬢ &nbsp; Live Analysis", use_container_width=True):
                st.switch_page("pages/dashboard.py")
            
            # Scan Results
            if st.button("◈ &nbsp; Scan Results", use_container_width=True):
                st.switch_page("pages/results.py")
            
            # Active Scans / Live Scan
            if st.button("◌ &nbsp; Active Scan", use_container_width=True):
                st.switch_page("pages/running_scan.py")
            
            # --- INFRASTRUCTURE ---
            st.markdown('<p class="section-label">🏗️ INFRASTRUCTURE</p>', unsafe_allow_html=True)
            
            # Asset Manager (admin and analyst only)
            if role in ['admin', 'analyst']:
                if st.button("⚙️ &nbsp; Asset Manager", use_container_width=True):
                    st.switch_page('pages/manage.py')
            
            # Alert Center (all authenticated users)
            if st.button("⚡ &nbsp; Alert Center", use_container_width=True):
                st.switch_page('pages/alert.py')
            
            # --- SYSTEM ---
            st.markdown('<p class="section-label">⚙️ SYSTEM</p>', unsafe_allow_html=True)
            
            # Settings (admin only)
            if role == 'admin':
                if st.button("🔧 &nbsp; Settings", use_container_width=True):
                    st.switch_page("app.py")
            
            # --- USER ACTIONS ---
            st.markdown('<p class="section-label">👤 ACCOUNT</p>', unsafe_allow_html=True)
            
            # Logout button
            if st.button("🚪 &nbsp; Logout", use_container_width=True):
                logout()
                st.rerun()
        
        else:
            # Show limited navigation for unauthenticated users
            # Only show login option
            st.markdown('<p class="section-label">🔐 ACCESS</p>', unsafe_allow_html=True)
            
            if st.button("🔑 &nbsp; Login", use_container_width=True):
                st.switch_page("pages/login.py")
            
            # Show a message
            st.markdown("""
            <div style="padding: 1rem; margin-top: 2rem; text-align: center;">
                <span style="color: #475569; font-size: 0.7rem;">
                    Please login to access<br>the vulnerability scanner
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Clean Footer with animated status

# Helper function to get current page (optional - for advanced features)
def get_current_page():
    """Returns the current page name from the URL"""
    try:
        # Get the current script path
        import os
        script_path = os.path.basename(st.scriptrunner.script_runner.get_script_path())
        return script_path.replace(".py", "")
    except Exception:
        return "unknown"
