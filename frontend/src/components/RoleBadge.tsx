import React from 'react';

import type { UserRole } from '../types/rbac';

interface RoleBadgeProps {
  role: UserRole;
  compact?: boolean;
}

const ROLE_LABELS: Record<
  UserRole,
  string
> = {
  superadmin: 'SuperAdmin',
  admin: 'Admin',
  employee: 'Employee',
};

const ROLE_COLORS: Record<
  UserRole,
  string
> = {
  superadmin: 'var(--purple)',
  admin: 'var(--cyan)',
  employee: 'var(--emerald)',
};

export const RoleBadge: React.FC<
  RoleBadgeProps
> = ({
  role,
  compact = false,
}) => {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        padding: compact
          ? '2px 6px'
          : '3px 8px',
        borderRadius: '12px',
        border: `1px solid ${ROLE_COLORS[role]}40`,
        background:
          `${ROLE_COLORS[role]}12`,
        color:
          ROLE_COLORS[role],
        fontSize: compact
          ? '0.58rem'
          : '0.65rem',
        fontWeight: 700,
        whiteSpace: 'nowrap',
      }}
    >
      <span
        style={{
          width: '5px',
          height: '5px',
          borderRadius: '50%',
          background:
            ROLE_COLORS[role],
        }}
      />

      {ROLE_LABELS[role]}
    </span>
  );
};
