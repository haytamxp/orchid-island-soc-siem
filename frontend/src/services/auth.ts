import type {
  AuthSession,
  UserRole,
} from '../types/rbac';

const SESSION_KEY = 'siem_session';

function normalizeRole(
  value: unknown,
): UserRole {
  const role = String(value ?? '')
    .trim()
    .toLowerCase();

  if (
    role === 'superadmin' ||
    role === 'super_admin' ||
    role === 'super-admin'
  ) {
    return 'superadmin';
  }

  if (role === 'employee') {
    return 'employee';
  }

  return 'admin';
}

export interface LoginResponse {
  status: 'authenticated';
  session_token: string;
  username: string;
  role: string;
}

export function saveAuthSession(
  response: LoginResponse,
): AuthSession {
  const session: AuthSession = {
    sessionToken: response.session_token,
    username: response.username,
    role: normalizeRole(response.role),
    authenticatedAt:
      new Date().toISOString(),
  };

  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify(session),
  );

  return session;
}

export function getAuthSession():
  | AuthSession
  | null {
  const raw =
    localStorage.getItem(
      SESSION_KEY,
    );

  if (!raw) {
    return null;
  }

  try {
    const parsed =
      JSON.parse(raw) as Partial<AuthSession>;

    if (
      typeof parsed.sessionToken !==
        'string' ||
      typeof parsed.username !==
        'string'
    ) {
      return null;
    }

    return {
      sessionToken:
        parsed.sessionToken,
      username:
        parsed.username,
      role: normalizeRole(
        parsed.role,
      ),
      authenticatedAt:
        typeof parsed.authenticatedAt ===
        'string'
          ? parsed.authenticatedAt
          : new Date().toISOString(),
    };
  } catch {
    return null;
  }
}

export function clearAuthSession(): void {
  localStorage.removeItem(
    SESSION_KEY,
  );
}

export function isAuthenticated(): boolean {
  return Boolean(
    getAuthSession(),
  );
}

export function getCurrentRole():
  | UserRole
  | null {
  return (
    getAuthSession()?.role ??
    null
  );
}
