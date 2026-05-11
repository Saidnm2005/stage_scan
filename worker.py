"""
worker.py — Headless background scanner for NetAudit
=====================================================
Writes scan_progress.json at every step so the Streamlit UI
can read real-time progress without sharing a process.

Usage:
    python worker.py                       # runs forever (systemd mode)
    python worker.py --once                # single scan then exit
    python worker.py --range 10.0.0.0/24  # override IP range
"""

import time
import json
import os
import sys
import argparse
import logging
from datetime import datetime, timedelta

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("worker.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("pfe-scanner")

# ─── Paths ────────────────────────────────────────────────────────────────────
SETTINGS_FILE  = "general_settings.json"
SCAN_LOG_FILE  = "scan_log.json"
PROGRESS_FILE  = "scan_progress.json"   # ← UI reads this


# ─── Progress writer ─────────────────────────────────────────────────────────
# This is the bridge between worker.py and live_scan.py.
# Every time something meaningful happens, call _progress(**kwargs).
# live_scan.py polls this file every 2 seconds.

def _progress(**kwargs) -> None:
    """Merge kwargs into the progress file atomically."""
    current = {}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE) as f:
                current = json.load(f)
        except Exception:
            current = {}
    current.update(kwargs)
    current["updated_at"] = datetime.now().isoformat()
    try:
        # Write to a temp file first, then rename — prevents partial reads
        tmp = PROGRESS_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(current, f, indent=2)
        os.replace(tmp, PROGRESS_FILE)
    except Exception as exc:
        log.warning("Could not write progress file: %s", exc)


def _reset_progress(ip_range: str) -> None:
    """Start fresh progress state for a new scan."""
    try:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
    except Exception:
        pass
    _progress(
        phase            = "init",
        message          = "Initialising scan engine…",
        ip_range         = ip_range,
        progress_percent = 0,
        total_hosts      = 0,
        current_host     = 0,
        current_ip       = "",
        total_services   = 0,
        total_vulns      = 0,
        hosts_done       = [],   # list of {ip, vulns, services, asset_id}
        complete         = False,
        error            = None,
        scan_id          = None,
        started_at       = datetime.now().isoformat(),
        finished_at      = None,
    )


# ─── Config helpers ───────────────────────────────────────────────────────────

def load_config() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as exc:
            log.warning("Could not read config: %s", exc)
    return {}


