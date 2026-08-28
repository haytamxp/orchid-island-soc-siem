# Playbook: Network and Service Scanning

## Objective

Identify reconnaissance and scanning activity, determine its scope and
intent, and reduce unnecessary exposure.

## 1. Triage

Review:

- source IP;
- destination hosts;
- destination ports;
- protocol;
- request frequency;
- number of unique targets;
- number of unique ports;
- response patterns;
- scan duration.

Indicators include:

- sequential port probing;
- connection attempts across many hosts;
- high counts of failed connections;
- rapid enumeration;
- repeated service discovery requests.

## 2. Immediate Containment

When scanning is confirmed or highly suspicious:

1. Rate-limit the source.
2. Block the source where operationally appropriate.
3. Reduce exposure of unnecessary services.
4. Increase monitoring for the targeted hosts.
5. Preserve scan telemetry for correlation.

## 3. Investigation

Determine:

- whether the activity is internal or external;
- whether the source belongs to an approved scanner;
- what services were identified;
- whether scanning was followed by exploitation;
- whether privileged or sensitive systems were targeted.

Check for follow-on alerts such as:

- exploitation;
- authentication attacks;
- malware delivery;
- suspicious remote access.

## 4. Remediation

Apply:

1. Close unnecessary ports and services.
2. Restrict exposed management interfaces.
3. Segment sensitive systems.
4. Apply firewall/WAF access controls.
5. Maintain an approved scanning-source allow-list.
6. Review external attack-surface exposure regularly.

## 5. Recovery

Confirm:

- unauthorized scanning has stopped;
- exposed services are minimized;
- targeted systems show no evidence of compromise;
- follow-on activity was investigated.

## 6. Validation

Verify:

- approved scanners remain functional;
- unexpected scanning is detected;
- alerts contain source, target, port, and timing information;
- correlated exploitation attempts are escalated.

## 7. ATT&CK Context

T1046 — Network Service Scanning is relevant when the observed activity
demonstrates discovery of network services or ports.

Only assign the technique when the evidence supports it.