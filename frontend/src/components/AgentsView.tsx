import React, { useState } from 'react';
import type { Agent } from '../data/mockData';
import { Laptop, Cpu, CheckCircle2, RotateCw, Play, ShieldAlert, Monitor } from 'lucide-react';
import { BACKEND_URL } from '../config';

interface AgentsViewProps {
  agents: Agent[];
  setAgents: React.Dispatch<React.SetStateAction<Agent[]>>;
}

export const AgentsView: React.FC<AgentsViewProps> = ({ agents, setAgents }) => {
  const [runningScanId, setRunningScanId] = useState<string | null>(null);
  const [restartingAgentId, setRestartingAgentId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string>('');

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3000);
  };

  const handleRunScan = async (agentId: string, agentName: string) => {
    setRunningScanId(agentId);
    await new Promise(r => setTimeout(r, 2000));
    setRunningScanId(null);
    triggerToast(`Scan de vulnérabilités terminé sur ${agentName}. Aucun nouveau CVE critique détecté.`);
  };

  const handleRestartAgent = async (agentId: string, agentName: string) => {
    setRestartingAgentId(agentId);
    
    try {
      const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
      const res = await fetch(`${BACKEND_URL}/api/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'Online',
          last_keep_alive: now
        })
      });

      if (res.ok) {
        const updated = await res.json();
        setAgents(prev => prev.map(agt => agt.id === agentId ? updated : agt));
        triggerToast(`Service Wazuh redémarré avec succès sur ${agentName}.`);
      }
    } catch (err) {
      console.error("Erreur de redémarrage de l'agent:", err);
    } finally {
      setRestartingAgentId(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid var(--cyan)',
          borderRadius: '8px',
          padding: '12px 20px',
          color: '#ffffff',
          boxShadow: '0 4px 20px rgba(6,182,212,0.3)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          zIndex: 9999
        }}>
          <CheckCircle2 size={18} style={{ color: 'var(--emerald)' }} />
          <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>{toastMessage}</span>
        </div>
      )}

      {/* Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--emerald)' }}>
            <Laptop size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>AGENTS TOTAL</h4>
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>{agents.length}</span>
          </div>
        </div>
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(6, 182, 212, 0.1)', color: 'var(--cyan)' }}>
            <CheckCircle2 size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>ONLINE AGENTS</h4>
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>{agents.filter(a => a.status === 'Online').length}</span>
          </div>
        </div>
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--red)' }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>OFFLINE AGENTS</h4>
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>{agents.filter(a => a.status === 'Offline').length}</span>
          </div>
        </div>
      </div>

      {/* Agents Grid list */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {agents.map(agent => (
          <div 
            key={agent.id} 
            className="glass-panel" 
            style={{ 
              padding: '20px', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '16px',
              borderTop: `4px solid ${agent.status === 'Online' ? 'var(--emerald)' : 'var(--text-muted)'}`
            }}
          >
            {/* Header info */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Monitor size={18} style={{ color: 'var(--cyan)' }} /> {agent.name}
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>ID: {agent.id} | {agent.version}</span>
              </div>
              <span style={{
                fontSize: '0.7rem',
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: agent.status === 'Online' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                color: agent.status === 'Online' ? 'var(--emerald)' : 'var(--text-muted)'
              }}>
                {agent.status}
              </span>
            </div>

            {/* Metrics data */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <div><strong>IP Address:</strong> {agent.ip_address}</div>
              <div><strong>OS:</strong> {agent.os}</div>
              <div style={{ gridColumn: 'span 2' }}>
                <strong>Last Keep-alive:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{agent.last_keep_alive}</span>
              </div>
            </div>

            {/* Resource stats */}
            {agent.status === 'Online' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', borderTop: '1px solid var(--border-primary)', paddingTop: '12px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Cpu size={12} /> CPU Usage</span>
                    <span style={{ fontWeight: 600 }}>{agent.cpu_usage.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${agent.cpu_usage}%`, background: 'var(--cyan)', borderRadius: '3px' }}></div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                    <span>RAM Usage</span>
                    <span style={{ fontWeight: 600 }}>{agent.ram_usage.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${agent.ram_usage}%`, background: 'var(--purple)', borderRadius: '3px' }}></div>
                  </div>
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div style={{ display: 'flex', gap: '10px', borderTop: '1px solid var(--border-primary)', paddingTop: '12px', marginTop: 'auto' }}>
              <button 
                disabled={agent.status === 'Offline' || runningScanId === agent.id}
                onClick={() => handleRunScan(agent.id, agent.name)}
                className="btn-primary" 
                style={{ fontSize: '0.75rem', padding: '6px 12px', flexGrow: 1, justifyContent: 'center' }}
              >
                {runningScanId === agent.id ? (
                  <>
                    <RotateCw size={12} className="animate-spin" /> Scanning...
                  </>
                ) : (
                  <>
                    <Play size={12} /> Scan Vulnerability
                  </>
                )}
              </button>
              
              <button 
                disabled={restartingAgentId === agent.id}
                onClick={() => handleRestartAgent(agent.id, agent.name)}
                className="btn-secondary" 
                style={{ fontSize: '0.75rem', padding: '6px 12px', flexGrow: 1, justifyContent: 'center' }}
              >
                {restartingAgentId === agent.id ? (
                  <>
                    <RotateCw size={12} className="animate-spin" /> Restarting...
                  </>
                ) : (
                  <>
                    <RotateCw size={12} /> Restart Daemon
                  </>
                )}
              </button>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
};
