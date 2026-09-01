import React, { useState, useMemo } from 'react';
import type { SecurityEvent } from '../data/mockData';
import { Network, ShieldAlert, Search } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface SuricataViewProps {
  events: SecurityEvent[];
}

export const SuricataView: React.FC<SuricataViewProps> = ({ events }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter events that represent Network IDS/Suricata alerts
  const suricataEvents = useMemo(() => {
    const networkCategories = ['SQL Injection', 'SSH Brute Force', 'Local Port Scan', 'DNS Query Exfiltration', 'DNS Amplification Response', 'SMB Session Exploit Attempt', 'Kerberoasting Ticket Requested', 'SSH Session Opened', 'SSH Reverse Shell Check', 'Outbound Shell Connection', 'DNS Flood'];
    
    return events.filter(e => {
      const cat = (e.category || '').toLowerCase();
      const host = (e.hostname || '').toLowerCase();
      const isNetwork = 
        cat.includes('suricata') || 
        cat.includes('ids') || 
        cat.includes('nids') || 
        cat.includes('attempted') || 
        cat.includes('network') ||
        cat.includes('exploit') ||
        cat.includes('scan') ||
        cat.includes('flood') ||
        cat.includes('injection') ||
        cat.includes('brute') ||
        host.includes('suricata') ||
        networkCategories.some(c => cat.includes(c.toLowerCase()));

      const matchesSearch = 
        (e.src_ip || '').includes(searchTerm) || 
        (e.dest_ip || '').includes(searchTerm) || 
        cat.includes(searchTerm.toLowerCase());

      return isNetwork && matchesSearch;
    });
  }, [events, searchTerm]);

  // Aggregate protocol stats
  const protocolStats = useMemo(() => {
    const stats: Record<string, number> = { TCP: 0, UDP: 0, ICMP: 0, DNS: 0 };
    suricataEvents.forEach(e => {
      if (e.dest_port === 53 || e.dest_port === 88) stats.DNS++;
      else if (e.dest_port === 22 || e.dest_port === 80 || e.dest_port === 443 || e.dest_port === 3306 || e.dest_port === 445 || e.dest_port === 8080) stats.TCP++;
      else if (e.dest_port === 25 || e.dest_port === 389) stats.TCP++;
      else stats.UDP++;
    });
    return Object.keys(stats).map(key => ({ name: key, count: stats[key] }));
  }, [suricataEvents]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Overview stats panel */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(6, 182, 212, 0.1)', color: 'var(--cyan)' }}>
            <Network size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>TOTAL NETWORK IDS INTRUSIONS</h4>
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>{suricataEvents.length}</span>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--red)' }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>CRITICAL IDS SIGS</h4>
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>
              {suricataEvents.filter(e => e.severity === 'Critical').length}
            </span>
          </div>
        </div>
      </div>

      {/* Network Protocols Graph & Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px' }}>
        
        {/* Recharts Bar Chart */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px' }}>Procotol alert distribution</h3>
          <div style={{ width: '100%', height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={protocolStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                    border: '1px solid var(--border-primary)', 
                    borderRadius: '8px',
                    color: 'var(--text-primary)' 
                  }} 
                />
                <Bar dataKey="count" fill="var(--cyan)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Info panel */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '10px', color: 'var(--cyan)' }}>Suricata NIDS Core Rules</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            Ce panneau affiche les flux réseau capturés par les sondes passives de type SPAN/TAP et traitées par le moteur de signatures Suricata.
          </p>
          <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.75rem' }}>
            <div>• <strong>Engine Version:</strong> Suricata v7.0.2-RELEASE</div>
            <div>• <strong>Network Interfaces:</strong> eth0 (10.100.0.0/16), eth1 (192.168.1.0/24)</div>
            <div>• <strong>Active ruleset:</strong> Emerging Threats (ET) Open Ruleset</div>
          </div>
        </div>

      </div>

      {/* Logs Table */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Suricata Intrusion Alert Logs</h3>
          
          <div style={{ position: 'relative', width: '260px' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Filter by IP or anomaly type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-primary)',
                borderRadius: '6px',
                padding: '6px 12px 6px 30px',
                color: '#ffffff',
                fontSize: '0.8rem',
                outline: 'none'
              }}
            />
          </div>
        </div>

        <div style={{ overflowX: 'auto', border: '1px solid var(--border-primary)', borderRadius: '8px' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Source IP</th>
                <th>Destination</th>
                <th>Protocol / Port</th>
                <th>Intrusion Signature</th>
                <th>Rule Signature ID</th>
                <th>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {suricataEvents.length > 0 ? (
                suricataEvents.map(event => (
                  <tr key={event.id}>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{event.timestamp}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{event.src_ip}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{event.dest_ip}</td>
                    <td style={{ color: 'var(--cyan)', fontWeight: 500, fontSize: '0.8rem' }}>
                      {event.dest_port === 53 ? 'DNS' : event.dest_port === 80 || event.dest_port === 443 ? 'HTTP/S' : 'TCP'} ({event.dest_port})
                    </td>
                    <td style={{ fontWeight: 600 }}>ET SCAN {event.category} Attempt</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{event.rule_id}</td>
                    <td>
                      <span style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        backgroundColor: event.severity === 'Critical' ? 'rgba(239, 68, 68, 0.15)' : event.severity === 'High' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                        color: event.severity === 'Critical' ? 'var(--red)' : event.severity === 'High' ? 'var(--amber)' : 'var(--cyan)'
                      }}>
                        {event.severity}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                    Aucune signature réseau detectée.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
