import React, { useState, useMemo } from 'react';
import type { FimEvent } from '../data/mockData';
import { FileCode, Search, AlertCircle } from 'lucide-react';

interface FimViewProps {
  fimEvents: FimEvent[];
}

export const FimView: React.FC<FimViewProps> = ({ fimEvents }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const filteredFim = useMemo(() => {
    return fimEvents.filter(e => 
      e.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.hostname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.modified_by.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [fimEvents, searchTerm]);

  const truncateHash = (hash: string) => {
    if (hash === 'EMPTY_FILE') return hash;
    return `${hash.substring(0, 8)}...${hash.substring(hash.length - 8)}`;
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Description header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileCode size={20} style={{ color: 'var(--cyan)' }} /> File Integrity Monitoring (FIM)
          </h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Détection des altérations et modifications non autorisées de fichiers système critiques.
          </p>
        </div>
      </div>

      {/* Toolbar Search */}
      <div style={{ position: 'relative' }}>
        <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          type="text"
          placeholder="Filter by filepath, host, or modified user..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="glow-border-cyan"
          style={{
            width: '100%',
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--border-primary)',
            borderRadius: '8px',
            padding: '10px 16px 10px 38px',
            color: '#ffffff',
            fontSize: '0.875rem'
          }}
        />
      </div>

      {/* FIM Table */}
      <div style={{ overflowX: 'auto', border: '1px solid var(--border-primary)', borderRadius: '8px' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Host</th>
              <th>File Integrity Path</th>
              <th>Event</th>
              <th>Modified By</th>
              <th>Old Hash (SHA-256)</th>
              <th>New Hash (SHA-256)</th>
            </tr>
          </thead>
          <tbody>
            {filteredFim.length > 0 ? (
              filteredFim.map(event => {
                const isExpanded = expandedRow === event.id;
                const isHashChanged = event.old_hash !== event.new_hash && event.old_hash !== 'EMPTY_FILE';
                return (
                  <React.Fragment key={event.id}>
                    <tr 
                      onClick={() => setExpandedRow(isExpanded ? null : event.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{event.timestamp}</td>
                      <td style={{ fontWeight: 500 }}>{event.hostname}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--cyan)' }}>{event.filename}</td>
                      <td>
                        <span style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '4px',
                          backgroundColor: event.event_type === 'Added' ? 'rgba(16, 185, 129, 0.15)' : event.event_type === 'Deleted' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                          color: event.event_type === 'Added' ? 'var(--emerald)' : event.event_type === 'Deleted' ? 'var(--red)' : 'var(--amber)'
                        }}>
                          {event.event_type}
                        </span>
                      </td>
                      <td style={{ fontWeight: 500 }}>{event.modified_by}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {truncateHash(event.old_hash)}
                      </td>
                      <td style={{ 
                        fontFamily: 'var(--font-mono)', 
                        fontSize: '0.75rem', 
                        color: isHashChanged ? 'var(--red)' : 'var(--emerald)'
                      }}>
                        {truncateHash(event.new_hash)}
                        {isHashChanged && <AlertCircle size={10} style={{ display: 'inline-block', marginLeft: '4px', color: 'var(--red)' }} />}
                      </td>
                    </tr>
                    
                    {/* Expanded details row */}
                    {isExpanded && (
                      <tr>
                        <td colSpan={7} style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '16px' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem' }}>
                            <div>
                              <strong style={{ color: 'var(--text-secondary)' }}>Complete Filename:</strong> 
                              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--cyan)', marginLeft: '6px' }}>{event.filename}</span>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '4px' }}>
                              <div>
                                <strong style={{ color: 'var(--text-secondary)' }}>Old Hash SHA-256:</strong>
                                <pre style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.2)', padding: '6px', borderRadius: '4px', marginTop: '4px', overflowX: 'auto' }}>
                                  {event.old_hash}
                                </pre>
                              </div>
                              <div>
                                <strong style={{ color: 'var(--text-secondary)' }}>New Hash SHA-256:</strong>
                                <pre style={{ 
                                  fontFamily: 'var(--font-mono)', 
                                  color: isHashChanged ? 'var(--red)' : 'var(--emerald)', 
                                  background: 'rgba(0,0,0,0.2)', 
                                  padding: '6px', 
                                  borderRadius: '4px', 
                                  marginTop: '4px', 
                                  overflowX: 'auto',
                                  border: isHashChanged ? '1px solid rgba(239,68,68,0.2)' : 'none'
                                }}>
                                  {event.new_hash}
                                </pre>
                              </div>
                            </div>
                            {isHashChanged && (
                              <div style={{ marginTop: '8px', color: 'var(--red)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <AlertCircle size={14} />
                                <span>Avertissement : Les signatures de hachage diffèrent. Cela peut indiquer une altération non autorisée du fichier binaire ou de configuration.</span>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            ) : (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                  Aucun événement FIM ne correspond à la recherche.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
};
