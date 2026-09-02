"""
seed_users.py — create / restore the default login accounts.

Idempotent: run it as many times as you like. It upserts each row in
DEFAULT_USERS, so it both seeds a fresh database and repairs an account
whose password hash got mangled.

    ./venv/bin/python -m backend.scripts.seed_users            # seed / repair all
    ./venv/bin/python -m backend.scripts.seed_users --list     # just show what's there

Default credentials:
    admin / admin123    MFA: 000000    role: admin
"""
import sys

from werkzeug.security import generate_password_hash

from backend.services.db import query_all, execute

# username -> (plaintext password, mfa token, role)
DEFAULT_USERS: dict[str, tuple[str, str, str]] = {
    "admin": ("admin123", "000000", "admin"),
}

# pbkdf2 is portable across machines; scrypt (the werkzeug default) depends
# on the local OpenSSL build and can silently differ between environments.
HASH_METHOD = "pbkdf2:sha256"


def list_users() -> None:
    rows = query_all("SELECT id, username, role, mfa_token, created_at FROM users ORDER BY id")
    if not rows:
        print("(users table is empty)")
        return
    for r in rows:
        print(f"  #{r['id']:<3} {r['username']:<20} role={r['role']:<10} mfa={r['mfa_token']!r}")


def seed() -> None:
    for username, (password, mfa_token, role) in DEFAULT_USERS.items():
        execute(
            """
            INSERT INTO users (username, password, mfa_token, role)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                password  = VALUES(password),
                mfa_token = VALUES(mfa_token),
                role      = VALUES(role)
            """,
            (username, generate_password_hash(password, method=HASH_METHOD), mfa_token, role),
        )
        print(f"seeded: {username} / {password}   (MFA {mfa_token}, role {role})")


def main() -> int:
    if "--list" in sys.argv[1:]:
        list_users()
        return 0
    seed()
    print()
    print("current users:")
    list_users()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
