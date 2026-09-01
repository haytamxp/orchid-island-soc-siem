import React from 'react';
import { ShieldX } from 'lucide-react';

interface AccessDeniedProps {
  title?: string;
  message?: string;
}

export const AccessDenied: React.FC<
  AccessDeniedProps
> = ({
  title = 'Access Restricted',
  message = 'Your current role does not have permission to access this area.',
}) => {
  return (
    <div
      className="glass-panel"
      style={{
        minHeight: '360px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        gap: '10px',
        padding: '30px',
      }}
    >
      <ShieldX
        size={42}
        style={{
          color: 'var(--red)',
        }}
      />

      <h3
        style={{
          margin: 0,
          fontSize: '1rem',
        }}
      >
        {title}
      </h3>

      <p
        style={{
          maxWidth: '420px',
          margin: 0,
          color: 'var(--text-secondary)',
          fontSize: '0.75rem',
          lineHeight: 1.5,
        }}
      >
        {message}
      </p>
    </div>
  );
};
