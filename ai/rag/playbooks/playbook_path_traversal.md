# Playbook: Path Traversal

## Objective

Detect, contain, investigate, and remediate attempts to access files or
directories outside the intended application path.

## 1. Triage

Review:

- requested URL or resource path;
- source IP;
- HTTP method;
- target hostname;
- HTTP status code;
- application and web-server logs;
- repeated traversal patterns;
- encoded traversal variants.

Common indicators include:

- `../`
- `..\`
- encoded traversal such as `%2e%2e%2f`;
- attempts to access sensitive locations;
- repeated requests for system files;
- abnormal path normalization behavior.

## 2. Immediate Containment

Depending on confidence and impact:

1. Temporarily block or rate-limit the source.
2. Apply a WAF rule for confirmed malicious traversal patterns.
3. Restrict the affected endpoint if exploitation is ongoing.
4. Preserve relevant application and web-server logs before cleanup.

## 3. Investigation

Determine:

- whether the application normalized the path safely;
- whether a sensitive file was successfully returned;
- whether the response contained credentials or configuration data;
- whether the same source attempted other endpoints;
- whether application privileges allowed access beyond the intended directory.

A `404` or `403` response alone does not prove that exploitation was successful.

## 4. Remediation

Implement:

1. Canonical path validation.
2. Strict allow-listing of accessible files/resources.
3. Rejection of traversal sequences before file access.
4. Least-privilege application filesystem permissions.
5. Secure framework and web-server configuration.

Avoid constructing filesystem paths directly from untrusted user input.

## 5. Recovery

If sensitive files may have been exposed:

- rotate affected credentials and secrets;
- review application configuration;
- search for follow-on access;
- preserve forensic evidence;
- verify whether unauthorized data was downloaded.

## 6. Validation

Confirm that:

- traversal payloads are rejected;
- encoded variants are also rejected;
- legitimate paths still work;
- sensitive filesystem locations cannot be reached;
- application logs record blocked attempts.

## 7. ATT&CK Context

ATT&CK mappings should only be added when the observed activity supports them.

For exploitation of an exposed public-facing application, T1190 may be relevant.

Do not assign a technique solely because the alert was classified as path traversal.