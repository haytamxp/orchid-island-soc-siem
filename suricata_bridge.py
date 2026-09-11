#!/usr/bin/env python3
"""
suricata_bridge.py

Tails Suricata's eve.json log, picks out "alert" events, and forwards
each one to a local Flask API (/api/events) as they happen.

Usage:
    python3 suricata_bridge.py

Config via environment variables (all optional, sensible defaults below):
    EVE_JSON_PATH   - path to Suricata's eve.json      (default: /var/log/suricata/eve.json)
    API_URL         - full URL of the ingestion route  (default: http://127.0.0.1:5000/api/events)
    STATE_FILE      - where to remember read position  (default: ./.suricata_bridge_state)
    POLL_INTERVAL   - seconds between checks for new lines (default: 1.0)
"""

import os
import json
import time
import socket
import sys

import requests

EVE_JSON_PATH = os.environ.get("EVE_JSON_PATH", "/var/log/suricata/eve.json")
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000/api/events")
STATE_FILE = os.environ.get("STATE_FILE", ".suricata_bridge_state")
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "1.0"))

HOSTNAME = socket.gethostname()

# Suricata alert.severity: 1 = high, 2 = medium, 3 = low (lower number = more severe)
SEVERITY_MAP = {1: "High", 2: "Medium", 3: "Low"}


def load_last_position() -> int:
    """Read the byte offset we last left off at, if any."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return int(f.read().strip() or 0)
        except (ValueError, OSError):
            return 0
    return 0


def save_last_position(pos: int) -> None:
    with open(STATE_FILE, "w") as f:
        f.write(str(pos))


def eve_alert_to_event(raw: dict) -> dict | None:
    """Convert a raw Suricata eve.json 'alert' record into our API's schema.
    Returns None if the record isn't a usable alert."""
    if raw.get("event_type") != "alert":
        return None

    alert = raw.get("alert", {})
    severity_num = alert.get("severity", 2)

    return {
        "hostname": HOSTNAME,
        "src_ip": raw.get("src_ip", "unknown"),
        "dest_ip": raw.get("dest_ip", "unknown"),
        "dest_port": raw.get("dest_port", 0) or 0,
        "category": alert.get("category") or alert.get("signature", "Unknown"),
        "rule_id": str(alert.get("signature_id", "unknown")),
        "severity": SEVERITY_MAP.get(severity_num, "Medium"),
        "action_taken": "detected",  # Suricata IDS mode only detects, doesn't block
    }


def send_event(event: dict) -> None:
    try:
        resp = requests.post(API_URL, json=event, timeout=5)
        if resp.status_code == 201:
            print(f"[sent] {event['category']} ({event['severity']}) "
                  f"{event['src_ip']} -> {event['dest_ip']}:{event['dest_port']}")
        else:
            print(f"[warn] API returned {resp.status_code}: {resp.text}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"[error] Failed to POST event: {e}", file=sys.stderr)


def follow(path: str, start_pos: int):
    """Generator that yields new lines appended to `path`, handling
    the case where the file doesn't exist yet or gets rotated."""
    f = None
    pos = start_pos

    while True:
        if f is None:
            try:
                f = open(path, "r")
                f.seek(pos)
            except FileNotFoundError:
                time.sleep(POLL_INTERVAL)
                continue

        line = f.readline()
        if line:
            pos = f.tell()
            yield line, pos
        else:
            # Detect log rotation: if the file shrank, reopen from the start
            try:
                if os.path.getsize(path) < pos:
                    f.close()
                    f = None
                    pos = 0
                    continue
            except OSError:
                f.close()
                f = None
                continue
            time.sleep(POLL_INTERVAL)


def main():
    print(f"Watching:  {EVE_JSON_PATH}")
    print(f"Forwarding alerts to: {API_URL}")
    print(f"Hostname tag: {HOSTNAME}")
    print("Press Ctrl+C to stop.\n")

    start_pos = load_last_position()

    try:
        for line, pos in follow(EVE_JSON_PATH, start_pos):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue  # partially-written line, skip

            event = eve_alert_to_event(raw)
            if event:
                send_event(event)

            save_last_position(pos)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()