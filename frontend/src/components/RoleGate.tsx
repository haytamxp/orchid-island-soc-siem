import React from 'react';

import type {
  Permission,
  UserRole,
} from '../types/rbac';

import { hasPermission } from '../types/rbac';

interface RoleGateProps {
  role: UserRole;
  permission?: Permission;
  allowedRoles?: readonly UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGate: React.FC<RoleGateProps> = ({
  role,
  permission,
  allowedRoles,
  children,
  fallback = null,
}) => {
  if (
    allowedRoles &&
    !allowedRoles.includes(role)
  ) {
    return <>{fallback}</>;
  }

  if (
    permission &&
    !hasPermission(role, permission)
  ) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
