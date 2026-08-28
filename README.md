# Orchid Island SOC/SIEM

## Intelligent Security Monitoring, Detection and Behavioral Analysis Platform

> **Project:** Orchid Island Real Estate
> **Client:** Orchid Island Real Estate — Direction Générale
> **Technical team:** Nezha HALLA & Haytam RAGUEB
> **Delivery target:** 20 September 2026
> **Current phase:** Project takeover and technical audit

---

## 1. Project Overview

Orchid Island SOC/SIEM is a cybersecurity platform designed to centralize security events, analyze them, generate risk assessments, notify the supervision team, and support automated security response.

The project is a **continuation and finalization of an existing platform** developed by a previous team.

The objective is not to rebuild the platform from scratch, but to:

* audit the existing implementation;
* recover and document the current architecture;
* identify broken, incomplete, or disconnected components;
* restore the end-to-end security event pipeline;
* connect the React dashboard to the Flask backend;
* integrate the platform with the company's web environment;
* validate existing automated response mechanisms;
* develop a behavioral analysis module;
* document the final architecture, limitations, and operating procedures.

---

## 2. Project Objectives

### Phase 1 — Finalization and Integration

The first phase focuses on obtaining a functional end-to-end SOC/SIEM platform.

Target flow:

```text
Security Sources
      |
      v
Wazuh / Suricata
      |
      v
Collectors / Agents
      |
      v
Flask REST API
      |
      +--------------------+
      |                    |
      v                    v
    MySQL              Risk Engine
                          |
                          v
                    AI / RAG Analysis
                          |
                          v
                 Reports / Alerts
                          |
              +-----------+-----------+
              |                       |
              v                       v
       React Dashboard       Telegram / Email
```

Phase 1 objectives include:

* dashboard ↔ backend API integration;
* authentication validation;
* event and alert visualization;
* database and API flow validation;
* Wazuh/Suricata ingestion validation;
* risk scoring validation;
* AI report generation validation;
* notification validation;
* integration with the company's web environment;
* regression testing of existing security mechanisms.

---

## 3. Phase 2 — Behavioral Analysis

The second phase introduces behavioral security analysis.

The module will analyze relevant behavioral signals such as:

* login time;
* login frequency;
* source IP;
* access patterns;
* authentication failures;
* unusual activity;
* deviations from historical user behavior.

The system will calculate a behavioral risk score for a user or session.

Conceptually:

```text
User / Session Activity
          |
          v
Feature Extraction
          |
          v
Behavioral Model
          |
          v
Risk Score
          |
      +---+---+
      |       |
      v       v
   Alert    Response
             |
       +-----+-----+
       |           |
       v           v
    Telegram    IP/User Block
```

The final model and detection strategy will be selected after analysis of the available data and documented with its assumptions, advantages, limitations, and validation results.

---

## 4. Existing Technology Stack

The project specification identifies the following technologies:

| Component                | Technology                |
| ------------------------ | ------------------------- |
| Host monitoring          | Wazuh                     |
| Network monitoring       | Suricata                  |
| Search / observability   | OpenSearch                |
| Backend                  | Python / Flask            |
| Database                 | MySQL                     |
| Frontend                 | React / TypeScript / Vite |
| Risk scoring             | XGBoost                   |
| LLM / RAG                | Ollama / Llama 3.2        |
| Threat intelligence      | VirusTotal                |
| Notifications            | Telegram / Email          |
| Automated response       | IPTables                  |
| External web environment | Cloudflare                |
| Operating system         | Ubuntu Linux              |

These technologies describe the **existing/project-target stack**. Their actual implementation status will be established during the takeover audit.

---

## 5. Repository Structure

```text
orchid-island-soc-siem/
│
├── backend/                    # Flask REST API
├── frontend/                   # React / TypeScript dashboard
├── agents/                     # Wazuh / Suricata collection agents
│
├── ai/                         # AI and machine-learning components
│   ├── xgboost/
│   ├── behavioral/
│   ├── rag/
│   └── ollama/
│
├── response/                   # Automated security response
│   ├── iptables/
│   ├── telegram/
│   └── email/
│
├── integrations/               # External security integrations
│   ├── cloudflare/
│   ├── virustotal/
│   └── wazuh/
│
├── database/                   # Database schema and migrations
│   ├── schema/
│   ├── migrations/
│   └── seeds/
│
├── docs/                       # Technical and project documentation
│   ├── architecture/
│   ├── phase-1/
│   ├── phase-2/
│   ├── deployment/
│   └── security/
│
├── tests/                      # Unit / integration / validation tests
├── scripts/                    # Development and operational scripts
│
├── .github/                    # GitHub workflows and project automation
│   └── workflows/
│
├── .env.example
├── .gitignore
├── SECURITY.md
└── README.md
```

---

## 6. Project Timeline

| Milestone | Period         | Objective                                       |
| --------- | -------------- | ----------------------------------------------- |
| M0        | 24–29 Aug 2026 | Takeover, audit and environment discovery       |
| M1        | 30 Aug–5 Sep   | Dashboard ↔ backend integration                 |
| M2        | 6–10 Sep       | Website / Cloudflare integration and validation |
| M3        | 11–16 Sep      | Behavioral AI module                            |
| M4        | 17–18 Sep      | Automated response integration                  |
| M5        | 19–20 Sep      | Final tests, documentation and delivery         |

---

## 7. Acceptance Criteria

The project is considered functionally complete when:

* the dashboard receives real backend data;
* events and alerts can be visualized;
* the main ingestion pipeline works end to end;
* critical alerts trigger the expected notification mechanism;
* the behavioral module detects the agreed test scenarios;
* the required automated response is executed safely;
* existing functionality does not regress;
* technical documentation is complete;
* the final demonstration is validated by the client.

---

## 8. Security Requirements

This repository may contain code related to security monitoring and automated response.

The following must **never** be committed:

* API keys;
* passwords;
* JWT secrets;
* Telegram bot tokens;
* Cloudflare credentials;
* VirusTotal API keys;
* private keys or certificates;
* production log exports;
* real user behavioral datasets containing sensitive information.

Use `.env.example` as the configuration template.

---

## 9. Development Principles

The implementation follows these principles:

### Preserve before replacing

Existing functionality must be understood before being rewritten.

### Verify before trusting

A component mentioned in the previous project documentation is not considered functional until it has been tested.

### Security by design

Authentication, authorization, secrets management, input validation, logging and failure handling are part of the implementation rather than post-development additions.

### Observable behavior

Important actions should produce useful logs and measurable results.

### Reproducibility

Development environments, database structures and deployment procedures must be documented.

---

## 10. Current Status

### M0 — Takeover and Audit

**Status: In progress**

The repository is currently being prepared for the technical takeover of the previous implementation.

The next step is to inspect the existing source code, identify the actual architecture, map dependencies, verify the database model, and establish a working baseline before modifying the application.

---

## 11. Documentation

Technical documentation will be maintained under `docs/`.

Important areas include:

* architecture;
* Phase 1 implementation;
* Phase 2 behavioral AI;
* deployment;
* security;
* testing;
* incident/response procedures.

---

## 12. Project Team

**Client / Commanditaire**

M. Dekkak Mohamed — PDG

**Technical team**

Nezha Halla
Haytam Ragueb

---

## 13. Disclaimer

This project is developed for the authorized security monitoring and protection of Orchid Island Real Estate infrastructure.

All security testing, automated response, traffic analysis, IP blocking and external integrations must be performed within the scope authorized by the client.

## 14. Development Setup
### Setting up the Python virtual environment

**Linux / macOS (Ubuntu):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
```