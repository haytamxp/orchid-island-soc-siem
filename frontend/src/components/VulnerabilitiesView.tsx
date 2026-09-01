import React, { useState } from 'react';
import type { Vulnerability } from '../data/mockData';
import { AlertCircle, ShieldAlert, CheckCircle, Search, FileCheck } from 'lucide-react';
import { BACKEND_URL } from '../config';

interface VulnerabilitiesViewProps {
  vulnerabilities: Vulnerability[];
  setVulnerabilities: React.Dispatch<React.SetStateAction<Vulnerability[]>>;
}

export const VulnerabilitiesView: React.FC<VulnerabilitiesViewProps> = ({ vulnerabilities, setVulnerabilities }) => {
  const vulns = vulnerabilities;
  const setVulns = setVulnerabilities;
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('All');
  const [processingVulnId, setProcessingVulnId] = useState<string | null>(null);

  // Normalize impacted_agents: backend may return a comma-separated string
  const normVulns = vulns.map(v => {
    const raw: unknown = v.impacted_agents;
    const impacted_agents: string[] = Array.isArray(raw)
      ? (raw as string[])
      : typeof raw === 'string'
        ? raw.split(',').map(s => s.trim()).filter(Boolean)
        : [];
    return { ...v, impacted_agents };
  });

  const filteredVulns = normVulns.filter(v => {
    const matchesSearch = 
      v.cve_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.impacted_agents.join(' ').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSeverity = selectedSeverity === 'All' || v.severity === selectedSeverity;
    return matchesSearch && matchesSeverity;
  });

  const handleApplyPatch = async (vulnId: string) => {
    setProcessingVulnId(vulnId);
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/vulnerabilities/${vulnId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Patched' })
      });

      if (res.ok) {
        const updated = await res.json();
        setVulns(prev => prev.map(v => v.id === vulnId ? updated : v));
      }
    } catch (err) {
      console.error("Erreur lors de l'application du correctif:", err);
    } finally {
      setProcessingVulnId(null);
    }
  };

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'Critical': return 'var(--red)';
      case 'High': return 'var(--amber)';
      case 'Medium': return 'var(--cyan)';
      default: return 'var(--emerald)';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
        <div className="glass-panel" style={{ padding: '20px', borderLeft: '3px solid var(--red)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>CRITICAL CVEs</span>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, marginTop: '4px', color: 'var(--red)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={24} /> {normVulns.filter(v => v.severity === 'Critical' && v.status !== 'Patched').length}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px', borderLeft: '3px solid var(--amber)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>HIGH CVEs</span>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, marginTop: '4px', color: 'var(--amber)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={24} /> {normVulns.filter(v => v.severity === 'High' && v.status !== 'Patched').length}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px', borderLeft: '3px solid var(--emerald)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>RESOLVED VULNERABILITIES</span>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, marginTop: '4px', color: 'var(--emerald)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={24} /> {normVulns.filter(v => v.status === 'Patched').length}
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        
        {/* Search */}
        <div style={{ position: 'relative', width: '280px', flexGrow: 1 }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search CVE ID, Title, or Affected Host..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-primary)',
              borderRadius: '6px',
              padding: '8px 12px 8px 36px',
              color: '#ffffff',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
        </div>

        {/* Severity Filter */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {['All', 'Critical', 'High', 'Medium'].map(sev => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              style={{
                fontSize: '0.75rem',
                padding: '6px 12px',
                borderRadius: '6px',
                border: '1px solid',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backgroundColor: selectedSeverity === sev ? 'rgba(6, 182, 212, 0.15)' : 'rgba(15, 23, 42, 0.4)',
                color: selectedSeverity === sev ? 'var(--cyan)' : 'var(--text-secondary)',
                borderColor: selectedSeverity === sev ? 'var(--cyan)' : 'var(--border-primary)'
              }}
            >
              {sev === 'All' ? 'Tous' : sev}
            </button>
          ))}
        </div>

      </div>

      {/* Vulnerabilities Table / Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {filteredVulns.map(vuln => (
          <div key={vuln.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            
            {/* Header info */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  padding: '3px 8px',
                  borderRadius: '4px',
                  backgroundColor: getSeverityColor(vuln.severity) + '15',
                  color: getSeverityColor(vuln.severity),
                  border: `1px solid ${getSeverityColor(vuln.severity)}25`
                }}>
                  CVSS {vuln.cvss_score} - {vuln.severity}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--cyan)' }}>{vuln.cve_id}</span>
              </div>

              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: vuln.status === 'Patched' ? 'var(--emerald)' : vuln.status === 'Mitigated' ? 'var(--amber)' : 'var(--red)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <span style={{ 
                  width: '6px', 
                  height: '6px', 
                  borderRadius: '50%', 
                  background: vuln.status === 'Patched' ? 'var(--emerald)' : vuln.status === 'Mitigated' ? 'var(--amber)' : 'var(--red)' 
                }} />
                {vuln.status}
              </span>
            </div>

            {/* Title & Description */}
            <div>
              <h4 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '6px' }}>{vuln.title}</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{vuln.description}</p>
            </div>

            {/* Impacted Agents and Remediation */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '20px', fontSize: '0.8rem', borderTop: '1px solid var(--border-primary)', paddingTop: '12px' }}>
              <div>
                <strong style={{ color: 'var(--text-secondary)' }}>Impacted Machine:</strong>
                <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
                  {vuln.impacted_agents.map(agt => (
                    <span key={agt} style={{
                      background: 'rgba(255,255,255,0.03)',
                      border: '1px solid var(--border-primary)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>{agt}</span>
                  ))}
                </div>
              </div>

              <div>
                <strong style={{ color: 'var(--text-secondary)' }}>Remediation Strategy:</strong>
                <p style={{ marginTop: '6px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>{vuln.remediation}</p>
              </div>
            </div>

            {/* Apply patch action */}
            {vuln.status !== 'Patched' && (
              <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px dashed var(--border-primary)', paddingTop: '12px' }}>
                <button
                  disabled={processingVulnId === vuln.id}
                  onClick={() => handleApplyPatch(vuln.id)}
                  className="btn-primary"
                  style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                >
                  {processingVulnId === vuln.id ? (
                    <>Appliquant le Hotfix...</>
                  ) : (
                    <>
                      <FileCheck size={14} /> Virtual Patching (Wazuh Agent Hotfix)
                    </>
                  )}
                </button>
              </div>
            )}

          </div>
        ))}
      </div>

    </div>
  );
};
