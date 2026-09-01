"""
reset_admin_password.py — dev helper to (re)set a user's login password.

Usage (from the project root, with the venv):

    ./venv/bin/python -m backend.scripts.reset_admin_password [username] [password]

Defaults to  admin / admin123.  The MFA token is left untouched
(the seeded 'admin' account uses 000000).
"""
import sys

from werkzeug.security import generate_password_hash

from backend.services.db import query_all, execute


def main() -> int:
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"

    users = query_all("SELECT id, username, role, mfa_token FROM users")
    user = next((u for u in users if u["username"] == username), None)

    if user is None:
        print(f"No user named '{username}'. Existing users:")
        for u in users:
            print(f"  - {u['username']} (role={u['role']}, mfa={u['mfa_token']!r})")
        if not users:
            print("  (users table is empty)")
        return 1

    execute(
        "UPDATE users SET password = %s WHERE username = %s",
        (generate_password_hash(password), username),
    )

    print(f"Password for '{username}' (role={user['role']}) set to: {password}")
    print(f"MFA token on record: {user['mfa_token']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
