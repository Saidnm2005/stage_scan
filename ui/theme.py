import streamlit as st


def apply_app_theme() -> None:
    """Apply the shared VulnScan interface theme."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

            :root {
                --vs-bg: #070b12;
                --vs-bg-soft: #0c1220;
                --vs-panel: rgba(15, 23, 42, 0.82);
                --vs-panel-solid: #101827;
                --vs-border: rgba(148, 163, 184, 0.16);
                --vs-border-strong: rgba(96, 165, 250, 0.36);
                --vs-text: #e5edf7;
                --vs-muted: #94a3b8;
                --vs-faint: #64748b;
                --vs-blue: #38bdf8;
                --vs-indigo: #6366f1;
                --vs-green: #22c55e;
                --vs-amber: #f59e0b;
                --vs-red: #ef4444;
                --vs-shadow: 0 20px 60px rgba(0, 0, 0, 0.34);
                --vs-radius: 8px;
            }

            html, body, [class*="css"] {
                font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }

            .stApp {
                color: var(--vs-text);
                background:
                    radial-gradient(circle at 18% 12%, rgba(56, 189, 248, 0.16), transparent 26rem),
                    radial-gradient(circle at 90% 8%, rgba(99, 102, 241, 0.16), transparent 24rem),
                    linear-gradient(180deg, #070b12 0%, #0a1020 48%, #070b12 100%) !important;
            }

            .main .block-container {
                max-width: 1440px;
                padding: 2rem 2.4rem 3rem;
            }

            h1, h2, h3 {
                font-family: 'Inter', system-ui, sans-serif !important;
                letter-spacing: 0 !important;
                color: var(--vs-text) !important;
            }

            h1 {
                font-size: clamp(2rem, 3vw, 3.25rem) !important;
                font-weight: 800 !important;
                line-height: 1.05 !important;
            }

            h2, h3 {
                font-weight: 750 !important;
            }

            p, label, span, div {
                letter-spacing: 0;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(8, 13, 23, 0.98), rgba(12, 18, 32, 0.98)),
                    radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 16rem) !important;
                border-right: 1px solid var(--vs-border) !important;
                box-shadow: 18px 0 70px rgba(0, 0, 0, 0.28) !important;
            }

            [data-testid="stSidebar"] .block-container {
                padding: 1.2rem 0.95rem 1.4rem;
            }

            .nav-header {
                padding: 1rem 0.75rem 1.25rem !important;
                margin-bottom: 1rem !important;
                border-bottom: 1px solid var(--vs-border) !important;
            }

            .nav-header h2 {
                font-family: 'Inter', system-ui, sans-serif !important;
                font-size: 1.35rem !important;
                font-weight: 800 !important;
                letter-spacing: 0 !important;
                color: var(--vs-text) !important;
                -webkit-text-fill-color: initial !important;
                background: none !important;
            }

            .nav-header span {
                color: var(--vs-blue) !important;
                -webkit-text-fill-color: initial !important;
                background: none !important;
            }

            .section-label {
                margin: 1.15rem 0 0.55rem 0.75rem !important;
                color: var(--vs-faint) !important;
                font-family: 'Inter', system-ui, sans-serif !important;
                font-size: 0.68rem !important;
                font-weight: 800 !important;
                letter-spacing: 0.08em !important;
            }

            div.stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                min-height: 2.75rem;
                border-radius: var(--vs-radius) !important;
                border: 1px solid var(--vs-border) !important;
                background: rgba(15, 23, 42, 0.66) !important;
                color: var(--vs-text) !important;
                font-family: 'Inter', system-ui, sans-serif !important;
                font-size: 0.9rem !important;
                font-weight: 700 !important;
                letter-spacing: 0 !important;
                box-shadow: none !important;
                transition: transform 160ms ease, border-color 160ms ease, background 160ms ease, color 160ms ease;
            }

            div.stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-1px);
                border-color: var(--vs-border-strong) !important;
                background: rgba(30, 41, 59, 0.92) !important;
                color: #ffffff !important;
            }

            div.stButton > button[kind="primary"],
            div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
                background: linear-gradient(135deg, #0284c7, #4f46e5) !important;
                border-color: rgba(125, 211, 252, 0.42) !important;
                color: #ffffff !important;
            }

            [data-testid="stSidebar"] div.stButton > button {
                justify-content: flex-start;
                height: 2.65rem;
                margin-bottom: 0.25rem;
                padding: 0 0.85rem !important;
                background: transparent !important;
                color: var(--vs-muted) !important;
            }

            [data-testid="stSidebar"] div.stButton > button:hover {
                transform: translateX(2px);
                background: rgba(56, 189, 248, 0.1) !important;
                color: var(--vs-text) !important;
                border-color: rgba(56, 189, 248, 0.3) !important;
            }

            [data-testid="stVerticalBlockBorderWrapper"],
            [data-testid="stMetric"],
            .metric-card,
            .info-card,
            .device-card,
            .filter-bar,
            .timeline-container {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.66)) !important;
                border: 1px solid var(--vs-border) !important;
                border-radius: var(--vs-radius) !important;
                box-shadow: var(--vs-shadow);
            }

            .metric-card {
                padding: 1.15rem !important;
            }

            .metric-card:hover,
            .info-card:hover,
            .device-card:hover,
            [data-testid="stMetric"]:hover {
                border-color: var(--vs-border-strong) !important;
                transform: translateY(-2px);
            }

            .big-metric,
            [data-testid="stMetricValue"] {
                font-family: 'JetBrains Mono', monospace !important;
                color: var(--vs-text) !important;
                letter-spacing: -0.02em !important;
            }

            .metric-label,
            [data-testid="stMetricLabel"] {
                color: var(--vs-muted) !important;
                font-family: 'Inter', system-ui, sans-serif !important;
                letter-spacing: 0.08em !important;
                font-weight: 800 !important;
            }

            .section-header,
            .cyber-header {
                color: var(--vs-text) !important;
                border-left: 3px solid var(--vs-blue) !important;
                padding-left: 0.85rem !important;
                letter-spacing: 0 !important;
            }

            .accent-blue { border-top-color: var(--vs-blue) !important; }
            .accent-red { border-top-color: var(--vs-red) !important; }
            .accent-amber { border-top-color: var(--vs-amber) !important; }
            .accent-emerald { border-top-color: var(--vs-green) !important; }

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"],
            .stMultiSelect [data-baseweb="select"] {
                background: rgba(7, 11, 18, 0.82) !important;
                color: var(--vs-text) !important;
                border: 1px solid var(--vs-border) !important;
                border-radius: var(--vs-radius) !important;
                box-shadow: none !important;
            }

            .stTextInput input:focus,
            .stNumberInput input:focus,
            .stTextArea textarea:focus {
                border-color: var(--vs-blue) !important;
                box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.16) !important;
            }

            label, [data-testid="stWidgetLabel"] {
                color: var(--vs-muted) !important;
                font-weight: 700 !important;
            }

            [data-testid="stDataFrame"],
            .stDataFrame {
                border: 1px solid var(--vs-border) !important;
                border-radius: var(--vs-radius) !important;
                overflow: hidden;
                box-shadow: var(--vs-shadow);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.35rem !important;
                background: rgba(15, 23, 42, 0.72) !important;
                border: 1px solid var(--vs-border);
                border-radius: var(--vs-radius);
                padding: 0.35rem !important;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 6px !important;
                color: var(--vs-muted) !important;
                font-family: 'Inter', system-ui, sans-serif !important;
                font-weight: 700 !important;
            }

            .stTabs [aria-selected="true"] {
                background: rgba(56, 189, 248, 0.16) !important;
                color: #ffffff !important;
            }

            details,
            .streamlit-expanderHeader,
            [data-testid="stExpander"] {
                border-color: var(--vs-border) !important;
                border-radius: var(--vs-radius) !important;
                background: rgba(15, 23, 42, 0.58) !important;
            }

            .stAlert {
                border-radius: var(--vs-radius) !important;
                border: 1px solid var(--vs-border) !important;
                background: rgba(15, 23, 42, 0.72) !important;
            }

            code {
                background: rgba(2, 6, 23, 0.72) !important;
                color: #7dd3fc !important;
                border: 1px solid var(--vs-border) !important;
                border-radius: 6px !important;
                font-family: 'JetBrains Mono', monospace !important;
            }

            hr {
                border-color: var(--vs-border) !important;
            }

            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }

            ::-webkit-scrollbar-track {
                background: #070b12;
            }

            ::-webkit-scrollbar-thumb {
                background: #334155;
                border-radius: 999px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #475569;
            }

            @media (max-width: 768px) {
                .main .block-container {
                    padding: 1.1rem 1rem 2rem;
                }

                .big-metric {
                    font-size: 2.35rem !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_login_theme() -> None:
    """Apply the focused authentication screen theme."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

            .stApp {
                background:
                    radial-gradient(circle at 50% 8%, rgba(56, 189, 248, 0.18), transparent 24rem),
                    radial-gradient(circle at 10% 85%, rgba(99, 102, 241, 0.14), transparent 24rem),
                    linear-gradient(180deg, #070b12 0%, #0a1020 100%) !important;
                font-family: 'Inter', system-ui, sans-serif !important;
            }

            .main .block-container {
                max-width: 460px !important;
                padding-top: 7vh !important;
            }

            .login-container {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.68)) !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                border-radius: 10px !important;
                box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42) !important;
                padding: 2rem !important;
            }

            .cyber-header h1 {
                font-family: 'Inter', system-ui, sans-serif !important;
                font-size: 2.45rem !important;
                letter-spacing: 0 !important;
                -webkit-text-fill-color: initial !important;
                background: none !important;
                color: #e5edf7 !important;
            }

            .cyber-header span {
                color: #38bdf8 !important;
                -webkit-text-fill-color: initial !important;
                background: none !important;
            }

            .cyber-header p {
                color: #94a3b8 !important;
                letter-spacing: 0.1em !important;
                font-weight: 800 !important;
            }

            .stTextInput > div > div > input {
                background: rgba(7, 11, 18, 0.86) !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                border-radius: 8px !important;
                color: #e5edf7 !important;
                font-family: 'Inter', system-ui, sans-serif !important;
            }

            .stTextInput > div > div > input:focus {
                border-color: #38bdf8 !important;
                box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.16) !important;
            }

            .stTextInput > label {
                color: #94a3b8 !important;
                font-family: 'Inter', system-ui, sans-serif !important;
                letter-spacing: 0.08em !important;
                font-weight: 800 !important;
            }

            .stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(135deg, #0284c7, #4f46e5) !important;
                color: #ffffff !important;
                border: 1px solid rgba(125, 211, 252, 0.42) !important;
                border-radius: 8px !important;
                font-family: 'Inter', system-ui, sans-serif !important;
                font-weight: 800 !important;
                letter-spacing: 0 !important;
                min-height: 2.9rem;
                box-shadow: 0 16px 40px rgba(2, 132, 199, 0.22) !important;
            }

            .stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-1px);
                filter: brightness(1.06);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
