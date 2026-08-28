   -- Users (authentication)
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(100) NOT NULL UNIQUE,
       password VARCHAR(255) NOT NULL,        -- hashed (werkzeug check_password_hash)
       mfa_token VARCHAR(255),                -- SHA-256 hash of MFA token
       role VARCHAR(50) DEFAULT 'admin',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Raw security events (from Wazuh/Suricata agents)
   CREATE TABLE events (
       id INT AUTO_INCREMENT PRIMARY KEY,
       timestamp DATETIME NOT NULL,
       hostname VARCHAR(255) NOT NULL,
       src_ip VARCHAR(45) NOT NULL,
       dest_ip VARCHAR(45),
       dest_port INT,
       category VARCHAR(100),
       rule_id VARCHAR(50),
       severity VARCHAR(20),                  -- Low / Medium / High / Critical
       action_taken VARCHAR(50),              -- Allowed / Logged / Dropped / Blocked / Killed
       INDEX idx_timestamp (timestamp),
       INDEX idx_severity (severity)
   );

   -- Qualified alerts (post risk-scoring)
   CREATE TABLE alerts (
       id INT AUTO_INCREMENT PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       severity VARCHAR(20) NOT NULL,
       description TEXT,
       rule_id VARCHAR(50),
       timestamp DATETIME NOT NULL,
       xgboost_probability FLOAT DEFAULT 0,   -- kept for continuity; may become
                                                -- a generic "risk_score" if the
                                                -- new repo drops XGBoost naming
       analyst_assigned VARCHAR(100) DEFAULT 'Unassigned',
       status VARCHAR(20) DEFAULT 'New',      -- New / Acknowledged / Resolved
       ai_report_id INT,
       INDEX idx_status (status),
       INDEX idx_severity (severity)
   );

   -- AI-generated incident reports
   CREATE TABLE ai_reports (
       id INT AUTO_INCREMENT PRIMARY KEY,
       alert_id INT,
       generated_at DATETIME NOT NULL,
       markdown_content TEXT NOT NULL,
       FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
   );

   -- Monitored agents (Wazuh fleet)
   CREATE TABLE agents (
       id VARCHAR(100) PRIMARY KEY,           -- e.g. "agt-webserver01"
       name VARCHAR(255) NOT NULL,
       ip_address VARCHAR(45),
       status VARCHAR(20) DEFAULT 'Offline',  -- Online / Offline
       os VARCHAR(100),
       last_keep_alive DATETIME,
       cpu_usage FLOAT DEFAULT 0,
       ram_usage FLOAT DEFAULT 0
   );

   -- File Integrity Monitoring events
   CREATE TABLE fim_events (
       id INT AUTO_INCREMENT PRIMARY KEY,
       hostname VARCHAR(255),
       timestamp DATETIME NOT NULL,
       file_path VARCHAR(500),
       change_type VARCHAR(50),               -- added / modified / deleted
       INDEX idx_hostname (hostname),
       INDEX idx_timestamp (timestamp)
   );

   -- Detected vulnerabilities (CVEs)
   CREATE TABLE vulnerabilities (
       id VARCHAR(50) PRIMARY KEY,            -- e.g. CVE identifier or internal ID
       hostname VARCHAR(255),
       cve_id VARCHAR(50),
       description TEXT,
       cvss_score FLOAT DEFAULT 0,
       status VARCHAR(20) DEFAULT 'Open',      -- Open / Patched / Ignored
       detected_at DATETIME
   );

   -- Threat Intelligence indicators of compromise
   CREATE TABLE threat_intel_iocs (
       id VARCHAR(50) PRIMARY KEY,             -- e.g. "ioc-<timestamp>"
       value VARCHAR(500) NOT NULL,
       type VARCHAR(50) NOT NULL,              -- IP / Domain / Hash
       threat_actor VARCHAR(255) DEFAULT 'Unknown',
       description TEXT,
       date_added DATETIME NOT NULL
   );