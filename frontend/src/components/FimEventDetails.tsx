import React from 'react';

import {
  AlertCircle,
  Clock,
  Cpu,
  FileText,
  User,
} from 'lucide-react';

import type {
  FimEvent,
} from '../types/fim';

interface FimEventDetailsProps {
  event: FimEvent;
}

function formatBytes(
  bytes: number | null,
): string {
  if (
    bytes === null ||
    bytes === undefined
  ) {
    return 'N/A';
  }

  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(
      bytes / 1024
    ).toFixed(1)} KB`;
  }

  if (bytes < 1024 * 1024 * 1024) {
    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(1)} MB`;
  }

  return `${(
    bytes /
    (1024 * 1024 * 1024)
  ).toFixed(1)} GB`;
}

export const FimEventDetails: React.FC<
  FimEventDetailsProps
> = ({ event }) => {
  const changed =
    event.old_hash !==
      event.new_hash &&
    event.old_hash !== null;

  return (
    <div
      style={{
        padding: '18px',
        background:
          'rgba(0,0,0,0.22)',
        borderTop:
          '1px solid var(--border-primary)',
      }}
    >
      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '14px',
          marginBottom: '14px',
        }}
      >
        <div>
          <div
            style={{
              color:
                'var(--text-muted)',
              fontSize:
                '0.7rem',
            }}
          >
            FILE
          </div>

          <div
            style={{
              display: 'flex',
              gap: '7px',
              marginTop: '5px',
              fontFamily:
                'var(--font-mono)',
              color:
                'var(--cyan)',
              fontSize:
                '0.78rem',
              wordBreak:
                'break-all',
            }}
          >
            <FileText size={14} />
            {event.file_path}
          </div>
        </div>

        <div>
          <div
            style={{
              color:
                'var(--text-muted)',
              fontSize:
                '0.7rem',
            }}
          >
            ACTOR
          </div>

          <div
            style={{
              display: 'flex',
              gap: '7px',
              marginTop: '5px',
              alignItems: 'center',
            }}
          >
            <User size={14} />

            {event.actor ||
              'Unknown'}
          </div>
        </div>

        <div>
          <div
            style={{
              color:
                'var(--text-muted)',
              fontSize:
                '0.7rem',
            }}
          >
            PROCESS
          </div>

          <div
            style={{
              display: 'flex',
              gap: '7px',
              marginTop: '5px',
              alignItems: 'center',
              fontFamily:
                'var(--font-mono)',
            }}
          >
            <Cpu size={14} />

            {event.process_name ||
              'Unknown'}
          </div>
        </div>

        <div>
          <div
            style={{
              color:
                'var(--text-muted)',
              fontSize:
                '0.7rem',
            }}
          >
            DETECTED
          </div>

          <div
            style={{
              display: 'flex',
              gap: '7px',
              marginTop: '5px',
              alignItems: 'center',
            }}
          >
            <Clock size={14} />
            {event.timestamp}
          </div>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            '1fr 1fr',
          gap: '12px',
        }}
      >
        <div>
          <div
            style={{
              color:
                'var(--text-muted)',
              fontSize:
                '0.7rem',
              marginBottom:
                '5px',
            }}
          >
            OLD SHA-256
          </div>

          <pre
            style={{
              margin: 0,
              padding: '10px',
              background:
                'rgba(0,0,0,0.25)',
              borderRadius: '6px',
              fontFamily:
                'var(--font-mono)',
              fontSize:
                '0.68rem',
              wordBreak:
                'break-all',
                whiteSpace:
                'pre-wrap',
              color:
                'var(--text-secondary)',
            }}
          >
            {event.old_hash ||
              'N/A'}
          </pre>

          <div
            style={{
              marginTop: '5px',
              fontSize:
                '0.7rem',
              color:
                'var(--text-muted)',
            }}
          >
            Size:{' '}
            {formatBytes(
              event.old_size,
            )}
          </div>
        </div>

        <div>
          <div
            style={{
              color:
                'var(--text-muted)',
              fontSize:
                '0.7rem',
              marginBottom:
                '5px',
            }}
          >
            NEW SHA-256
          </div>

          <pre
            style={{
              margin: 0,
              padding: '10px',
              background:
                'rgba(0,0,0,0.25)',
              borderRadius: '6px',
              fontFamily:
                'var(--font-mono)',
              fontSize:
                '0.68rem',
              wordBreak:
                'break-all',
              whiteSpace:
                'pre-wrap',
              color:
                changed
                  ? 'var(--red)'
                  : 'var(--emerald)',
            }}
          >
            {event.new_hash ||
              'N/A'}
          </pre>

          <div
            style={{
              marginTop: '5px',
              fontSize:
                '0.7rem',
              color:
                'var(--text-muted)',
            }}
          >
            Size:{' '}
            {formatBytes(
              event.new_size,
            )}
          </div>
        </div>
      </div>

      {changed && (
        <div
          style={{
            display: 'flex',
            gap: '8px',
            alignItems:
              'center',
            marginTop: '14px',
            color:
              'var(--red)',
            fontSize:
              '0.75rem',
          }}
        >
          <AlertCircle
            size={15}
          />

          SHA-256 mismatch detected
          against the trusted baseline.
        </div>
      )}

      {event.details && (
        <div
          style={{
            marginTop: '14px',
            padding: '10px',
            borderRadius: '6px',
            border:
              '1px solid rgba(6,182,212,0.15)',
            background:
              'rgba(6,182,212,0.04)',
            color:
              'var(--text-secondary)',
            fontSize:
              '0.75rem',
          }}
        >
          {event.details}
        </div>
      )}
    </div>
  );
};