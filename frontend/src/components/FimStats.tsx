import React from 'react';

import type {
  FimStats as FimStatsType,
} from '../types/fim';

interface Props {
  stats: FimStatsType;
}

interface CardProps {
  label: string;
  value: number;
}

const Card: React.FC<CardProps> = ({
  label,
  value,
}) => (
  <div
    style={{
      padding: '14px',
      border: '1px solid var(--border-primary)',
      borderRadius: '9px',
      background: 'rgba(255,255,255,0.02)',
    }}
  >
    <div
      style={{
        color: 'var(--text-muted)',
        fontSize: '0.68rem',
        textTransform: 'uppercase',
      }}
    >
      {label}
    </div>

    <div
      style={{
        marginTop: '5px',
        fontSize: '1.4rem',
        fontWeight: 700,
      }}
    >
      {value}
    </div>
  </div>
);

export const FimStats: React.FC<Props> = ({
  stats,
}) => (
  <div
    style={{
      display: 'grid',
      gridTemplateColumns:
        'repeat(auto-fit, minmax(130px, 1fr))',
      gap: '10px',
    }}
  >
    <Card
      label="Total events"
      value={stats.total}
    />

    <Card
      label="Critical"
      value={stats.critical}
    />

    <Card
      label="High"
      value={stats.high}
    />

    <Card
      label="Modified"
      value={stats.modified}
    />

    <Card
      label="Deleted"
      value={stats.deleted}
    />

    <Card
      label="Added"
      value={stats.added}
    />
  </div>
);
