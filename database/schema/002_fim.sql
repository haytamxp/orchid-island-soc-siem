-- ============================================================
-- Orchid Island SOC/SIEM
-- FIM schema upgrade
-- ============================================================

-- Baseline = trusted state of a monitored file.
CREATE TABLE IF NOT EXISTS fim_baselines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    sha256 CHAR(64) NOT NULL,
    file_size BIGINT UNSIGNED NOT NULL DEFAULT 0,
    mode VARCHAR(32) NULL,
    owner_name VARCHAR(255) NULL,
    monitored BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_fim_baseline_host_path (hostname, file_path),
    INDEX idx_fim_baseline_hostname (hostname),
    INDEX idx_fim_baseline_monitored (monitored)
);

-- Upgrade the existing event table with integrity evidence.
ALTER TABLE fim_events
    ADD COLUMN old_hash CHAR(64) NULL,
    ADD COLUMN new_hash CHAR(64) NULL,
    ADD COLUMN old_size BIGINT UNSIGNED NULL,
    ADD COLUMN new_size BIGINT UNSIGNED NULL,
    ADD COLUMN severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
    ADD COLUMN actor VARCHAR(255) NULL,
    ADD COLUMN process_name VARCHAR(255) NULL,
    ADD COLUMN agent_id VARCHAR(100) NULL,
    ADD COLUMN details TEXT NULL;

CREATE INDEX idx_fim_events_change_type
    ON fim_events (change_type);

CREATE INDEX idx_fim_events_severity
    ON fim_events (severity);

CREATE INDEX idx_fim_events_file_path
    ON fim_events (file_path);

CREATE INDEX idx_fim_events_agent_id
    ON fim_events (agent_id);

-- Useful lookup index for the most recent event for a file.
CREATE INDEX idx_fim_events_host_file_time
    ON fim_events (hostname, file_path, timestamp);