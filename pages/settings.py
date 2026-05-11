import streamlit as st
import json
import os
import subprocess
import ipaddress
from datetime import datetime, timedelta
from ui.navigation import render_navigation
render_navigation()

# ─── Constants ────────────────────────────────────────────────────────────────
SETTINGS_FILE = "general_settings.json"
WORKER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "worker.py")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"target_ip": "10.114.121.0/24", "auto_rerun": False, "interval": 24, "unit": "Hours"}


def save_settings(data: dict) -> bool:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as exc:
        st.error(f"Error saving config: {exc}")
        return False


def validate_ip(ip: str) -> bool:
    try:
        ipaddress.ip_network(ip, strict=False)
        return True
    except ValueError:
        return False


def worker_is_running() -> bool:
    try:
        return subprocess.run(["pgrep", "-f", "worker.py"],
                              capture_output=True).returncode == 0
    except Exception:
        return False


def systemd_service_status() -> str:
    """Returns 'active', 'inactive', 'failed', or 'unknown'."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "pfe-scanner"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def enable_systemd_service() -> bool:
    try:
        subprocess.run(["sudo", "systemctl", "enable", "pfe-scanner"], check=True)
        subprocess.run(["sudo", "systemctl", "start",  "pfe-scanner"], check=True)
        return True
    except Exception:
        return False


def disable_systemd_service() -> bool:
    try:
        subprocess.run(["sudo", "systemctl", "stop",    "pfe-scanner"], check=True)
        subprocess.run(["sudo", "systemctl", "disable", "pfe-scanner"], check=True)
        return True
    except Exception:
        return False


# ─── Page ─────────────────────────────────────────────────────────────────────

def load_settings_page():
    st.title("🛡️ System Configuration")

    config = load_settings()

    with st.container(border=True):

        # ── Network target ────────────────────────────────────────────────────
        st.subheader("📡 Global Network Target")
        target_ip = st.text_input(
            "Default Scan Range",
            value=config.get("target_ip", ""),
            help="Primary target used by both manual launches and the background service.",
        )
        st.divider()

        # ── Schedule ──────────────────────────────────────────────────────────
        st.subheader("⏳ Automation & Scheduling")
        auto_rerun = st.checkbox(
            "Enable Automatic Rescanning",
            value=config.get("auto_rerun", False),
            help="When enabled, the systemd service will re-run the scan automatically on the schedule below.",
        )

        col1, col2 = st.columns(2)
        with col1:
            interval_value = st.number_input("Scan Frequency", min_value=1,
                                             value=config.get("interval", 24))
        with col2:
            units = ["Minutes", "Hours", "Days"]
            interval_unit = st.selectbox("Time Unit", units,
                                         index=units.index(config.get("unit", "Hours")))

        # ── Schedule preview ──────────────────────────────────────────────────
        if auto_rerun:
            st.info(f"⏰ The background service will rescan every {interval_value} {interval_unit}.")

            last_completed = config.get("last_scan_completed")
            if last_completed:
                try:
                    base  = datetime.fromisoformat(last_completed)
                    delta = {"Minutes": timedelta(minutes=interval_value),
                             "Hours":   timedelta(hours=interval_value),
                             "Days":    timedelta(days=interval_value)}[interval_unit]
                    next_run  = base + delta
                    time_left = next_run - datetime.now()

                    st.caption(f"📅 Last scan completed: {base.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.caption(f"⏰ Next scheduled run:  {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

                    if time_left.total_seconds() > 0:
                        h = int(time_left.total_seconds() // 3600)
                        m = int((time_left.total_seconds() % 3600) // 60)
                        s = int(time_left.total_seconds() % 60)
                        st.caption(f"🕐 Time remaining: {h:02d}:{m:02d}:{s:02d}")
                except Exception:
                    pass
        else:
            st.caption("Automatic rescanning is disabled — scans only run when launched manually.")

        st.divider()

        # ── Systemd service status ────────────────────────────────────────────
        st.subheader("🔧 Background Service Status")
        svc_status  = systemd_service_status()
        is_scanning = worker_is_running()

        status_map = {
            "active":   ("🟢", "Active — service is running and will rescan automatically"),
            "inactive": ("⚪", "Inactive — service is stopped"),
            "failed":   ("🔴", "Failed — check: journalctl -u pfe-scanner"),
            "unknown":  ("🟡", "Unknown — deploy the service first: sudo bash deploy_service.sh"),
        }
        icon, label = status_map.get(svc_status, ("🟡", svc_status))
        st.caption(f"{icon} Service: {label}")

        if is_scanning:
            st.success("🔵 A scan is currently in progress.")

        st.divider()

        # ── Last scan summary ─────────────────────────────────────────────────
        if config.get("last_scan_completed"):
            st.subheader("📊 Last Scan Results")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Hosts Scanned",         config.get("last_scan_hosts", 0))
            with c2:
                st.metric("Vulnerabilities Found",  config.get("last_scan_vulns", 0))
            st.caption(f"Completed at: {config.get('last_scan_completed')}")
            st.divider()

        # ── Action buttons ────────────────────────────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Save Configuration", use_container_width=True, type="secondary"):
                if not validate_ip(target_ip):
                    st.error("Invalid IP range — configuration not saved.")
                else:
                    new_cfg = {
                        "target_ip":    target_ip,
                        "auto_rerun":   auto_rerun,
                        "interval":     interval_value,
                        "unit":         interval_unit,
                        "last_updated": datetime.now().isoformat(),
                    }
                    for key in ("last_scan_completed", "last_scan_hosts",
                                "last_scan_vulns", "last_launch"):
                        if config.get(key) is not None:
                            new_cfg[key] = config[key]

                    if save_settings(new_cfg):
                        # Sync systemd service with the toggle
                        if auto_rerun and svc_status != "active":
                            if not enable_systemd_service():
                                st.warning(
                                    "⚠ Settings saved but could not auto-enable the service.\n"
                                    "Run manually: `sudo systemctl enable pfe-scanner && sudo systemctl start pfe-scanner`"
                                )
                        elif not auto_rerun and svc_status == "active":
                            if not disable_systemd_service():
                                st.warning(
                                    "⚠ Settings saved but could not auto-stop the service.\n"
                                    "Run manually: `sudo systemctl stop pfe-scanner && sudo systemctl disable pfe-scanner`"
                                )

                        st.toast("Configuration updated!", icon="✅")
                        st.success("Settings saved successfully!")
                        st.balloons()

        with col2:
            launch_label = "🔄 Scan Already Running" if is_scanning else "🚀 Launch Audit Now"
            if st.button(launch_label, use_container_width=True, type="primary",
                         disabled=is_scanning):
                if not validate_ip(target_ip):
                    st.error("Invalid IP range — please fix before launching.")
                else:
                    # Save settings with launch timestamp
                    new_cfg = {
                        "target_ip":   target_ip,
                        "auto_rerun":  auto_rerun,
                        "interval":    interval_value,
                        "unit":        interval_unit,
                        "last_launch": datetime.now().isoformat(),
                    }
                    for key in ("last_scan_completed", "last_scan_hosts", "last_scan_vulns"):
                        if config.get(key) is not None:
                            new_cfg[key] = config[key]
                    save_settings(new_cfg)

                    # Tell live_scan.py to auto-launch the worker on arrival
                    st.session_state.target_ip      = target_ip
                    st.session_state.scan_requested = True
                    st.toast("Launching audit…", icon="🚀")
                    st.switch_page("pages/live_scan.py")


if __name__ == "__main__":
    load_settings_page()