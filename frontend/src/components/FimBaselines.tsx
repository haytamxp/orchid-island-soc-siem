import React from 'react';

import {
  CheckCircle2,
  PauseCircle,
  PlayCircle,
  ShieldCheck,
} from 'lucide-react';

import type {
  FimBaseline,
} from '../types/fim';

interface Props {
  baselines: FimBaseline[];
  onDisable: (id: number) => Promise<void>;
  onEnable: (id: number) => Promise<void>;
}

function formatBytes(
  bytes: number,
): string {
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

export const FimBaselines:
  React.FC<Props> = ({
    baselines,
    onDisable,
    onEnable,
  }) => (
    <section
      style={{
        marginTop: '18px',
        border:
          '1px solid var(--border-primary)',
        borderRadius: '10px',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '14px 16px',
          borderBottom:
            '1px solid var(--border-primary)',
        }}
      >
        <ShieldCheck
          size={17}
          color="var(--cyan)"
        />

        <strong>Trusted baselines</strong>

        <span
          style={{
            marginLeft: 'auto',
            color: 'var(--text-muted)',
            fontSize: '0.74rem',
          }}
        >
          {baselines.length} configured
        </span>
      </div>

      {baselines.length === 0 ? (
        <div
          style={{
            padding: '24px',
            textAlign: 'center',
            color: 'var(--text-muted)',
          }}
        >
          No real baselines configured.
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
              borderCollapse: 'collapse',
            }}
          >
            <thead>
              <tr>
                <th>Host</th>
                <th>File</th>
                <th>SHA-256</th>
                <th>Size</th>
                <th>Updated</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {baselines.map(
                (baseline) => (
                  <tr
                    key={baseline.id}
                    style={{
                      borderTop:
                        '1px solid var(--border-primary)',
                    }}
                  >
                    <td>
                      {baseline.hostname}
                    </td>

                    <td
                      style={{
                        fontFamily:
                          'var(--font-mono)',
                        fontSize: '0.7rem',
                        color: 'var(--cyan)',
                      }}
                    >
                      {baseline.file_path}
                    </td>

                    <td
                      style={{
                        maxWidth: '250px',
                        fontFamily:
                          'var(--font-mono)',
                        fontSize: '0.64rem',
                        wordBreak: 'break-all',
                      }}
                    >
                      {baseline.sha256}
                    </td>

                    <td>
                      {formatBytes(
                        baseline.file_size,
                      )}
                    </td>

                    <td>
                      {baseline.updated_at}
                    </td>

                    <td>
                      {baseline.monitored ? (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '5px',
                            color:
                              'var(--emerald)',
                          }}
                        >
                          <CheckCircle2 size={13} />
                          Monitoring
                        </span>
                      ) : (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '5px',
                            color:
                              'var(--text-muted)',
                          }}
                        >
                          <PauseCircle size={13} />
                          Disabled
                        </span>
                      )}
                    </td>

                    <td>
                      {baseline.monitored ? (
                        <button
                          type="button"
                          onClick={() =>
                            void onDisable(
                              baseline.id,
                            )
                          }
                        >
                          <PauseCircle size={13} />
                          Disable
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() =>
                            void onEnable(
                              baseline.id,
                            )
                          }
                        >
                          <PlayCircle size={13} />
                          Enable
                        </button>
                      )}
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
