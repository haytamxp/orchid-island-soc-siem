-- ============================================================
-- Seed: default login accounts
-- ------------------------------------------------------------
-- Idempotent. Re-running this file restores the known dev
-- credentials (use it whenever login stops working).
--
--   admin / admin123        MFA: 000000   role: admin
--
-- The password column stores a Werkzeug pbkdf2:sha256 hash so it
-- is portable across machines (unlike scrypt, which needs a
-- matching OpenSSL build).  Regenerate with:
--   python -c "from werkzeug.security import generate_password_hash as g; print(g('admin123', method='pbkdf2:sha256'))"
-- ============================================================

INSERT INTO users (username, password, mfa_token, role)
VALUES (
    'admin',
    'pbkdf2:sha256:1000000$Abv7KanWle0BkOOq$312d3a70a618ff886d48507b7c6313ce411244a54acab074d7194ede2698339e',
    '000000',
    'admin'
)
ON DUPLICATE KEY UPDATE
    password  = VALUES(password),
    mfa_token = VALUES(mfa_token),
    role      = VALUES(role);
