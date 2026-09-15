import React, {
  useState,
} from 'react';

import {
  ChevronDown,
  ChevronRight,
  Filter,
  RefreshCw,
  ShieldAlert,
} from 'lucide-react';

import type {
  FimEvent,
} from '../types/fim';

import {
  useFimData,
} from '../hooks/useFimData';

import {
  FimEventDetails,
} from './FimEventDetails';

import {
  FimBaselines,
} from './FimBaselines';

import {
  FimStats,
} from './FimStats';

interface FimViewProps {
  /*
   * Compatibility with App.tsx.
   * This prop is intentionally not used.
   * FIM data comes exclusively from the backend.
   */
  fimEvents?: FimEvent[];
}

function severityColor(
  severity: string,
): string {
  switch (severity) {
    case 'Critical':
      return 'var(--red)';
    case 'High':
      return 'var(--orange)';
    case 'Medium':
      return 'var(--yellow)';
    default:
      return 'var(--text-muted)';
  }
}

export const FimView:
  React.FC<FimViewProps> = () => {
    const {
      filteredEvents,
      baselines,
      stats,
      loading,
      backendHealthy,
      error,
      filters,
      setFilters,
      refresh,
      disableBaseline,
      enableBaseline,
    } = useFimData();

    const [
      expandedId,
      setExpandedId,
    ] = useState<number | null>(null);

    return (
      <div
        style={{
          padding: '22px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '6px',
          }}
        >
          <ShieldAlert
            size={21}
            color="var(--cyan)"
          />

          <h2
            style={{
              margin: 0,
            }}
          >
            File Integrity Monitoring
          </h2>

          <span
            style={{
              marginLeft: 'auto',
              padding: '5px 9px',
              borderRadius: '999px',
              fontSize: '0.7rem',
              border:
                '1px solid var(--border-primary)',
              color:
                backendHealthy
                  ? 'var(--emerald)'
                  : 'var(--red)',
            }}
          >
            {backendHealthy
              ? 'Live backend data'
              : 'Backend unavailable'}
          </span>
        </div>

        <div
          style={{
            color: 'var(--text-muted)',
            fontSize: '0.78rem',
            marginBottom: '18px',
          }}
        >
          Real FIM telemetry from the
          backend and MariaDB.
        </div>

        {error && (
          <div
            style={{
              marginBottom: '14px',
              padding: '11px 13px',
              borderRadius: '7px',
              border:
                '1px solid rgba(239,68,68,0.35)',
              background:
                'rgba(239,68,68,0.08)',
              color: 'var(--red)',
              fontSize: '0.75rem',
            }}
          >
            {error}
          </div>
        )}

        <FimStats stats={stats} />

        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '10px',
            marginTop: '18px',
          }}
        >
          <input
            value={filters.hostname}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                hostname: event.target.value,
              }))
            }
            placeholder="Hostname"
          />

          <select
            value={filters.severity}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                severity: event.target.value,
              }))
            }
          >
            <option value="">
              All severities
            </option>
            <option value="Critical">
              Critical
            </option>
            <option value="High">
              High
            </option>
            <option value="Medium">
              Medium
            </option>
            <option value="Low">
              Low
            </option>
          </select>

          <select
            value={filters.change_type}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                change_type: event.target.value,
              }))
            }
          >
            <option value="">
              All changes
            </option>
            <option value="modified">
              Modified
            </option>
            <option value="added">
              Added
            </option>
            <option value="deleted">
              Deleted
            </option>
          </select>

          <input
            value={filters.search}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                search: event.target.value,
              }))
            }
            placeholder="Search..."
          />

          <button
            type="button"
            onClick={() => void refresh()}
          >
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>

        <div
          style={{
            marginTop: '18px',
            border:
              '1px solid var(--border-primary)',
            borderRadius: '9px',
            overflow: 'hidden',
          }}
        >
          {loading ? (
            <div
              style={{
                padding: '30px',
                textAlign: 'center',
              }}
            >
              Loading real FIM telemetry...
            </div>
          ) : filteredEvents.length === 0 ? (
            <div
              style={{
                padding: '35px',
                textAlign: 'center',
                color: 'var(--text-muted)',
              }}
            >
              No real FIM events match
              the current filters.
            </div>
          ) : (
            <div
              style={{
                overflowX: 'auto',
              }}
            >
              <table
                style={{
                  width: '100%',
                  borderCollapse:
                    'collapse',
                }}
              >
                <thead>
                  <tr>
                    <th />
                    <th>Time</th>
                    <th>Host</th>
                    <th>File</th>
                    <th>Change</th>
                    <th>Severity</th>
                    <th>Agent</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredEvents.map(
                    (event) => {
                      const expanded =
                        expandedId === event.id;

                      return (
                        <React.Fragment
                          key={event.id}
                        >
                          <tr
                            onClick={() =>
                              setExpandedId(
                                expanded
                                  ? null
                                  : event.id,
                              )
                            }
                          >
                            <td>
                              {expanded ? (
                                <ChevronDown
                                  size={15}
                                />
                              ) : (
                                <ChevronRight
                                  size={15}
                                />
                              )}
                            </td>

                            <td>
                              {event.timestamp}
                            </td>

                            <td>
                              {event.hostname}
                            </td>

                            <td
                              style={{
                                fontFamily:
                                  'var(--font-mono)',
                                color:
                                  'var(--cyan)',
                              }}
                            >
                              {event.file_path}
                            </td>

                            <td>
                              {event.change_type}
                            </td>

                            <td
                              style={{
                                color:
                                  severityColor(
                                    event.severity,
                                  ),
                              }}
                            >
                              {event.severity}
                            </td>

                            <td>
                              {event.agent_id ||
                                'N/A'}
                            </td>
                          </tr>

                          {expanded && (
                            <tr>
                              <td colSpan={7}>
                                <FimEventDetails
                                  event={event}
                                />
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    },
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <FimBaselines
          baselines={baselines}
          onDisable={disableBaseline}
          onEnable={enableBaseline}
        />

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            marginTop: '12px',
            color: 'var(--text-muted)',
            fontSize: '0.7rem',
          }}
        >
          <Filter size={13} />

          Empty means no matching real
          telemetry exists.
        </div>
      </div>
    );
  };
