"""
live_scan.py
============
- Reads scan_progress.json written by worker.py every 2 s
- Auto-launches the next scan when the schedule interval elapses
- Shows real-time progress: phase bar, current host, live stats, host cards
- When a scan completes, shows summary + countdown to next run
"""

import streamlit as st
import pandas as pd
import subprocess
import os
import json
import time
from datetime import datetime, timedelta

# ─── Navigation ───────────────────────────────────────────────────────────────
try:
    from ui.navigation import render_navigation
except ImportError:
    pass

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NetAudit · Live Scan",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Constants ────────────────────────────────────────────────────────────────
SETTINGS_FILE    = "general_settings.json"
PROGRESS_FILE    = "scan_progress.json"
WORKER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "worker.py")
REFRESH_INTERVAL = 2

# ══════════════════════════════════════════════════════════════════════════════
# ENHANCED CSS - Modern Cyber Theme with Animations
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700;800&family=Syne:wght@400;500;600;700;800&display=swap');

/* ==========================================================================
   RESET & BASE
   ========================================================================== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: radial-gradient(ellipse at 20% 30%, #0a0f1a, #020409);
    font-family: 'JetBrains Mono', monospace;
}

.main .block-container {
    padding: 1.5rem 2.5rem 3rem;
    max-width: 1600px;
    margin: 0 auto;
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1726; }
::-webkit-scrollbar-thumb { background: #1a6bff; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3d82ff; }

/* Hide Streamlit default elements */
[data-testid="stSidebar"] { background: #030609; border-right: 1px solid #0d1726; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ==========================================================================
   HERO SECTION - Enhanced Glow Effect
   ========================================================================== */
.hero {
    position: relative;
    padding: 2.8rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    border-radius: 4px;
    overflow: hidden;
    background: linear-gradient(165deg, #0a1220 0%, #020409 100%);
    border: 1px solid rgba(26, 107, 255, 0.15);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.hero::before {
    content: '';
    position: absolute;
    inset: 0 0 auto 0;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        #1a6bff 15%, 
        #00e5ff 50%, 
        #1a6bff 85%, 
        transparent 100%);
    background-size: 200% 100%;
    animation: scanline 3s linear infinite;
}

.hero::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -30%;
    width: 400px;
    height: 400px;
    background: radial-gradient(ellipse, rgba(26, 107, 255, 0.08) 0%, transparent 70%);
    pointer-events: none;
}

@keyframes scanline {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #1a6bff;
    border: 1px solid rgba(26, 107, 255, 0.4);
    background: rgba(26, 107, 255, 0.05);
    padding: 0.35rem 1rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    backdrop-filter: blur(4px);
}

.hero-badge .dot {
    width: 8px;
    height: 8px;
    background: #1a6bff;
    border-radius: 50%;
    animation: pulse 1.4s ease-in-out infinite;
    box-shadow: 0 0 8px #1a6bff;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.2); }
}

.hero h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: clamp(1.8rem, 4vw, 3rem);
    background: linear-gradient(135deg, #e8edf5 0%, #8fa8cc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin: 0 0 0.5rem;
    line-height: 1.1;
}

.hero h1 span {
    background: linear-gradient(135deg, #1a6bff, #00e5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 0.8rem;
    color: #5a6e8a;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
}

/* ==========================================================================
   STATISTICS CARDS - Glassmorphism Style
   ========================================================================== */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.stat-card {
    background: rgba(5, 13, 26, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(26, 107, 255, 0.15);
    border-radius: 8px;
    padding: 1.2rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
    border-color: rgba(26, 107, 255, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(26, 107, 255, 0.15);
}

.stat-card::before {
    content: '';
    position: absolute;
    inset: 0 auto 0 0;
    width: 3px;
    background: var(--accent, #1a6bff);
    opacity: 0.8;
    transition: width 0.3s ease;
}

.stat-card:hover::before {
    width: 4px;
}

.stat-label {
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #5a6e8a;
    margin-bottom: 0.6rem;
    font-weight: 500;
}

.stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e8edf5;
    line-height: 1;
}

.stat-value.accent {
    background: linear-gradient(135deg, var(--accent, #1a6bff), #00e5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ==========================================================================
   PROGRESS BAR - Animated
   ========================================================================== */
.phase-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.phase-label {
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #1a6bff;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.phase-label.done { color: #22dd88; }

.phase-label::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #1a6bff;
    border-radius: 50%;
    animation: pulse 1.4s ease-in-out infinite;
    box-shadow: 0 0 6px #1a6bff;
}

.phase-label.done::before {
    background: #22dd88;
    animation: none;
    box-shadow: 0 0 8px #22dd88;
}

.phase-pct {
    font-size: 0.85rem;
    color: #e8edf5;
    font-weight: 600;
}

.prog-track {
    height: 6px;
    background: rgba(13, 23, 38, 0.8);
    border-radius: 3px;
    overflow: visible;
    margin-bottom: 1.5rem;
    position: relative;
}

.prog-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #1a6bff, #00e5ff);
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    box-shadow: 0 0 10px rgba(26, 107, 255, 0.5);
}

.prog-fill::after {
    content: '';
    position: absolute;
    right: -5px;
    top: 50%;
    transform: translateY(-50%);
    width: 12px;
    height: 12px;
    background: #00e5ff;
    border-radius: 50%;
    box-shadow: 0 0 15px #00e5ff;
    animation: glow 1s ease-in-out infinite;
}

@keyframes glow {
    0%, 100% { opacity: 0.6; transform: translateY(-50%) scale(1); }
    50% { opacity: 1; transform: translateY(-50%) scale(1.2); }
}

.prog-fill.done {
    background: linear-gradient(90deg, #22dd88, #00e5ff);
}

.prog-fill.done::after {
    background: #22dd88;
    box-shadow: 0 0 15px #22dd88;
}

/* ==========================================================================
   STATUS MESSAGES
   ========================================================================== */
.status-msg {
    background: rgba(5, 13, 26, 0.6);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(26, 107, 255, 0.2);
    border-left: 3px solid #1a6bff;
    padding: 0.9rem 1.2rem;
    border-radius: 6px;
    font-size: 0.78rem;
    color: #8fa8cc;
    margin-bottom: 1.5rem;
    letter-spacing: 0.03em;
    font-family: 'JetBrains Mono', monospace;
}

.status-msg.done {
    border-left-color: #22dd88;
    background: rgba(34, 221, 136, 0.05);
}

/* ==========================================================================
   TARGET CARD
   ========================================================================== */
.target-card {
    background: linear-gradient(135deg, rgba(5, 13, 26, 0.9), rgba(26, 107, 255, 0.05));
    border: 1px solid rgba(26, 107, 255, 0.3);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(26, 107, 255, 0.1);
    animation: slideIn 0.4s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.target-icon {
    font-size: 2rem;
    filter: drop-shadow(0 0 5px #1a6bff);
}

.target-ip {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1a6bff;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
}

.target-meta {
    font-size: 0.65rem;
    color: #5a6e8a;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* ==========================================================================
   HOST CARDS - Modern List View
   ========================================================================== */
.host-card {
    background: rgba(5, 13, 26, 0.7);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(13, 23, 38, 0.8);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.25s ease;
    cursor: pointer;
}

.host-card:hover {
    border-color: rgba(26, 107, 255, 0.4);
    background: rgba(26, 107, 255, 0.05);
    transform: translateX(5px);
}

.host-ip {
    font-size: 0.9rem;
    color: #e8edf5;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.host-meta {
    font-size: 0.65rem;
    color: #5a6e8a;
    margin-top: 0.2rem;
    letter-spacing: 0.05em;
}

.host-badges {
    display: flex;
    gap: 0.6rem;
    align-items: center;
}

.hbadge {
    font-size: 0.6rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 15px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.hbadge-vuln {
    background: rgba(255, 68, 68, 0.15);
    color: #ff5555;
    border: 1px solid rgba(255, 68, 68, 0.3);
}

.hbadge-vuln:hover {
    background: rgba(255, 68, 68, 0.25);
    transform: scale(1.05);
}

.hbadge-safe {
    background: rgba(34, 221, 136, 0.1);
    color: #22dd88;
    border: 1px solid rgba(34, 221, 136, 0.3);
}

.hbadge-svc {
    background: rgba(0, 229, 255, 0.08);
    color: #00e5ff;
    border: 1px solid rgba(0, 229, 255, 0.2);
}

/* ==========================================================================
   COUNTDOWN TIMER
   ========================================================================== */
.countdown {
    background: linear-gradient(135deg, rgba(5, 13, 26, 0.9), rgba(26, 107, 255, 0.03));
    border: 1px solid rgba(26, 107, 255, 0.2);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    font-size: 0.78rem;
    color: #5a6e8a;
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(4px);
}

.countdown-timer {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #1a6bff, #00e5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
}

.countdown-label {
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #5a6e8a;
}

.schedule-info {
    font-size: 0.7rem;
    color: #5a6e8a;
    letter-spacing: 0.05em;
    line-height: 1.6;
}

.schedule-info strong {
    color: #8fa8cc;
    font-weight: 600;
}

/* ==========================================================================
   COMPLETE BANNER
   ========================================================================== */
.complete-banner {
    background: linear-gradient(135deg, rgba(34, 221, 136, 0.08), rgba(5, 13, 26, 0.9));
    border: 1px solid rgba(34, 221, 136, 0.3);
    border-radius: 10px;
    padding: 1.3rem 1.8rem;
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    backdrop-filter: blur(4px);
    animation: slideDown 0.5s ease;
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.complete-icon {
    font-size: 2rem;
    animation: bounce 0.5s ease;
}

@keyframes bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.complete-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #22dd88;
}

.complete-sub {
    font-size: 0.72rem;
    color: #5a6e8a;
    margin-top: 0.2rem;
    letter-spacing: 0.05em;
}

/* ==========================================================================
   IDLE PANEL
   ========================================================================== */
.idle-panel {
    background: rgba(5, 13, 26, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(26, 107, 255, 0.15);
    border-radius: 12px;
    padding: 3.5rem;
    text-align: center;
    margin: 2rem 0;
}

.idle-panel .idle-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
    filter: drop-shadow(0 0 10px #1a6bff);
}

.idle-panel p {
    color: #5a6e8a;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    margin-bottom: 0;
    line-height: 1.8;
}

/* ==========================================================================
   SECTION TITLE
   ========================================================================== */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #e8edf5;
    letter-spacing: -0.01em;
    margin: 1.8rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1a6bff, transparent);
    margin-left: 0.5rem;
}

/* ==========================================================================
   BUTTONS - Modern Design
   ========================================================================== */
div.stButton > button {
    background: linear-gradient(135deg, rgba(5, 13, 26, 0.9), rgba(26, 107, 255, 0.05));
    color: #8fa8cc;
    border: 1px solid rgba(26, 107, 255, 0.3);
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    padding: 0.6rem 1.2rem;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    backdrop-filter: blur(4px);
}

div.stButton > button:hover {
    background: rgba(26, 107, 255, 0.15);
    border-color: rgba(26, 107, 255, 0.7);
    color: #e8edf5;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(26, 107, 255, 0.2);
}

div.stButton > button:active {
    transform: translateY(0);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a6bff, #0d4fd0);
    color: #fff;
    border-color: #1a6bff;
    box-shadow: 0 2px 8px rgba(26, 107, 255, 0.3);
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #3d82ff, #1a6bff);
    box-shadow: 0 4px 15px rgba(26, 107, 255, 0.4);
    transform: translateY(-2px);
}

/* ==========================================================================
   STREAMLIT COMPONENT OVERRIDES
   ========================================================================== */
[data-testid="stMetric"] {
    background: rgba(5, 13, 26, 0.6);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(26, 107, 255, 0.15);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    transition: all 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(26, 107, 255, 0.4);
}

[data-testid="stMetricLabel"] {
    color: #5a6e8a !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: #e8edf5 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}

.streamlit-expanderHeader {
    background: rgba(5, 13, 26, 0.8) !important;
    border-radius: 8px !important;
    color: #8fa8cc !important;
    border: 1px solid rgba(26, 107, 255, 0.2) !important;
    font-size: 0.78rem !important;
    transition: all 0.2s ease;
}

.streamlit-expanderHeader:hover {
    border-color: rgba(26, 107, 255, 0.5) !important;
    background: rgba(26, 107, 255, 0.05) !important;
}

.streamlit-expanderContent {
    background: rgba(3, 6, 9, 0.8) !important;
    border: 1px solid rgba(26, 107, 255, 0.2) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

.stAlert {
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    backdrop-filter: blur(4px);
}

hr {
    border-color: rgba(13, 23, 38, 0.8) !important;
    margin: 1.5rem 0;
}

code {
    background: rgba(13, 23, 38, 0.8) !important;
    color: #1a6bff !important;
    padding: 0.15rem 0.45rem !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    border: 1px solid rgba(26, 107, 255, 0.3);
}

.stDataFrame {
    border: 1px solid rgba(26, 107, 255, 0.2) !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* Loading spinner overlay */
@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(26, 107, 255, 0.2);
    border-top-color: #1a6bff;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_config() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def read_progress() -> dict:
    """Read scan_progress.json written atomically by worker.py."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def worker_is_running() -> bool:
    try:
        return subprocess.run(
            ["pgrep", "-f", "worker.py"], capture_output=True
        ).returncode == 0
    except Exception:
        return False


def launch_worker(ip_range: str) -> bool:
    """Spawn worker.py --once as a fully detached process."""
    try:
        log_path = os.path.join(os.path.dirname(__file__), "worker.log")
        subprocess.Popen(
            ["python3", WORKER_SCRIPT, "--once", "--range", ip_range],
            stdout=open(log_path, "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        return True
    except Exception as exc:
        st.error(f"Could not start worker: {exc}")
        return False


def next_scan_time(cfg: dict):
    """Return datetime of the next scheduled scan, or None."""
    if not cfg.get("auto_rerun"):
        return None
    interval = cfg.get("interval", 24)
    unit     = cfg.get("unit", "Hours")
    last     = cfg.get("last_scan_completed")
    if not last:
        return None
    try:
        base  = datetime.fromisoformat(last)
        delta = {
            "Minutes": timedelta(minutes=interval),
            "Hours":   timedelta(hours=interval),
            "Days":    timedelta(days=interval),
        }.get(unit, timedelta(hours=interval))
        return base + delta
    except Exception:
        return None


def time_until(dt: datetime) -> tuple:
    left = max((dt - datetime.now()).total_seconds(), 0)
    return int(left // 3600), int((left % 3600) // 60), int(left % 60)


# ══════════════════════════════════════════════════════════════════════════════
# UI Components
# ══════════════════════════════════════════════════════════════════════════════

def _hero(subtitle: str, is_live: bool = False):
    badge = f'<span class="loading-spinner"></span>SCANNING ACTIVE' if is_live else 'LIVE READY'
    st.markdown(f"""
    <div class="hero">
        <div class="hero-badge"><span class="dot"></span>{badge}</div>
        <h1>Net<span>Audit</span></h1>
        <div class="hero-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def _progress_bar(pct: float, phase: str, message: str, done: bool = False):
    done_cls  = "done" if done else ""
    label_cls = "phase-label done" if done else "phase-label"
    safe_pct  = max(float(pct), 2)
    st.markdown(f"""
    <div class="phase-header">
        <div class="{label_cls}">{phase.upper()}</div>
        <div class="phase-pct">{pct:.0f}%</div>
    </div>
    <div class="prog-track">
        <div class="prog-fill {done_cls}" style="width:{safe_pct:.0f}%"></div>
    </div>
    <div class="status-msg {done_cls}">⟫ {message}</div>
    """, unsafe_allow_html=True)


def _target_card(ip: str, current: int, total: int):
    st.markdown(f"""
    <div class="target-card">
        <div class="target-icon">🖥️</div>
        <div>
            <div class="target-ip">{ip}</div>
            <div class="target-meta">🎯 TARGET {current} OF {total} · ACTIVE SCAN</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _stat_cards(p: dict):
    total_h  = p.get("total_hosts", 0)
    done_h   = len(p.get("hosts_done", []))
    services = p.get("total_services", 0)
    vulns    = p.get("total_vulns", 0)
    vc = "#ff4444" if vulns else "#22dd88"
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card" style="--accent:#1a6bff">
            <div class="stat-label">🌐 HOSTS DISCOVERED</div>
            <div class="stat-value accent">{total_h}</div>
        </div>
        <div class="stat-card" style="--accent:#00e5ff">
            <div class="stat-label">✅ HOSTS SCANNED</div>
            <div class="stat-value accent" style="color:#00e5ff">{done_h}</div>
        </div>
        <div class="stat-card" style="--accent:#a78bfa">
            <div class="stat-label">🔌 SERVICES FOUND</div>
            <div class="stat-value accent" style="color:#a78bfa">{services}</div>
        </div>
        <div class="stat-card" style="--accent:{vc}">
            <div class="stat-label">⚠️ CVEs DETECTED</div>
            <div class="stat-value accent" style="color:{vc}">{vulns}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _host_row(host: dict):
    ip        = host.get("ip", "?")
    hostname  = host.get("hostname", "")
    vendor    = host.get("vendor", "")
    services  = host.get("services", 0)
    vulns     = host.get("vulns", 0)
    vuln_list = host.get("vuln_list", [])

    badge_cls  = "hbadge-vuln" if vulns else "hbadge-safe"
    badge_text = f"⚠️ {vulns} CVE{'s' if vulns != 1 else ''}" if vulns else "✓ CLEAN"
    meta_parts = [x for x in [hostname, vendor] if x and x not in ("Unknown", "")]
    meta_str   = "  ·  ".join(meta_parts) if meta_parts else "—"

    st.markdown(f"""
    <div class="host-card">
        <div>
            <div class="host-ip">{ip}</div>
            <div class="host-meta">{meta_str}</div>
        </div>
        <div class="host-badges">
            <span class="hbadge hbadge-svc">🔌 {services} svc</span>
            <span class="hbadge {badge_cls}">{badge_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if vuln_list:
        with st.expander(f"📋 CVE Details — {ip}"):
            rows = []
            for v in vuln_list:
                try:
                    s = float(v.get("cvss") or 0)
                    if s >= 7.0:
                        score_str = f"🔴 {s:.1f}"
                    elif s >= 4.0:
                        score_str = f"🟡 {s:.1f}"
                    else:
                        score_str = f"🟢 {s:.1f}"
                except (TypeError, ValueError):
                    score_str = "—"
                
                severity = v.get("severity", "UNKNOWN")
                severity_badge = {
                    "CRITICAL": "🔴 CRITICAL",
                    "HIGH": "🟠 HIGH",
                    "MEDIUM": "🟡 MEDIUM",
                    "LOW": "🟢 LOW"
                }.get(severity.upper(), severity)
                
                rows.append({
                    "CVE": v.get("cve_id", "—"),
                    "CVSS": score_str,
                    "Severity": severity_badge,
                    "Description": v.get("description", "")[:120] + ("..." if len(v.get("description", "")) > 120 else "")
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _countdown_banner(nxt: datetime, cfg: dict):
    h, m, s  = time_until(nxt)
    interval = cfg.get("interval", "?")
    unit     = cfg.get("unit", "Hours")
    last     = cfg.get("last_scan_completed", "")
    try:
        last_fmt = datetime.fromisoformat(last).strftime("%d %b %Y · %H:%M")
    except Exception:
        last_fmt = "—"
    st.markdown(f"""
    <div class="countdown">
        <div>
            <div class="countdown-label">⏰ NEXT SCAN IN</div>
            <div class="countdown-timer">{h:02d}:{m:02d}:{s:02d}</div>
        </div>
        <div style="width:1px;height:2.5rem;background:rgba(26,107,255,0.3);"></div>
        <div class="schedule-info">
            📅 Every <strong>{interval} {unit}</strong><br>
            ✓ Last completed: <strong>{last_fmt}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _complete_banner(p: dict):
    hosts    = p.get("total_hosts", 0)
    services = p.get("total_services", 0)
    vulns    = p.get("total_vulns", 0)
    finished = p.get("finished_at", "")
    try:
        finished_fmt = datetime.fromisoformat(finished).strftime("%d %b %Y · %H:%M:%S")
    except Exception:
        finished_fmt = ""
    st.markdown(f"""
    <div class="complete-banner">
        <div class="complete-icon">✅</div>
        <div>
            <div class="complete-title">AUDIT COMPLETE</div>
            <div class="complete-sub">
                📊 {hosts} host(s) &nbsp;·&nbsp; 🔌 {services} service(s) &nbsp;·&nbsp;
                ⚠️ {vulns} CVE(s) &nbsp;·&nbsp; 🕐 {finished_fmt}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    cfg      = load_config()
    ip_range = st.session_state.get("target_ip") or cfg.get("target_ip", "")
    if ip_range:
        st.session_state.target_ip = ip_range

    # ── No IP range configured ────────────────────────────────────────────────
    if not ip_range:
        _hero("Configure a target range to get started.")
        st.markdown("""
        <div class="idle-panel">
            <div class="idle-icon">📡</div>
            <p>No target IP range configured.<br>Head to Settings to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚙️ Open Settings", use_container_width=True):
            st.switch_page("pages/settings.py")
        return

    # ── Read current state from progress file ─────────────────────────────────
    p           = read_progress()
    is_scanning = worker_is_running()
    phase       = p.get("phase", "idle")
    complete    = p.get("complete", False)
    error       = p.get("error")

    # ── Auto-launch: coming from Settings with scan_requested=True ────────────
    if st.session_state.pop("scan_requested", False) and not is_scanning:
        if launch_worker(ip_range):
            is_scanning = True
            time.sleep(0.6)
            p     = read_progress()
            phase = p.get("phase", "init")
            st.toast("🚀 Scan started!", icon="⚡")

    # ── Auto-schedule: trigger next scan when interval has elapsed ─────────────
    if not is_scanning and cfg.get("auto_rerun"):
        nxt = next_scan_time(cfg)
        if nxt and datetime.now() >= nxt:
            if launch_worker(ip_range):
                is_scanning = True
                time.sleep(0.6)
                p     = read_progress()
                phase = p.get("phase", "init")
                st.toast("⏰ Auto-scan started!", icon="🔄")

    # ── Hero ──────────────────────────────────────────────────────────────────
    _hero(
        f"🎯 Scanning `{ip_range}`..." if is_scanning else f"📡 Target: `{ip_range}`",
        is_live=is_scanning,
    )

    if p.get("scan_id"):
        st.caption(f"🆔 Scan ID · `{p['scan_id']}`")

    # ── Action bar ────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        if is_scanning:
            st.markdown(
                f'<div class="status-msg">⚡ SCAN ACTIVE — Auto-refreshing every {REFRESH_INTERVAL}s</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button("🚀 Launch Scan Now", use_container_width=True, type="primary"):
                if launch_worker(ip_range):
                    is_scanning = True
                    st.rerun()
    with c2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with c3:
        if st.button("⚙️ Settings", use_container_width=True, key="settings_top"):
            st.switch_page("pages/settings.py")

    st.markdown("---")

    # ── Nothing has run yet ───────────────────────────────────────────────────
    if not p and not is_scanning:
        nxt = next_scan_time(cfg)
        if nxt:
            _countdown_banner(nxt, cfg)
        st.markdown("""
        <div class="idle-panel">
            <div class="idle-icon">🔍</div>
            <p>No scan has run yet.<br>
            Click <strong>🚀 Launch Scan Now</strong> above,<br>
            or configure auto-scheduling in Settings.</p>
        </div>
        """, unsafe_allow_html=True)
        if nxt:
            time.sleep(REFRESH_INTERVAL)
            st.rerun()
        return

    # ── Error from last scan ───────────────────────────────────────────────────
    if error and not is_scanning:
        st.error(f"❌ Scan failed: {error}")

    # ── Progress bar ──────────────────────────────────────────────────────────
    if p:
        _progress_bar(
            p.get("progress_percent", 0),
            phase if is_scanning else "COMPLETE",
            p.get("message", "Processing..."),
            done=(complete and not is_scanning),
        )

    # ── Active target card ────────────────────────────────────────────────────
    if is_scanning and p.get("current_ip"):
        _target_card(
            p["current_ip"],
            p.get("current_host", 0),
            p.get("total_hosts", 0),
        )

    # ── Live stat cards ───────────────────────────────────────────────────────
    if p:
        _stat_cards(p)

    # ── Completed hosts list (grows in real-time) ─────────────────────────────
    hosts_done = p.get("hosts_done", [])
    if hosts_done:
        prefix = "🔄" if is_scanning else "✅"
        st.markdown(
            f'<div class="section-title">{prefix} SCANNED HOSTS</div>',
            unsafe_allow_html=True,
        )
        for host in hosts_done:
            _host_row(host)

    # ── Scan complete banner + next-run countdown ─────────────────────────────
    if complete and not is_scanning:
        _complete_banner(p)

        nxt = next_scan_time(cfg)
        if nxt:
            h, m, s = time_until(nxt)
            if h + m + s > 0:
                _countdown_banner(nxt, cfg)
            else:
                st.info("⏰ Schedule elapsed — starting next scan...")
                if launch_worker(ip_range):
                    time.sleep(0.6)
                    st.rerun()

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Run Again", use_container_width=True, type="primary"):
                if launch_worker(ip_range):
                    st.rerun()
        with col2:
            if st.button("📊 Dashboard", use_container_width=True):
                st.switch_page("app.py")
        with col3:
            if st.button("⚙️ Settings", use_container_width=True, key="settings_bottom"):
                st.switch_page("pages/settings.py")

        if nxt:
            time.sleep(REFRESH_INTERVAL)
            st.rerun()
        return

    # ── Auto-refresh while scan is running ───────────────────────────────────
    if is_scanning:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

render_navigation()
if __name__ == "__main__":
    main()