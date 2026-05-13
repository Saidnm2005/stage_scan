import streamlit as st
import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from ui.theme import apply_login_theme

# Must be first Streamlit command
st.set_page_config(
    page_title="VulnScan | Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar and navigation for login page
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 420px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Constants
USERS_FILE = "users.json"
SESSION_FILE = "session.json"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 15  # minutes

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Default users
    default_users = {
        "admin": {
            "password": hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "failed_attempts": 0,
            "locked_until": None
        },
        "analyst": {
            "password": hash_password("analyst123"),
            "role": "analyst",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "failed_attempts": 0,
            "locked_until": None
        },
        "viewer": {
            "password": hash_password("viewer123"),
            "role": "viewer",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "failed_attempts": 0,
            "locked_until": None
        }
    }
    save_users(default_users)
    return default_users

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return True
    except:
        return False

def load_session():
    """Load current session from file"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session = json.load(f)
                # Check if session expired (24 hours)
                expires_at = datetime.fromisoformat(session.get('expires_at', '2000-01-01'))
                if expires_at > datetime.now():
                    return session
        except:
            pass
    return None

def save_session(username, role):
    """Save session to file"""
    session = {
        "username": username,
        "role": role,
        "login_time": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f, indent=4)
    return session

def clear_session():
    """Clear current session"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def is_account_locked(user_data):
    """Check if account is locked"""
    locked_until = user_data.get('locked_until')
    if locked_until:
        lock_time = datetime.fromisoformat(locked_until)
        if lock_time > datetime.now():
            remaining = (lock_time - datetime.now()).seconds // 60
            return True, remaining
        else:
            # Lock expired, reset failed attempts
            user_data['failed_attempts'] = 0
            user_data['locked_until'] = None
    return False, 0

def login_page():
    """Main login page"""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700;800&family=Syne:wght@400;500;600;700;800&display=swap');
        
        /* Cyber background */
        .stApp {
            background: radial-gradient(ellipse at 20% 30%, #0a0f1a, #020409);
            font-family: 'JetBrains Mono', monospace;
        }
        
        /* Login container */
        .login-container {
            background: linear-gradient(135deg, #0f172a, #0a0f1a);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 2.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            animation: fadeInUp 0.6s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Header */
        .cyber-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .cyber-header h1 {
            font-family: 'Syne', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #f3f4f6, #9ca3af);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        .cyber-header span {
            background: linear-gradient(135deg, #3b82f6, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .cyber-header p {
            color: #64748b;
            font-size: 0.75rem;
            letter-spacing: 3px;
            margin-top: 0.5rem;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background: #05070a;
            border: 1px solid #1e293b;
            border-radius: 8px;
            color: #f3f4f6;
            font-family: 'JetBrains Mono', monospace;
            padding: 0.7rem 1rem;
            font-size: 0.85rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
            outline: none;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            border: none;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            padding: 0.7rem 1rem;
            transition: all 0.3s ease;
            width: 100%;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Alert messages */
        .stAlert {
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
        }
        
        /* Divider */
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1.5rem 0;
            color: #334155;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #1e293b;
        }
        
        .divider span {
            margin: 0 0.75rem;
            font-size: 0.65rem;
            letter-spacing: 1px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 1.5rem;
            font-size: 0.7rem;
            color: #475569;
        }
        
        /* Status indicator */
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        /* Label styling */
        .stTextInput > label {
            color: #9ca3af !important;
            font-size: 0.7rem !important;
            letter-spacing: 1px !important;
            margin-bottom: 0.3rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    apply_login_theme()
    
    # Check if already logged in
    session = load_session()
    if session:
        st.session_state.authenticated = True
        st.session_state.username = session.get('username')
        st.session_state.user_role = session.get('role')
        st.switch_page("app.py")
        return
    
    # Login form container
    with st.container():
        st.markdown("""
        <div class="login-container">
            <div class="cyber-header">
                <h1>VULN<span>SCAN</span></h1>
                <p>AUTHORIZED ACCESS ONLY</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("USERNAME", placeholder="Enter your username", key="login_username")
            password = st.text_input("PASSWORD", type="password", placeholder="Enter your password", key="login_password")
            
            submitted = st.form_submit_button("🔐 LOGIN", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    users = load_users()
                    
                    if username in users:
                        user_data = users[username]
                        
                        # Check if account is locked
                        locked, remaining = is_account_locked(user_data)
                        if locked:
                            st.error(f"❌ Account locked. Try again in {remaining} minutes.")
                        else:
                            # Verify password
                            if user_data['password'] == hash_password(password):
                                # Successful login
                                user_data['failed_attempts'] = 0
                                user_data['last_login'] = datetime.now().isoformat()
                                user_data['locked_until'] = None
                                save_users(users)
                                
                                # Create session
                                save_session(username, user_data['role'])
                                
                                st.session_state.authenticated = True
                                st.session_state.username = username
                                st.session_state.user_role = user_data['role']
                                
                                st.success(f"✅ Welcome, {username}!")
                                st.balloons()
                                import time
                                time.sleep(1)
                                st.rerun()
                            else:
                                # Failed login attempt
                                user_data['failed_attempts'] = user_data.get('failed_attempts', 0) + 1
                                
                                if user_data['failed_attempts'] >= MAX_LOGIN_ATTEMPTS:
                                    # Lock the account
                                    lock_until = datetime.now() + timedelta(minutes=LOCKOUT_TIME)
                                    user_data['locked_until'] = lock_until.isoformat()
                                    st.error(f"❌ Too many failed attempts. Account locked for {LOCKOUT_TIME} minutes.")
                                else:
                                    remaining_attempts = MAX_LOGIN_ATTEMPTS - user_data['failed_attempts']
                                    st.error(f"❌ Invalid password. {remaining_attempts} attempts remaining.")
                                
                                save_users(users)
                    else:
                        st.error("❌ Username not found")
        
      
def logout():
    """Logout function"""
    clear_session()
    for key in ['authenticated', 'username', 'user_role']:
        if key in st.session_state:
            del st.session_state[key]
    st.success("✅ Logged out successfully!")
    st.rerun()


def check_authentication():
    """Check if user is authenticated, redirect to login if not"""
    session = load_session()
    
    if session:
        st.session_state.authenticated = True
        st.session_state.username = session.get('username')
        st.session_state.user_role = session.get('role')
        return True
    elif st.session_state.get('authenticated', False):
        return True
    else:
        st.switch_page("pages/login.py")
        return False


def require_role(required_roles):
    """Function to check user role"""
    if not check_authentication():
        return False
    
    user_role = st.session_state.get('user_role')
    if user_role not in required_roles:
        st.error(f"❌ Access denied. Required role: {', '.join(required_roles)}")
        return False
    
    return True


def get_current_user():
    """Get current user info"""
    return {
        "username": st.session_state.get('username'),
        "role": st.session_state.get('user_role')
    }


# If running directly
if __name__ == "__main__":
    import time
    login_page()