def save_config(cfg: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except IOError as exc:
        log.warning("Could not save config: %s", exc)


def log_scan(data: dict) -> None:
    try:
        history = []
        if os.path.exists(SCAN_LOG_FILE):
            with open(SCAN_LOG_FILE) as f:
                history = json.load(f)
        history.append(data)
        history = history[-50:]
        with open(SCAN_LOG_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as exc:
        log.warning("Could not write scan log: %s", exc)


def sleep_interval(cfg: dict) -> float:
    interval = cfg.get("interval", 24)
    unit     = cfg.get("unit", "Hours")
    return interval * {"Minutes": 60, "Hours": 3600, "Days": 86400}.get(unit, 3600)


# ─── API helpers ──────────────────────────────────────────────────────────────

def _create_asset(ip: str, host_detail: dict) -> str | None:
    from APi.AssetsAPi import add_asset, get_assets
    from APi.known_assets_api import check_existing_asset
    from APi.alert_api import add_alert

    mac      = host_detail.get("mac", "N/A")
    hostname = host_detail.get("hostname", "Unknown")
    vendor   = host_detail.get("vendor",   "Unknown")

    resp = add_asset({
        "ip_address":  ip,
        "mac_address": mac,
        "hostname":    hostname,
        "vendor":      vendor,
        "status":      "active",
        "trust_level": "pending",
    })

    asset_id = None
    if isinstance(resp, dict):
        asset_id = (resp.get("data") or {}).get("id") or resp.get("id")

    if not asset_id:
        assets = (get_assets() or {}).get("data", [])
        asset_id = next((a["id"] for a in assets if a.get("ip_address") == ip), None)

    if not asset_id:
        log.warning("  Could not create/find asset for %s", ip)
        return None

    time.sleep(0.3)

    severity = "HIGH"
    if not mac or mac == "N/A":
        severity = "MEDIUM"
    elif check_existing_asset(mac):
        return asset_id

    add_alert({
        "asset_id": asset_id,
        "type":     "unknown_device",
        "severity": severity,
        "message":  (
            f"Unknown device: asset={asset_id}, MAC={mac}, "
            f"IP={ip}, host={hostname}, vendor={vendor}"
        ),
        "resolved": False,
    })
    log.info("  Alert raised for unknown device %s (MAC: %s)", ip, mac)
    return asset_id


def _register_service(asset_id: str, port_info: dict, protocol: str) -> str | None:
    from APi.servicesAPi import add_service
    try:
        resp = add_service({
            "asset_id":     asset_id,
            "port":         port_info.get("port"),
            "protocol":     protocol,
            "service_name": port_info.get("product", "").strip(),
            "version":      port_info.get("version", "").strip(),
        })
        if resp and not resp.get("error"):
            return (resp.get("data") or {}).get("id")
    except Exception as exc:
        log.debug("  register_service error: %s", exc)
    return None


def _save_vuln(v: dict) -> str | None:
    from APi.vulnAPi import get_vulnerability_by_cve, add_vulnerability

    cve_id = v.get("id")
    if isinstance(cve_id, dict):
        cve_id = cve_id.get("value")
    if not cve_id:
        return None

    try:
        existing = get_vulnerability_by_cve(cve_id)
        if existing and not existing.get("error"):
            eid = (existing.get("data") or {}).get("id")
            if eid:
                return eid
    except Exception:
        pass

    try:
        cvss = float(v.get("cvssScore"))
    except (TypeError, ValueError):
        cvss = None

    severity = (v.get("severity") or "UNKNOWN").upper()
    if severity in ("N/A", ""):
        severity = "UNKNOWN"

    try:
        resp = add_vulnerability({
            "cve_id":         cve_id,
            "description":    str(v.get("description", ""))[:500],
            "severity":       severity,
            "cvss_score":     cvss,
            "published_date": v.get("published") or v.get("publishedDate"),
        })
        if resp and not resp.get("error"):
            return (resp.get("data") or {}).get("id")
    except Exception as exc:
        log.debug("  save_vuln error for %s: %s", cve_id, exc)
    return None


def _link_service_vuln(service_id: str, vuln_id: str) -> None:
    if not (service_id and vuln_id):
        return
    try:
        from APi.service_vuln import add_service_vulnerability
        add_service_vulnerability({"service_id": service_id, "vulnerability_id": vuln_id})
    except Exception as exc:
        log.debug("  link_service_vuln error: %s", exc)


# ─── Core scan (writes progress at every step) ────────────────────────────────

def run_single_scan(ip_range: str) -> dict:
    from nmap_scan import discover_network, scan_host_auto
    from CVE_Matching import run_vuln_scan
    from APi.scan_result_api import add_scan_result
    import APi.scaniAPi as scaniAPI

    # Reset the progress file for this run
    _reset_progress(ip_range)
    log.info("=== Scan started | range: %s ===", ip_range)

    # ── Create DB scan record ─────────────────────────────────────────────────
    scan_id = None
    try:
        resp = scaniAPI.add_scan({
            "ip_range": ip_range,
            "status":   "running",
            "start_at": datetime.now().isoformat(),
        })
        if resp and not resp.get("error"):
            scan_id = (resp.get("data") or {}).get("id")
            log.info("Scan record created: %s", scan_id)
    except Exception as exc:
        log.warning("Could not create scan record: %s", exc)

    _progress(scan_id=scan_id)

    # ── Phase 1: Discovery ────────────────────────────────────────────────────
    _progress(phase="discovery", message="Pinging network — discovering active hosts…",
              progress_percent=5)
    log.info("Phase 1 — host discovery…")

    raw          = discover_network(ip_range)
    active_hosts = [h for h in (raw or []) if h.get("state") == "up"]

    if not active_hosts:
        log.warning("No active hosts found.")
        _progress(phase="error", error="No active hosts found in range.",
                  complete=True, progress_percent=100)
        return {"hosts": 0, "services": 0, "vulnerabilities": 0}

    log.info("Found %d active host(s).", len(active_hosts))
    _progress(total_hosts=len(active_hosts),
              message=f"Found {len(active_hosts)} active host(s) — starting port scans…")

    total_services = total_vulns = 0
    stored_assets: list[str] = []
    hosts_done: list[dict]   = []

    # ── Phase 2: Per-host scan ────────────────────────────────────────────────
    for idx, host in enumerate(active_hosts):
        ip  = host["ip"]
        pct = 10 + int((idx / len(active_hosts)) * 85)

        _progress(
            phase            = "scanning",
            progress_percent = pct,
            current_host     = idx + 1,
            current_ip       = ip,
            message          = f"Port-scanning {ip}  [{idx + 1} / {len(active_hosts)}]…",
        )
        log.info("Phase 2 — scanning %s (%d/%d)…", ip, idx + 1, len(active_hosts))

        # ── Scan the host ─────────────────────────────────────────────────────
        try:
            raw_data    = scan_host_auto(ip)
            host_detail = (raw_data[0] if isinstance(raw_data, list) and raw_data else raw_data) or {}
        except Exception as exc:
            log.error("  scan_host_auto failed for %s: %s", ip, exc)
            _progress(message=f"⚠ Could not scan {ip}: {exc}")
            continue

        if not isinstance(host_detail, dict):
            continue

        # ── Create asset ──────────────────────────────────────────────────────
        _progress(message=f"Registering asset {ip} in database…")
        asset_id = _create_asset(ip, host_detail)
        if not asset_id:
            continue

        if scan_id and asset_id not in stored_assets:
            try:
                r = add_scan_result({"scan_id": scan_id, "asset_id": asset_id})
                if r and not r.get("error"):
                    stored_assets.append(asset_id)
            except Exception:
                pass

        # ── Services & CVEs ───────────────────────────────────────────────────
        host_vulns    = []
        host_services = 0

        for proto in host_detail.get("protocols", []):
            for port_info in proto.get("ports", []):
                name    = port_info.get("product", "").strip()
                version = port_info.get("version", "").strip()
                port    = port_info.get("port", "?")

                if not (name and version):
                    continue

                total_services += 1
                host_services  += 1

                _progress(
                    total_services = total_services,
                    message        = f"Checking CVEs for {name} {version} on {ip}:{port}…",
                )

                service_id = _register_service(asset_id, port_info, proto.get("protocol", "tcp"))

                try:
                    raw_vulns = run_vuln_scan(name, version)
                    if isinstance(raw_vulns, dict):
                        all_vulns = [v for vlist in raw_vulns.values()
                                     if isinstance(vlist, list)
                                     for v in vlist if isinstance(v, dict)]
                    elif isinstance(raw_vulns, list):
                        all_vulns = [v for v in raw_vulns if isinstance(v, dict)]
                    else:
                        all_vulns = []
                except Exception as exc:
                    log.debug("  run_vuln_scan error (%s %s): %s", name, version, exc)
                    all_vulns = []

                if all_vulns:
                    total_vulns += len(all_vulns)
                    host_vulns.extend(all_vulns)
                    log.info("  %s:%s — %d CVE(s) found", port, name, len(all_vulns))
                    _progress(total_vulns=total_vulns,
                              message=f"Found {len(all_vulns)} CVE(s) for {name} {version}")

                for v in all_vulns:
                    vid = _save_vuln(v)
                    _link_service_vuln(service_id, vid)

        # ── Append completed host to progress ─────────────────────────────────
        hosts_done.append({
            "ip":       ip,
            "hostname": host_detail.get("hostname", ""),
            "vendor":   host_detail.get("vendor", ""),
            "services": host_services,
            "vulns":    len(host_vulns),
            "asset_id": asset_id,
            # Compact vuln list for the UI (top 10 only)
            "vuln_list": [
                {
                    "cve_id":      (v.get("id") if not isinstance(v.get("id"), dict)
                                    else v["id"].get("value", "?")),
                    "cvss":        v.get("cvssScore"),
                    "severity":    v.get("severity", "UNKNOWN"),
                    "description": str(v.get("description", ""))[:120],
                }
                for v in host_vulns[:10]
            ],
        })
        _progress(hosts_done=hosts_done)

    # ── Phase 3: Finalise ─────────────────────────────────────────────────────
    _progress(
        phase            = "complete",
        complete         = True,
        progress_percent = 100,
        total_vulns      = total_vulns,
        total_services   = total_services,
        current_ip       = "",
        finished_at      = datetime.now().isoformat(),
        message          = (
            f"Scan complete — {len(active_hosts)} host(s), "
            f"{total_services} service(s), {total_vulns} CVE(s)"
        ),
    )

    if scan_id:
        try:
            scaniAPI.update_scan(scan_id, {
                "status":      "completed",
                "finished_at": datetime.now().isoformat(),
            })
        except Exception as exc:
            log.warning("Could not mark scan as completed: %s", exc)

    summary = {
        "timestamp":       datetime.now().isoformat(),
        "ip_range":        ip_range,
        "hosts":           len(active_hosts),
        "services":        total_services,
        "vulnerabilities": total_vulns,
    }
    log_scan(summary)
    log.info("=== Scan complete | hosts=%d services=%d CVEs=%d ===",
             len(active_hosts), total_services, total_vulns)

    # Persist for settings page
    cfg = load_config()
    cfg.update({
        "last_scan_completed": datetime.now().isoformat(),
        "last_scan_hosts":     len(active_hosts),
        "last_scan_vulns":     total_vulns,
    })
    save_config(cfg)

    return summary


# ─── Scheduler loop ───────────────────────────────────────────────────────────

def run_forever(ip_range: str, cfg: dict) -> None:
    interval_sec = sleep_interval(cfg)
    log.info("Scheduler started — interval: %.0f s (%.1f h)",
             interval_sec, interval_sec / 3600)

    while True:
        try:
            run_single_scan(ip_range)
            cfg = load_config()
        except KeyboardInterrupt:
            log.info("Interrupted — shutting down.")
            break
        except Exception as exc:
            log.error("Scan failed: %s", exc, exc_info=True)
            _progress(phase="error", error=str(exc), complete=True)

        interval_sec = sleep_interval(cfg)
        next_run     = datetime.now() + timedelta(seconds=interval_sec)
        log.info("Next scan at %s — sleeping…", next_run.strftime("%Y-%m-%d %H:%M:%S"))
        _progress(
            phase   = "sleeping",
            message = f"Next scan at {next_run.strftime('%Y-%m-%d %H:%M:%S')}",
            complete= True,
        )

        try:
            time.sleep(interval_sec)
        except KeyboardInterrupt:
            log.info("Interrupted during sleep — shutting down.")
            break


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="NetAudit headless background scanner")
    parser.add_argument("--once",  action="store_true", help="Single scan then exit")
    parser.add_argument("--range", dest="ip_range",    help="Override IP range")
    args = parser.parse_args()

    cfg      = load_config()
    ip_range = args.ip_range or cfg.get("target_ip")

    if not ip_range:
        log.error("No IP range configured. Set target_ip in %s or pass --range.", SETTINGS_FILE)
        sys.exit(1)

    if args.once:
        run_single_scan(ip_range)
    else:
        run_forever(ip_range, cfg)


if __name__ == "__main__":
    main()