export type UserRole = 'superadmin' | 'admin' | 'employee';

export interface AuthSession {
  sessionToken: string;
  username: string;
  role: UserRole;
  authenticatedAt: string;
}

export type Permission =
  | 'dashboard.view'
  | 'events.view'
  | 'alerts.view'
  | 'alerts.manage'
  | 'agents.view'
  | 'agents.manage'
  | 'threat_intel.view'
  | 'threat_intel.manage'
  | 'ai.view'
  | 'reports.view'
  | 'reports.manage'
  | 'administration.view'
  | 'users.manage'
  | 'system.manage';

export const ROLE_PERMISSIONS: Record<
  UserRole,
  readonly Permission[]
> = {
  superadmin: [
    'dashboard.view',
    'events.view',
    'alerts.view',
    'alerts.manage',
    'agents.view',
    'agents.manage',
    'threat_intel.view',
    'threat_intel.manage',
    'ai.view',
    'reports.view',
    'reports.manage',
    'administration.view',
    'users.manage',
    'system.manage',
  ],

  admin: [
    'dashboard.view',
    'events.view',
    'alerts.view',
    'alerts.manage',
    'agents.view',
    'agents.manage',
    'threat_intel.view',
    'threat_intel.manage',
    'ai.view',
    'reports.view',
    'reports.manage',
  ],

  employee: [
    'dashboard.view',
    'alerts.view',
    'events.view',
  ],
};

export function normalizeRole(
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

export function hasPermission(
  role: UserRole,
  permission: Permission,
): boolean {
  return ROLE_PERMISSIONS[role].includes(
    permission,
  );
}

export function hasRole(
  role: UserRole,
  allowedRoles: readonly UserRole[],
): boolean {
  return allowedRoles.includes(role);
}
