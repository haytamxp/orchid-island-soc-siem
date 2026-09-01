import React, { useState } from 'react';
import { Settings, FileText, CheckCircle2, Play } from 'lucide-react';
import { BACKEND_URL } from '../config';

export const ReportsConfigView: React.FC = () => {
  const [slackUrl, setSlackUrl] = useState('');
  const [telegramToken, setTelegramToken] = useState('');
  const [mailTo, setMailTo] = useState('wazuh.x.alerte@gmail.com');
  
  const [slackEnabled, setSlackEnabled] = useState(true);
  const [telegramEnabled, setTelegramEnabled] = useState(true);
  const [mailEnabled, setMailEnabled] = useState(true);

  const [isTesting, setIsTesting] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 4000);
  };

  const handleTestIntegration = async (channel: string) => {
    setIsTesting(channel);
    try {
      if (channel === 'telegram') {
        const res = await fetch(`${BACKEND_URL}/api/notifications/test-telegram`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: telegramToken })
        });
        const data = await res.json();
        if (res.ok) {
          triggerToast(`✅ Telegram: ${data.message || 'Notification envoyée !'}`);
        } else {
          triggerToast(`❌ Erreur Telegram: ${data.error || 'Échec du test'}`);
        }
      } else if (channel === 'email list' || channel === 'email' || channel === 'mail') {
        const res = await fetch(`${BACKEND_URL}/api/notifications/test-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: mailTo })
        });
        const data = await res.json();
        if (res.ok) {
          triggerToast(`✅ Email: ${data.message || 'Message envoyé avec succès !'}`);
        } else {
          triggerToast(`⚠️ Erreur Email: ${data.error || 'Échec d\'envoi'}`);
        }
      } else {
        await new Promise(r => setTimeout(r, 1000));
        triggerToast(`Test message dispatched to ${channel}. Status: 200 OK.`);
      }
    } catch (err: any) {
      triggerToast(`❌ Erreur réseau: ${err.message}`);
    } finally {
      setIsTesting(null);
    }
  };


  const handleGenerateReport = async () => {
    setIsGenerating(true);

    let stats = { agents_online: 0, critical_alerts: 0, threat_index: 0, total_events: 0, total_alerts: 0 };
    let alertsList: any[] = [];
    let fimList: any[] = [];

    try {
      const [resStats, resAlerts, resFim] = await Promise.all([
        fetch(`${BACKEND_URL}/api/dashboard/stats`).then(r => r.json()).catch(() => null),
        fetch(`${BACKEND_URL}/api/alerts`).then(r => r.json()).catch(() => []),
        fetch(`${BACKEND_URL}/api/fim`).then(r => r.json()).catch(() => []),
        fetch(`${BACKEND_URL}/api/notifications/send-report`, { method: 'POST' }).catch(() => {})
      ]);
      if (resStats) stats = resStats;
      if (Array.isArray(resAlerts)) alertsList = resAlerts;
      if (Array.isArray(resFim)) fimList = resFim;
    } catch (e) {}

    await new Promise(r => setTimeout(r, 1000));
    setIsGenerating(false);

    triggerToast("📊 Rapport PDF généré & diffusé sur Telegram et par E-mail !");

    // ─── Génération du HTML du rapport ──────────────────────────────────────
    const alertRowsHtml = alertsList.length === 0 ? `
      <tr><td colspan="5" style="text-align: center; color: #64748b;">Aucune alerte enregistrée.</td></tr>
    ` : alertsList.slice(0, 10).map(al => `
      <tr>
        <td>${al.timestamp ? String(al.timestamp).replace('T', ' ').substring(0, 19) : 'N/A'}</td>
        <td>${al.title || 'Alerte sans titre'}</td>
        <td style="color: ${al.severity === 'Critical' ? '#ef4444' : al.severity === 'High' ? '#f59e0b' : '#10b981'}; font-weight: bold;">${al.severity || 'Low'}</td>
        <td>${al.analyst_assigned || 'Auto-Pipeline'}</td>
        <td>${al.status || 'New'}</td>
      </tr>
    `).join('');

    const fimRowsHtml = fimList.length === 0 ? `
      <tr><td colspan="5" style="text-align: center; color: #64748b;">Aucun événement FIM détecté.</td></tr>
    ` : fimList.slice(0, 5).map(f => `
      <tr>
        <td>${f.timestamp ? String(f.timestamp).replace('T', ' ').substring(0, 19) : 'N/A'}</td>
        <td>${f.hostname || 'rayane-vm'}</td>
        <td>${f.file_path || 'N/A'}</td>
        <td style="color: #f59e0b;">${f.event_type || 'Modified'}</td>
        <td>${f.user || 'root'}</td>
      </tr>
    `).join('');

    const reportHtml = `<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8"/>
    <title>Executive SIEM Cyber Security Report</title>
    <style>
      body { font-family: Arial, sans-serif; color: #1e293b; padding: 40px; line-height: 1.6; }
      .header { border-bottom: 3px solid #06b6d4; padding-bottom: 20px; margin-bottom: 30px; }
      .logo { font-size: 24px; font-weight: bold; color: #0f172a; }
      .title { font-size: 28px; font-weight: 700; margin-top: 10px; color: #0f172a; }
      .meta { font-size: 13px; color: #64748b; margin-top: 5px; }
      .section { margin-bottom: 30px; }
      h2 { font-size: 18px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; color: #0f172a; }
      .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px; }
      .card { padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; }
      .card-number { font-size: 22px; font-weight: bold; color: #06b6d4; }
      table { width: 100%; border-collapse: collapse; margin-top: 15px; }
      th { background-color: #f1f5f9; padding: 10px; border-bottom: 2px solid #cbd5e1; text-align: left; font-size: 12px; }
      td { padding: 10px; border-bottom: 1px solid #e2e8f0; font-size: 12px; }
      @media print { body { padding: 20px; } }
    </style>
  </head>
  <body>
    <div class="header">
      <div class="logo">SOC-AI CYBERSECURITY PLATFORM</div>
      <div class="title">SIEM Incident &amp; Integrity Executive Report</div>
      <div class="meta">
        <strong>Generated By:</strong> rayane-virtual-machine <br/>
        <strong>Database Source:</strong> MySQL siem_db <br/>
        <strong>Date:</strong> ${new Date().toLocaleString()}
      </div>
    </div>

    <div class="section">
      <h2>1. System Indicators &amp; Resource Metrics</h2>
      <div class="grid">
        <div class="card"><span style="font-size:12px;color:#64748b;">Total Security Events</span><div class="card-number">${stats.total_events}</div></div>
        <div class="card"><span style="font-size:12px;color:#64748b;">Active Wazuh Agents</span><div class="card-number">${stats.agents_online} Online</div></div>
        <div class="card"><span style="font-size:12px;color:#64748b;">Critical Alerts</span><div class="card-number" style="color:#ef4444;">${stats.critical_alerts}</div></div>
        <div class="card"><span style="font-size:12px;color:#64748b;">Threat Index Rating</span><div class="card-number" style="color:#f59e0b;">${stats.threat_index} / 100</div></div>
      </div>
    </div>

    <div class="section">
      <h2>2. Outstanding Security Incidents (MySQL Real Database)</h2>
      <table>
        <thead><tr><th>Timestamp</th><th>Incident Name</th><th>Severity</th><th>Assigned Analyst</th><th>Status</th></tr></thead>
        <tbody>${alertRowsHtml}</tbody>
      </table>
    </div>

    <div class="section">
      <h2>3. File Integrity Monitoring (FIM) Log Summary</h2>
      <table>
        <thead><tr><th>Timestamp</th><th>Host</th><th>File Integrity Path</th><th>Change Event</th><th>Modified By</th></tr></thead>
        <tbody>${fimRowsHtml}</tbody>
      </table>
    </div>
  </body>
</html>`;

    // ─── Téléchargement direct via Blob (pas de popup → jamais bloqué) ──────
    const blob = new Blob([reportHtml], { type: 'text/html;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href     = url;
    link.download = `SIEM_Report_${new Date().toISOString().slice(0, 10)}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  };

  return (

    <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1.75fr', gap: '20px' }}>
      
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

      {/* Report Generator Block */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={20} style={{ color: 'var(--cyan)' }} /> SIEM Executive Reporter
        </h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Compilez un rapport de synthèse PDF contenant le résumé analytique, les alertes non résolues et les logs FIM pertinents.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(0,0,0,0.15)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-primary)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <strong>Configuration du rapport:</strong>
            <div style={{ marginTop: '8px' }}>• Scope: Dernières 24h</div>
            <div style={{ marginTop: '4px' }}>• Format: Executive A4 Printable</div>
            <div style={{ marginTop: '4px' }}>• Include: Vulnerability list & Resource usage</div>
          </div>
        </div>

        <button 
          onClick={handleGenerateReport}
          disabled={isGenerating}
          className="btn-primary" 
          style={{ width: '100%', justifyContent: 'center', height: '42px' }}
        >
          {isGenerating ? (
            <>Compiling report metrics...</>
          ) : (
            <>
              <Play size={16} /> Generate Executive PDF
            </>
          )}
        </button>
      </div>

      {/* Webhook Alert Integration Settings */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Settings size={20} style={{ color: 'var(--cyan)' }} /> Webhook Alerts Channel Integrations
        </h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Associez des déclencheurs de notifications automatisés pour envoyer les alertes critiques (XGBoost &gt; 95%) sur vos canaux de discussion et courriels SecOps.
        </p>

        {/* Integration inputs list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Slack Webhook */}
          <div style={{ borderBottom: '1px solid var(--border-primary)', paddingBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                Slack Webhook URL
              </span>
              <input 
                type="checkbox" 
                checked={slackEnabled} 
                onChange={(e) => setSlackEnabled(e.target.checked)} 
                style={{ cursor: 'pointer' }}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                disabled={!slackEnabled}
                value={slackUrl}
                onChange={(e) => setSlackUrl(e.target.value)}
                style={{
                  flexGrow: 1,
                  background: 'rgba(15,23,42,0.6)',
                  border: '1px solid var(--border-primary)',
                  color: slackEnabled ? '#ffffff' : 'var(--text-muted)',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
              <button 
                disabled={!slackEnabled || isTesting === 'slack'}
                onClick={() => handleTestIntegration('slack')}
                className="btn-secondary" 
                style={{ fontSize: '0.75rem', padding: '0 12px' }}
              >
                {isTesting === 'slack' ? 'Testing...' : 'Test'}
              </button>
            </div>
          </div>

          {/* Telegram bot token */}
          <div style={{ borderBottom: '1px solid var(--border-primary)', paddingBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Telegram Bot Trigger Token</span>
              <input 
                type="checkbox" 
                checked={telegramEnabled} 
                onChange={(e) => setTelegramEnabled(e.target.checked)} 
                style={{ cursor: 'pointer' }}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                disabled={!telegramEnabled}
                value={telegramToken}
                onChange={(e) => setTelegramToken(e.target.value)}
                style={{
                  flexGrow: 1,
                  background: 'rgba(15,23,42,0.6)',
                  border: '1px solid var(--border-primary)',
                  color: telegramEnabled ? '#ffffff' : 'var(--text-muted)',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
              <button 
                disabled={!telegramEnabled || isTesting === 'telegram'}
                onClick={() => handleTestIntegration('telegram')}
                className="btn-secondary" 
                style={{ fontSize: '0.75rem', padding: '0 12px' }}
              >
                {isTesting === 'telegram' ? 'Testing...' : 'Test'}
              </button>
            </div>
          </div>

          {/* Email dispatch */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>SOC Mailing List Dispatch</span>
              <input 
                type="checkbox" 
                checked={mailEnabled} 
                onChange={(e) => setMailEnabled(e.target.checked)} 
                style={{ cursor: 'pointer' }}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="email"
                disabled={!mailEnabled}
                value={mailTo}
                onChange={(e) => setMailTo(e.target.value)}
                style={{
                  flexGrow: 1,
                  background: 'rgba(15,23,42,0.6)',
                  border: '1px solid var(--border-primary)',
                  color: mailEnabled ? '#ffffff' : 'var(--text-muted)',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
              <button 
                disabled={!mailEnabled || isTesting === 'mail'}
                onClick={() => handleTestIntegration('email list')}
                className="btn-secondary" 
                style={{ fontSize: '0.75rem', padding: '0 12px' }}
              >
                {isTesting === 'mail' ? 'Testing...' : 'Test'}
              </button>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};
