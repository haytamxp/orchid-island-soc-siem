import React, { useState, useEffect } from 'react';
import type { Alert, AiReport } from '../data/mockData';
import { BrainCircuit, Loader2, Save, CheckCircle2, User, ShieldCheck, HelpCircle } from 'lucide-react';
import { BACKEND_URL } from '../config';

interface AlertsViewProps {
  alerts: Alert[];
  aiReports: AiReport[];
  setAlerts: React.Dispatch<React.SetStateAction<Alert[]>>;
  setAiReports: React.Dispatch<React.SetStateAction<AiReport[]>>;
}

export const AlertsView: React.FC<AlertsViewProps> = ({ alerts, aiReports, setAlerts, setAiReports }) => {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(alerts[0] || null);
  const [analyzingAlertId, setAnalyzingAlertId] = useState<number | null>(null);
  const [aiReportOutput, setAiReportOutput] = useState<string>('');
  const [isSavingReport, setIsSavingReport] = useState<boolean>(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saved'>('idle');
  const [loadingStepText, setLoadingStepText] = useState<string>('');

  // Update selected alert details if the alerts array changes
  useEffect(() => {
    if (selectedAlert) {
      const updated = alerts.find(a => a.id === selectedAlert.id);
      if (updated) setSelectedAlert(updated);
    }
  }, [alerts]);

  // Read associated report if it already exists
  const getExistingReport = (alert: Alert) => {
    if (alert.ai_report_id) {
      return aiReports.find(r => r.id === alert.ai_report_id);
    }
    // Fallback: look up by alert_id in aiReports
    return aiReports.find(r => r.alert_id === alert.id);
  };

  const activeReport = selectedAlert ? getExistingReport(selectedAlert) : null;

  // Custom Markdown Parser to avoid external library friction
  const renderMarkdown = (text: string) => {
    if (!text) return null;
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('# ')) {
        return (
          <h3 key={idx} style={{ 
            fontSize: '1.2rem', 
            fontWeight: 700, 
            color: 'var(--cyan)', 
            borderBottom: '1px solid var(--border-primary)', 
            paddingBottom: '6px', 
            marginTop: '20px', 
            marginBottom: '10px' 
          }}>
            {line.replace('# ', '')}
          </h3>
        );
      }
      if (line.startsWith('- ')) {
        return (
          <li key={idx} style={{ marginLeft: '20px', marginBottom: '6px', color: 'var(--text-primary)', fontSize: '0.9rem' }}>
            {line.replace('- ', '')}
          </li>
        );
      }
      if (line.trim() === '') {
        return <div key={idx} style={{ height: '10px' }} />;
      }
      // Bold text handling
      let content: React.ReactNode = line;
      if (line.includes('**')) {
        const parts = line.split('**');
        content = parts.map((part, partIdx) => partIdx % 2 === 1 ? <strong key={partIdx} style={{ color: 'var(--cyan)' }}>{part}</strong> : part);
      }
      return <p key={idx} style={{ fontSize: '0.9rem', lineHeight: '1.5', color: 'var(--text-secondary)', marginBottom: '8px' }}>{content}</p>;
    });
  };

  // Perform AI Analysis using local backend LLM generator
  const handleAiAnalysis = async (alert: Alert) => {
    setAnalyzingAlertId(alert.id);
    setAiReportOutput('');
    setSaveStatus('idle');

    try {
      setLoadingStepText("Analyse contextuelle du pipeline IA Flask en cours...");
      await new Promise(r => setTimeout(r, 600));

      setLoadingStepText("Génération du rapport d'incident avec métriques réelles MySQL...");

      const response = await fetch(`${BACKEND_URL}/api/reports/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: alert.title,
          severity: alert.severity,
          description: alert.description,
          rule_id: alert.rule_id,
          xgboost_probability: alert.xgboost_probability
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAnalyzingAlertId(null);
        setAiReportOutput(data.markdown_content);
        return;
      }
    } catch (err) {
      console.warn("API report generation error:", err);
    }

    setAnalyzingAlertId(null);
  };

  // Persist the generated AI report back to mock MySQL lists
  const handleSaveReport = async () => {
    if (!selectedAlert || (!aiReportOutput && !activeReport)) return;

    setIsSavingReport(true);
    const content = aiReportOutput || (activeReport ? activeReport.markdown_content : '');

    try {
      const response = await fetch(`${BACKEND_URL}/api/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert_id: selectedAlert.id,
          markdown_content: content
        })
      });

      if (response.ok) {
        const newReport = await response.json();
        
        // Save report in reports array
        setAiReports(prev => {
          if (prev.some(r => r.id === newReport.id)) return prev;
          return [...prev, newReport];
        });

        // Update alert to point to new report
        setAlerts(prev => prev.map(a => {
          if (a.id === selectedAlert.id) {
            return { ...a, ai_report_id: newReport.id };
          }
          return a;
        }));

        setSaveStatus('saved');
        setAiReportOutput('');
      } else {
        console.error("Échec de la sauvegarde du rapport", response.statusText);
      }
    } catch (err) {
      console.error("Erreur de connexion au backend pour sauvegarder le rapport:", err);
    } finally {
      setIsSavingReport(false);
    }
  };

  const handleStatusChange = async (alertId: number, newStatus: 'New' | 'Acknowledged' | 'Resolved') => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/alerts/${alertId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        const updatedAlert = await response.json();
        setAlerts(prev => prev.map(a => a.id === alertId ? updatedAlert : a));
      }
    } catch (err) {
      console.error("Erreur de mise à jour du statut de l'alerte:", err);
    }
  };

  const handleAnalystChange = async (alertId: number, analyst: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/alerts/${alertId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analyst_assigned: analyst })
      });

      if (response.ok) {
        const updatedAlert = await response.json();
        setAlerts(prev => prev.map(a => a.id === alertId ? updatedAlert : a));
      }
    } catch (err) {
      console.error("Erreur de mise à jour de l'analyste de l'alerte:", err);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1.75fr', gap: '20px', height: 'calc(100vh - 160px)', minHeight: '550px' }}>
      
      {/* Left panel: Alerts list */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          Alert Feed <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '10px', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>MySQL Database</span>
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto', flexGrow: 1, paddingRight: '4px' }}>
          {alerts.map(alert => {
            const isSelected = selectedAlert?.id === alert.id;
            const hasReport = getExistingReport(alert);
            return (
              <div
                key={alert.id}
                onClick={() => {
                  setSelectedAlert(alert);
                  setAiReportOutput('');
                  setSaveStatus('idle');
                }}
                className="glass-panel"
                style={{
                  padding: '14px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  background: isSelected ? 'rgba(6, 182, 212, 0.05)' : 'rgba(255,255,255,0.01)',
                  borderColor: isSelected ? 'var(--cyan)' : 'var(--border-primary)',
                  borderLeft: `4px solid ${alert.severity === 'Critical' ? 'var(--red)' : alert.severity === 'High' ? 'var(--amber)' : 'var(--cyan)'}`
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: isSelected ? '#ffffff' : 'var(--text-primary)' }}>
                    {alert.title}
                  </span>
                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    backgroundColor: alert.severity === 'Critical' ? 'rgba(239, 68, 68, 0.15)' : alert.severity === 'High' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                    color: alert.severity === 'Critical' ? 'var(--red)' : alert.severity === 'High' ? 'var(--amber)' : 'var(--cyan)'
                  }}>
                    {alert.severity}
                  </span>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  <span style={{ 
                    background: 'rgba(6, 182, 212, 0.1)', 
                    color: 'var(--cyan)', 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontWeight: 600,
                    border: '1px solid rgba(6,182,212,0.2)'
                  }}>
                    XGBoost: {alert.xgboost_probability}%
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {alert.timestamp.split(' ')[1]}
                  </span>
                </div>

                {hasReport && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '8px', fontSize: '0.7rem', color: 'var(--emerald)' }}>
                    <ShieldCheck size={12} /> AI Report Saved
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right panel: Details and AI Report generator */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', overflow: 'hidden' }}>
        
        {selectedAlert ? (
          <>
            {/* Incident Details Card */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>INCIDENT #{selectedAlert.id}</span>
                    <span style={{
                      fontSize: '0.75rem',
                      color: selectedAlert.status === 'Resolved' ? 'var(--emerald)' : selectedAlert.status === 'Acknowledged' ? 'var(--amber)' : 'var(--red)',
                      background: selectedAlert.status === 'Resolved' ? 'rgba(16, 185, 129, 0.1)' : selectedAlert.status === 'Acknowledged' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      padding: '1px 6px',
                      borderRadius: '4px',
                      fontWeight: 600
                    }}>
                      {selectedAlert.status}
                    </span>
                  </div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '4px' }}>{selectedAlert.title}</h2>
                </div>
                
                {/* AI Trigger */}
                {!activeReport && !aiReportOutput && (
                  <button
                    disabled={analyzingAlertId === selectedAlert.id}
                    onClick={() => handleAiAnalysis(selectedAlert)}
                    className="btn-primary"
                    style={{ fontSize: '0.85rem' }}
                  >
                    {analyzingAlertId === selectedAlert.id ? (
                      <>
                        <Loader2 size={16} className="animate-spin" /> Analysing...
                      </>
                    ) : (
                      <>
                        <BrainCircuit size={16} /> Ollama Llama3.2
                      </>
                    )}
                  </button>
                )}
              </div>

              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '20px' }}>
                {selectedAlert.description}
              </p>

              {/* Assignment & Status Selectors */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', borderTop: '1px solid var(--border-primary)', paddingTop: '16px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Analyst Assigned</label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <User size={14} style={{ color: 'var(--text-muted)' }} />
                    <select
                      value={selectedAlert.analyst_assigned}
                      onChange={(e) => handleAnalystChange(selectedAlert.id, e.target.value)}
                      style={{
                        background: 'rgba(15,23,42,0.6)',
                        border: '1px solid var(--border-primary)',
                        color: 'var(--text-primary)',
                        padding: '6px 10px',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        width: '100%',
                        outline: 'none'
                      }}
                    >
                      <option value="Unassigned">Unassigned</option>
                      <option value="Rayane (SecOps)">Rayane (SecOps)</option>
                      <option value="Alex (Tier 2)">Alex (Tier 2)</option>
                      <option value="SOC Automateur">SOC Automateur</option>
                    </select>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Alert Status</label>
                  <select
                    value={selectedAlert.status}
                    onChange={(e) => handleStatusChange(selectedAlert.id, e.target.value as any)}
                    style={{
                      background: 'rgba(15,23,42,0.6)',
                      border: '1px solid var(--border-primary)',
                      color: 'var(--text-primary)',
                      padding: '6px 10px',
                      borderRadius: '6px',
                      fontSize: '0.8rem',
                      width: '100%',
                      outline: 'none'
                    }}
                  >
                    <option value="New">New</option>
                    <option value="Acknowledged">Acknowledged</option>
                    <option value="Resolved">Resolved</option>
                  </select>
                </div>
              </div>
            </div>

            {/* AI Report / Generating Workspace */}
            <div className="glass-panel" style={{ padding: '20px', flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative' }}>
              
              {/* Scan effect during loading */}
              {analyzingAlertId === selectedAlert.id && <div className="scanning-line" />}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <BrainCircuit size={16} style={{ color: 'var(--cyan)' }} /> SOC-AI Analysis Report
                </h4>
                
                {/* Actions on report */}
                {(aiReportOutput || activeReport) && saveStatus === 'idle' && (
                  <button
                    disabled={isSavingReport}
                    onClick={handleSaveReport}
                    className="btn-primary"
                    style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                  >
                    {isSavingReport ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <>
                        <Save size={12} /> Persist in MySQL
                      </>
                    )}
                  </button>
                )}

                {saveStatus === 'saved' && (
                  <span style={{ color: 'var(--emerald)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
                    <CheckCircle2 size={14} /> Persisted successfully!
                  </span>
                )}
              </div>

              {/* Body rendering */}
              <div style={{ flexGrow: 1, overflowY: 'auto', background: 'rgba(0, 0, 0, 0.2)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.02)' }}>
                {analyzingAlertId === selectedAlert.id ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '12px' }}>
                    <Loader2 size={32} className="animate-spin" style={{ color: 'var(--cyan)' }} />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                      {loadingStepText}
                    </span>
                  </div>
                ) : activeReport ? (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '14px', borderBottom: '1px dashed var(--border-primary)', paddingBottom: '8px' }}>
                      <span>MySQL Report ID: #{activeReport.id}</span>
                      <span>Generated: {activeReport.generated_at}</span>
                    </div>
                    {renderMarkdown(activeReport.markdown_content)}
                  </div>
                ) : aiReportOutput ? (
                  renderMarkdown(aiReportOutput)
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', gap: '10px' }}>
                    <HelpCircle size={32} />
                    <p style={{ fontSize: '0.85rem' }}>Aucun rapport IA disponible. Cliquez sur "Ollama Llama3.2" ci-dessus pour générer une analyse.</p>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Sélectionnez une alerte pour l'analyser.
          </div>
        )}
      </div>
    </div>
  );
};
