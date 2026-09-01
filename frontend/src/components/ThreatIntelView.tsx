import React, { useState } from 'react';
import type { ThreatIntelIOC } from '../data/mockData';
import { AlertCircle, Target, Plus, Database, Trash2 } from 'lucide-react';
import { BACKEND_URL } from '../config';

interface ThreatIntelViewProps {
  iocs: ThreatIntelIOC[];
  setIocs: React.Dispatch<React.SetStateAction<ThreatIntelIOC[]>>;
}

export const ThreatIntelView: React.FC<ThreatIntelViewProps> = ({ iocs, setIocs }) => {
  // States for registering new IOC
  const [newValue, setNewValue] = useState('');
  const [newType, setNewType] = useState<'IP' | 'Domain' | 'Hash'>('IP');
  const [newActor, setNewActor] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  // MITRE ATT&CK tactics & techniques mapping
  // Highlight values: 'none' | 'low' | 'medium' | 'high' | 'critical'
  const mitreMatrix = [
    {
      tactic: "Reconnaissance",
      id: "TA0043",
      techniques: [
        { name: "Active Scanning", id: "T1595", active: true, severity: "Critical", alert: "SQL Injection Probe" },
        { name: "Gather Victim Identity", id: "T1589", active: false, severity: "none", alert: "" },
        { name: "Search Open Websites", id: "T1593", active: false, severity: "none", alert: "" }
      ]
    },
    {
      tactic: "Initial Access",
      id: "TA0001",
      techniques: [
        { name: "Exploit Public-Facing Application", id: "T1190", active: true, severity: "Critical", alert: "SQL Injection Exploit" },
        { name: "External Remote Services", id: "T1133", active: true, severity: "High", alert: "SSH Brute Force" },
        { name: "Valid Accounts", id: "T1078", active: false, severity: "none", alert: "" }
      ]
    },
    {
      tactic: "Execution",
      id: "TA0002",
      techniques: [
        { name: "Command and Script Interpreter", id: "T1059", active: true, severity: "Critical", alert: "Outbound Shell Execution" },
        { name: "User Execution", id: "T1204", active: false, severity: "none", alert: "" },
        { name: "Windows Management Instr.", id: "T1047", active: false, severity: "none", alert: "" }
      ]
    },
    {
      tactic: "Credential Access",
      id: "TA0006",
      techniques: [
        { name: "Kerberoasting Requests", id: "T1558.003", active: true, severity: "High", alert: "RC4 Ticket Request" },
        { name: "Brute Force", id: "T1110", active: true, severity: "High", alert: "SSH Brute Force" },
        { name: "Credentials from Web Browsers", id: "T1539", active: false, severity: "none", alert: "" }
      ]
    },
    {
      tactic: "Exfiltration",
      id: "TA0010",
      techniques: [
        { name: "Exfiltration Over Alternative Protocol", id: "T1048", active: true, severity: "Critical", alert: "DNS Tunneling" },
        { name: "Exfiltration Over C2 Channel", id: "T1020", active: true, severity: "Critical", alert: "Reverse Shell C2" },
        { name: "Scheduled Transfer", id: "T1029", active: false, severity: "none", alert: "" }
      ]
    }
  ];

  const handleAddIoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newValue.trim()) return;

    const payload = {
      value: newValue.trim(),
      type: newType,
      threat_actor: newActor || 'Unknown Campaign',
      description: newDesc || 'Ad-hoc Indicator registered from SOC console.'
    };

    try {
      const res = await fetch(`${BACKEND_URL}/api/iocs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const newIoc = await res.json();
        setIocs(prev => {
          if (prev.some(i => i.id === newIoc.id)) return prev;
          return [newIoc, ...prev];
        });
        setNewValue('');
        setNewActor('');
        setNewDesc('');
        setIsAdding(false);
      }
    } catch (err) {
      console.error("Erreur d'ajout de l'IOC:", err);
    }
  };

  const handleDeleteIoc = async (id: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/iocs/${id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setIocs(prev => prev.filter(i => i.id !== id));
      }
    } catch (err) {
      console.error("Erreur de suppression de l'IOC:", err);
    }
  };

  const getMitreBg = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'rgba(239, 68, 68, 0.15)';
      case 'High': return 'rgba(245, 158, 11, 0.15)';
      case 'Medium': return 'rgba(6, 182, 212, 0.15)';
      default: return 'rgba(15, 23, 42, 0.4)';
    }
  };

  const getMitreBorder = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'rgba(239, 68, 68, 0.45)';
      case 'High': return 'rgba(245, 158, 11, 0.4)';
      case 'Medium': return 'rgba(6, 182, 212, 0.4)';
      default: return 'rgba(30, 41, 59, 0.7)';
    }
  };

  const getMitreTextColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'var(--red)';
      case 'High': return 'var(--amber)';
      case 'Medium': return 'var(--cyan)';
      default: return 'var(--text-secondary)';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* MITRE ATT&CK Matrix Card */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Target size={20} style={{ color: 'var(--cyan)' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>MITRE ATT&CK Adversary Tactics Matrix</h3>
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Visualisation en temps réel des techniques d'attaques actives identifiées dans votre SIEM. Les cases colorées représentent des vecteurs d'alertes non résolus.
        </p>

        {/* Matrix Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', overflowX: 'auto' }}>
          {mitreMatrix.map((col, idx) => (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '160px' }}>
              <div style={{
                background: 'rgba(15,23,42,0.8)',
                borderBottom: '2px solid var(--cyan)',
                padding: '10px',
                borderRadius: '6px 6px 0 0',
                textAlign: 'center'
              }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#ffffff' }}>{col.tactic}</h4>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{col.id}</span>
              </div>
              
              {col.techniques.map((tech, techIdx) => (
                <div
                  key={techIdx}
                  className="mitre-cell"
                  style={{
                    backgroundColor: getMitreBg(tech.severity),
                    borderColor: getMitreBorder(tech.severity),
                    borderWidth: '1px',
                    borderStyle: 'solid',
                    color: getMitreTextColor(tech.severity),
                    padding: '10px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    minHeight: '80px'
                  }}
                >
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, display: 'block', color: tech.active ? '#ffffff' : 'var(--text-secondary)' }}>
                      {tech.name}
                    </span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{tech.id}</span>
                  </div>
                  
                  {tech.active && (
                    <div style={{ 
                      fontSize: '0.65rem', 
                      background: 'rgba(0,0,0,0.3)', 
                      padding: '2px 6px', 
                      borderRadius: '4px', 
                      marginTop: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      color: getMitreTextColor(tech.severity)
                    }}>
                      <AlertCircle size={10} /> {tech.alert}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* IOC Panel */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={20} style={{ color: 'var(--cyan)' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Indicators of Compromise (IOC) Database</h3>
          </div>
          
          <button 
            onClick={() => setIsAdding(!isAdding)}
            className="btn-primary" 
            style={{ fontSize: '0.75rem', padding: '6px 12px' }}
          >
            <Plus size={14} /> Register IOC
          </button>
        </div>

        {/* IOC Registration Form */}
        {isAdding && (
          <form onSubmit={handleAddIoc} className="glass-panel" style={{ padding: '20px', marginBottom: '20px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', background: 'rgba(0,0,0,0.15)' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Indicator Value</label>
              <input
                type="text"
                required
                placeholder="IP, domain or SHA256 hash"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                style={{
                  background: 'rgba(15,23,42,0.8)',
                  border: '1px solid var(--border-primary)',
                  color: '#ffffff',
                  padding: '8px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Indicator Type</label>
              <select
                value={newType}
                onChange={(e) => setNewType(e.target.value as any)}
                style={{
                  background: 'rgba(15,23,42,0.8)',
                  border: '1px solid var(--border-primary)',
                  color: '#ffffff',
                  padding: '8px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              >
                <option value="IP">IP Address</option>
                <option value="Domain">Domain Name</option>
                <option value="Hash">MD5/SHA256 Hash</option>
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Threat Actor / Campaign</label>
              <input
                type="text"
                placeholder="e.g. CozyBear, APT29"
                value={newActor}
                onChange={(e) => setNewActor(e.target.value)}
                style={{
                  background: 'rgba(15,23,42,0.8)',
                  border: '1px solid var(--border-primary)',
                  color: '#ffffff',
                  padding: '8px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', gridColumn: 'span 2' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Description</label>
              <input
                type="text"
                placeholder="Malicious behavior context details..."
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                style={{
                  background: 'rgba(15,23,42,0.8)',
                  border: '1px solid var(--border-primary)',
                  color: '#ffffff',
                  padding: '8px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ gridColumn: 'span 2', display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
              <button type="button" onClick={() => setIsAdding(false)} className="btn-secondary" style={{ fontSize: '0.75rem' }}>Cancel</button>
              <button type="submit" className="btn-primary" style={{ fontSize: '0.75rem' }}>Save Indicator</button>
            </div>
          </form>
        )}

        {/* IOC Data Table */}
        <div style={{ overflowX: 'auto', border: '1px solid var(--border-primary)', borderRadius: '8px' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Date Added</th>
                <th>Indicator Value</th>
                <th>Type</th>
                <th>Threat Actor</th>
                <th>Description</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {iocs.map(ioc => (
                <tr key={ioc.id}>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{ioc.date_added}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--cyan)' }}>{ioc.value}</td>
                  <td>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(6, 182, 212, 0.1)',
                      color: 'var(--cyan)'
                    }}>
                      {ioc.type}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{ioc.threat_actor}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{ioc.description}</td>
                  <td>
                    <button 
                      onClick={() => handleDeleteIoc(ioc.id)}
                      style={{ background: 'none', border: 'none', color: 'var(--red)', cursor: 'pointer' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
