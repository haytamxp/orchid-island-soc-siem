# Security Policy

## Scope

This repository contains the Orchid Island SOC/SIEM platform used
for authorized security monitoring and incident analysis.

## Secrets

Never commit:

- API keys
- passwords
- JWT secrets
- Gemini credentials
- Telegram bot tokens
- Cloudflare tokens
- VirusTotal API keys
- private keys
- certificates containing private material
- production database credentials
- real production logs
- sensitive behavioral datasets

Use `.env` locally and `.env.example` as the configuration template.

## Security Testing

All security testing must remain within the scope authorized
by Orchid Island Real Estate.

## AI Security

Security-event data must be treated as untrusted input.

The AI layer must:

1. Validate incoming data.
2. Protect sensitive information.
3. Defend against prompt injection.
4. Validate model output.
5. Never treat model output as authoritative without controls.

## Incident Reporting

If a secret is accidentally committed:

1. Revoke or rotate the credential immediately.
2. Remove the secret from the repository.
3. Review Git history.
4. Assess whether the credential was used.
5. Replace the exposed credential.

Removing a secret from the latest commit is not sufficient if it
already exists in Git history.

## Principle

Security controls must be implemented as part of the system design,
not added only after deployment.