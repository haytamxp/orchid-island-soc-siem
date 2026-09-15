import React from 'react';

import {
  AlertTriangle,
  FileWarning,
  Plus,
  ShieldAlert,
  Trash2,
} from 'lucide-react';

import type {
  FimStats as FimStatsData,
} from '../types/fim';

interface FimStatsProps {
  stats: FimStatsData;
}

export const FimStats: React.FC<
  FimStatsProps
> = ({ stats }) => {
  const cards = [
    {
      label: 'Total Changes',
      value: stats.total,
      icon: <FileWarning size={18} />,
      color: 'var(--cyan)',
    },
    {
      label: 'Critical',
      value: stats.critical,
      icon: <ShieldAlert size={18} />,
      color: 'var(--red)',
    },
    {
      label: 'High',
      value: stats.high,
      icon: <AlertTriangle size={18} />,
      color: 'var(--amber)',
    },
    {
      label: 'Modified',
      value: stats.modified,
      icon: <FileWarning size={18} />,
      color: 'var(--amber)',
    },
    {
      label: 'Deleted',
      value: stats.deleted,
      icon: <Trash2 size={18} />,
      color: 'var(--red)',
    },
    {
      label: 'Added',
      value: stats.added,
      icon: <Plus size={18} />,
      color: 'var(--emerald)',
    },
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns:
          'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px',
      }}
    >
      {cards.map((card) => (
        <div
          key={card.label}
          className="glass-panel"
          style={{
            padding: '16px',
            minHeight: '100px',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent:
                'space-between',
              alignItems: 'center',
              marginBottom: '14px',
            }}
          >
            <span
              style={{
                color:
                  'var(--text-secondary)',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              {card.label}
            </span>

            <span
              style={{
                color: card.color,
              }}
            >
              {card.icon}
            </span>
          </div>

          <div
            style={{
              fontSize: '1.6rem',
              fontWeight: 800,
            }}
          >
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
};