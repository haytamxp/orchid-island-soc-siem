#!/usr/bin/env python3
"""
wazuh_bridge.py

Tails Wazuh's alerts.json log, and forwards each alert to a local Flask
API (/api/events) as they happen. Same pattern as suricata_bridge.py,
but mapped to Wazuh's alert schema (host-based, not network-based).

Usage:
    python3 wazuh_bridge.py

Config via environment variables (all optional, sensible defaults below):
    ALERTS_JSON_PATH - path to Wazuh's alerts.json   (default: /var/ossec/logs/alerts/alerts.json)
    API_URL          - full URL of the ingestion route (default: http://127.0.0.1:5000/api/events)
    STATE_FILE       - where to remember read position (default: ./.wazuh_bridge_state)
    POLL_INTERVAL    - seconds between checks for new lines (default: 1.0)
    MIN_LEVEL        - minimum rule.level to forward (default: 0, i.e. forward everything)
"""

import os
import json
import time
import sys

import requests

ALERTS_JSON_PATH = os.environ.get("ALERTS_JSON_PATH", "/var/ossec/logs/alerts/alerts.json")
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000/api/events")
STATE_FILE = os.environ.get("STATE_FILE", ".wazuh_bridge_state")
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "1.0"))
MIN_LEVEL = int(os.environ.get("MIN_LEVEL", "0"))

# Wazuh rule.level runs 0-15. Rough 3-tier mapping for our dashboard's severity field.
def map_severity(level: int) -> str:
    if level >= 12:
        return "High"
    if level >= 7:
        return "Medium"
    return "Low"


def load_last_position() -> int:
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


def wazuh_alert_to_event(raw: dict) -> dict | None:
    """Convert a raw Wazuh alerts.json record into our API's schema.
    Returns None if the record can't be mapped (missing required parts)."""
    rule = raw.get("rule", {})
    agent = raw.get("agent", {})

    level = rule.get("level", 0)
    if level < MIN_LEVEL:
        return None

    hostname = agent.get("name", "unknown")
    # Local manager agent (id "000") typically has no "ip" field
    src_ip = agent.get("ip", "127.0.0.1")

    return {
        "hostname": hostname,
        "src_ip": src_ip,
        # Wazuh is host-based, not network-based - there's no real "destination"
        # here. Defaulting to the manager's loopback; this field is not
        # meaningful for Wazuh-sourced events the way it is for Suricata.
        "dest_ip": "127.0.0.1",
        "dest_port": 0,
        "category": rule.get("description", "Unknown"),
        "rule_id": str(rule.get("id", "unknown")),
        "severity": map_severity(level),
        "action_taken": "detected",  # Wazuh manager logs/alerts; no active response configured
    }


def send_event(event: dict) -> None:
    try:
        resp = requests.post(API_URL, json=event, timeout=5)
        if resp.status_code == 201:
            print(f"[sent] {event['category']} (level-mapped: {event['severity']}) "
                  f"host={event['hostname']} src={event['src_ip']}")
        else:
            print(f"[warn] API returned {resp.status_code}: {resp.text}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"[error] Failed to POST event: {e}", file=sys.stderr)


def follow(path: str, start_pos: int):
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
    print(f"Watching:  {ALERTS_JSON_PATH}")
    print(f"Forwarding alerts to: {API_URL}")
    print(f"Minimum rule level forwarded: {MIN_LEVEL}")
    print("Press Ctrl+C to stop.\n")

    start_pos = load_last_position()

    try:
        for line, pos in follow(ALERTS_JSON_PATH, start_pos):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue  # partially-written line, skip

            event = wazuh_alert_to_event(raw)
            if event:
                send_event(event)

            save_last_position(pos)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()