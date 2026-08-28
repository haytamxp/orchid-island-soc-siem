# Playbook: Credential Attack

## Objective

Detect, contain, investigate, and remediate attempts to obtain or abuse
credentials.

## 1. Triage

Review:

- username or account targeted;
- source IP;
- destination host;
- authentication protocol;
- authentication failures;
- successful logins after failures;
- account lockouts;
- unusual login locations;
- unusual user agents or clients;
- authentication timestamps.

Look for patterns such as:

- repeated authentication failures;
- password spraying;
- credential stuffing;
- suspicious service-account use;
- abnormal successful authentication following failures.

## 2. Immediate Containment

Depending on confidence:

1. Rate-limit or block confirmed malicious sources.
2. Temporarily disable compromised accounts.
3. Force password reset for affected accounts.
4. Revoke active sessions or tokens where compromise is suspected.
5. Increase authentication logging and monitoring.

Avoid disabling critical service accounts without coordination.

## 3. Investigation

Correlate:

- authentication logs;
- VPN activity;
- Active Directory events;
- Wazuh telemetry;
- endpoint login events;
- MFA events;
- source IP reputation;
- successful authentication following failures.

Determine whether credentials were:

- only attacked;
- successfully compromised;
- reused on another system;
- used for lateral movement.

## 4. Remediation

Apply:

1. Strong password and credential policies.
2. MFA for appropriate accounts.
3. Account lockout or adaptive throttling.
4. Privileged-account separation.
5. Removal of stale accounts.
6. Credential rotation for confirmed compromise.

## 5. Recovery

Confirm:

- compromised credentials are reset;
- suspicious sessions are revoked;
- persistence is removed;
- affected systems are monitored;
- authentication anomalies have stopped.

## 6. Validation

Verify that:

- attack attempts decrease or stop;
- no unauthorized successful login remains;
- affected accounts are protected;
- monitoring detects repeated attempts.

## 7. ATT&CK Context

T1110 — Brute Force may be relevant when repeated credential guessing,
password spraying, or credential stuffing is supported by the evidence.

Do not automatically assign T1110 to every credential-related alert.