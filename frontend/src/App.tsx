import React, { useState, useEffect } from 'react';
import type {
  Agent,
  SecurityEvent,
  Alert,
  AiReport,
  Vulnerability,
  ThreatIntelIOC
} from './data/mockData';
import { BACKEND_URL, WEBSOCKET_URL } from './config';

// Views
import { AdminLogin } from './components/AdminLogin';
import { DashboardView } from './components/DashboardView';
import { EventsView } from './components/EventsView';
import { AlertsView } from './components/AlertsView';
import { AgentsView } from './components/AgentsView';
import { SuricataView } from './components/SuricataView';
import { FimView } from './components/FimView';
import { VulnerabilitiesView } from './components/VulnerabilitiesView';
import { VirusTotalView } from './components/VirusTotalView';
import { ThreatIntelView } from './components/ThreatIntelView';
import { ReportsConfigView } from './components/ReportsConfigView';

// Icons
import { 
  LayoutDashboard, 
  ShieldAlert, 
  BrainCircuit, 
  Laptop, 
  Network, 
  FileCode, 
  Search, 
  Target, 
  Settings, 
  ChevronLeft, 
  ChevronRight, 
  Bell, 
  Clock, 
  Globe,
  LogOut
} from 'lucide-react';

export const App: React.FC = () => {
  // Authentication State — checks localStorage for persisted session (any non-empty token)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    () => !!localStorage.getItem('siem_session')
  );
  // Incrementing key forces AdminLogin to fully remount on logout (clears all form state + browser autofill)
  const [logoutKey, setLogoutKey] = useState<number>(0);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('siem_session');
    setIsAuthenticated(false);
    setActiveView('Dashboard');
    setLogoutKey(prev => prev + 1); // Force AdminLogin remount
  };

  // Global Session State
  const [agents, setAgents] = useState<Agent[]>([]);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [aiReports, setAiReports] = useState<AiReport[]>([]);
  const [fimEvents, setFimEvents] = useState<any[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [iocs, setIocs] = useState<ThreatIntelIOC[]>([]);

  useEffect(() => {
    // 1. Fetch initial states
    const fetchData = async () => {
      try {
        const resAgents = await fetch(`${BACKEND_URL}/api/agents`);
        if (resAgents.ok) {
          const data = await resAgents.json();
          setAgents(Array.isArray(data) ? data : (data.data || []));
        }

        const resEvents = await fetch(`${BACKEND_URL}/api/events`);
        if (resEvents.ok) {
          const data = await resEvents.json();
          setEvents(Array.isArray(data) ? data : (data.data || []));
        }

        const resAlerts = await fetch(`${BACKEND_URL}/api/alerts`);
        if (resAlerts.ok) {
          const data = await resAlerts.json();
          setAlerts(Array.isArray(data) ? data : (data.data || []));
        }

        const resReports = await fetch(`${BACKEND_URL}/api/reports`);
        if (resReports.ok) {
          const data = await resReports.json();
          setAiReports(Array.isArray(data) ? data : (data.data || []));
        }

        const resFim = await fetch(`${BACKEND_URL}/api/fim`);
        if (resFim.ok) {
          const data = await resFim.json();
          setFimEvents(Array.isArray(data) ? data : (data.data || []));
        }

        const resVulns = await fetch(`${BACKEND_URL}/api/vulnerabilities`);
        if (resVulns.ok) {
          const data = await resVulns.json();
          setVulnerabilities(Array.isArray(data) ? data : (data.data || []));
        }

        const resIocs = await fetch(`${BACKEND_URL}/api/iocs`);
        if (resIocs.ok) {
          const data = await resIocs.json();
          setIocs(Array.isArray(data) ? data : (data.data || []));
        }
      } catch (err) {
        console.error("Erreur lors de la récupération des données de l'API SIEM backend:", err);
      }
    };
    
    fetchData();

    // 2. Setup WebSocket for real-time events
    let ws: WebSocket;
    let reconnectTimeout: any;

    const connectWebSocket = () => {
      ws = new WebSocket(WEBSOCKET_URL);

      ws.onopen = () => {
        console.log("[WEBSOCKET] Connecté au serveur SIEM");
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const { type, payload } = message;

          if (type === 'NEW_ALERT') {
            setAlerts(prev => {
              if (prev.some(a => a.id === payload.id)) return prev;
              return [payload, ...prev];
            });
          } else if (type === 'NEW_EVENT') {
            setEvents(prev => {
              if (prev.some(e => e.id === payload.id)) return prev;
              return [payload, ...prev];
            });
          } else if (type === 'UPDATE_ALERT') {
            setAlerts(prev => prev.map(a => a.id === payload.id ? payload : a));
          } else if (type === 'NEW_REPORT') {
            setAiReports(prev => {
              if (prev.some(r => r.id === payload.id)) return prev;
              return [...prev, payload];
            });
          } else if (type === 'UPDATE_AGENT') {
            setAgents(prev => prev.map(a => a.id === payload.id ? payload : a));
          } else if (type === 'UPDATE_VULNERABILITY') {
            setVulnerabilities(prev => prev.map(v => v.id === payload.id ? payload : v));
          } else if (type === 'NEW_IOC') {
            setIocs(prev => {
              if (prev.some(i => i.id === payload.id)) return prev;
              return [payload, ...prev];
            });
          } else if (type === 'DELETE_IOC') {
            setIocs(prev => prev.filter(i => i.id !== payload.id));
          }
        } catch (err) {
          console.error("Erreur lors du traitement du message WebSocket:", err);
        }
      };

      ws.onclose = () => {
        console.warn("[WEBSOCKET] Connexion fermée. Reconnexion automatique dans 5 secondes...");
        reconnectTimeout = setTimeout(connectWebSocket, 5000);
      };
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
      clearTimeout(reconnectTimeout);
    };
  }, []);

  // Layout States
  const [activeView, setActiveView] = useState<string>('Dashboard');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [timeRange, setTimeRange] = useState<string>('Last 24h');
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const [showTimeDropdown, setShowTimeDropdown] = useState<boolean>(false);

  const timeOptions = [
    { value: 'Live',       label: '🔴 Live Feed' },
    { value: 'Last 24h',   label: '⏱ Dernières 24h' },
    { value: 'Last 7 days',label: '📅 7 derniers jours' },
    { value: 'Custom',     label: '✏️ Personnalisé' },
  ];

  // Sidebar Menu configuration
  const navigationItems = [
    { name: 'Dashboard', icon: <LayoutDashboard size={18} /> },
    { name: 'Security Events', icon: <Globe size={18} /> },
    { name: 'Alerts & AI Insights', icon: <BrainCircuit size={18} />, badge: alerts.filter(a => a.status === 'New').length },
    { name: 'Wazuh Agents', icon: <Laptop size={18} /> },
    { name: 'Suricata IDS', icon: <Network size={18} /> },
    { name: 'File Integrity (FIM)', icon: <FileCode size={18} /> },
    { name: 'Vulnerability Detection', icon: <ShieldAlert size={18} /> },
    { name: 'VirusTotal Scan', icon: <Search size={18} /> },
    { name: 'Threat Intelligence', icon: <Target size={18} /> },
    { name: 'Reports & Configurations', icon: <Settings size={18} /> },
  ];

  // Global Notification logs
  const notifications = [
    { text: "Nouvelle tentative d'injection SQL bloquée sur soc-web-prod-01", time: "Il y a 3 mins", type: "critical" },
    { text: "Wazuh Agent 'soc-mail-gateway' marqué hors-ligne", time: "Il y a 4 heures", type: "warning" },
    { text: "Audit FIM : fichier modifié /etc/shadow sur soc-web-prod-01", time: "Il y a 5 mins", type: "info" }
  ];

  const filterByTimeRange = <T extends { timestamp: string }>(items: T[]): T[] => {
    if (timeRange === 'Live') {
      return items; // Tout afficher en mode Live
    }
    
    const now = new Date();
    const limitDate = new Date();
    
    if (timeRange === 'Last 24h') {
      limitDate.setHours(now.getHours() - 24);
    } else if (timeRange === 'Last 7 days') {
      limitDate.setDate(now.getDate() - 7);
    } else if (timeRange === 'Custom') {
      // Pour le mode personnalisé, on filtre par exemple sur les 3 derniers jours
      limitDate.setDate(now.getDate() - 3);
    }
    
    return items.filter(item => {
      if (!item.timestamp) return false;
      const formattedTimestamp = item.timestamp.includes('T') ? item.timestamp : item.timestamp.replace(' ', 'T');
      const itemDate = new Date(formattedTimestamp);
      return itemDate >= limitDate;
    });
  };

  // Dispatch view renders
  const renderActiveView = () => {
    const filteredEvents = filterByTimeRange(events);
    const filteredAlerts = filterByTimeRange(alerts);

    switch (activeView) {
      case 'Dashboard':
        return <DashboardView events={filteredEvents} alerts={filteredAlerts} agents={agents} setView={setActiveView} />;
      case 'Security Events':
        return <EventsView events={filteredEvents} />;
      case 'Alerts & AI Insights':
        return <AlertsView alerts={filteredAlerts} aiReports={aiReports} setAlerts={setAlerts} setAiReports={setAiReports} />;
      case 'Wazuh Agents':
        return <AgentsView agents={agents} setAgents={setAgents} />;
      case 'Suricata IDS':
        return <SuricataView events={filteredEvents} />;
      case 'File Integrity (FIM)':
        return <FimView fimEvents={fimEvents} />;
      case 'Vulnerability Detection':
        return <VulnerabilitiesView vulnerabilities={vulnerabilities} setVulnerabilities={setVulnerabilities} />;
      case 'VirusTotal Scan':
        return <VirusTotalView />;
      case 'Threat Intelligence':
        return <ThreatIntelView iocs={iocs} setIocs={setIocs} />;
      case 'Reports & Configurations':
        return <ReportsConfigView />;
      default:
        return <DashboardView events={filteredEvents} alerts={filteredAlerts} agents={agents} setView={setActiveView} />;
    }
  };

  // If not authenticated, render ONLY the login screen
  // key={logoutKey} forces a full remount each time the user logs out → clears all form state + browser autofill
  if (!isAuthenticated) {
    return <AdminLogin key={logoutKey} onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      
      {/* Sidebar Layout */}
      <aside 
        className="glass-panel" 
        style={{
          width: isSidebarCollapsed ? '72px' : '260px',
          minWidth: isSidebarCollapsed ? '72px' : '260px',
          borderRight: '1px solid var(--border-primary)',
          borderRadius: '0',
          display: 'flex',
          flexDirection: 'column',
          transition: 'var(--transition-smooth)',
          zIndex: 100,
          position: 'sticky',
          top: 0,
          height: '100vh',
          boxShadow: '4px 0 30px rgba(0, 0, 0, 0.5)'
        }}
      >
        {/* Title banner */}
        <div style={{
          padding: '20px 16px',
          borderBottom: '1px solid var(--border-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: isSidebarCollapsed ? 'center' : 'space-between',
          height: '70px'
        }}>
          {!isSidebarCollapsed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ background: 'rgba(6, 182, 212, 0.1)', padding: '6px', borderRadius: '6px' }}>
                <BrainCircuit style={{ color: 'var(--cyan)' }} size={20} />
              </div>
              <span style={{ fontWeight: 800, fontSize: '1.05rem', letterSpacing: '0.5px' }}>
                SOC<span style={{ color: 'var(--cyan)' }}>-AI</span> SIEM
              </span>
            </div>
          )}
          {isSidebarCollapsed && (
            <BrainCircuit style={{ color: 'var(--cyan)' }} size={24} />
          )}

          <button 
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '4px',
              borderRadius: '4px'
            }}
          >
            {isSidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation list */}
        <nav style={{ padding: '20px 8px', display: 'flex', flexDirection: 'column', gap: '6px', flexGrow: 1, overflowY: 'auto' }}>
          {navigationItems.map(item => {
            const isActive = activeView === item.name;
            return (
              <button
                key={item.name}
                onClick={() => setActiveView(item.name)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s',
                  background: isActive ? 'linear-gradient(90deg, rgba(6, 182, 212, 0.15) 0%, rgba(6, 182, 212, 0) 100%)' : 'none',
                  borderLeft: isActive ? '3px solid var(--cyan)' : '3px solid transparent',
                  color: isActive ? '#ffffff' : 'var(--text-secondary)',
                  justifyContent: isSidebarCollapsed ? 'center' : 'flex-start'
                }}
                title={item.name}
              >
                <div style={{ color: isActive ? 'var(--cyan)' : 'inherit', display: 'flex', alignItems: 'center' }}>
                  {item.icon}
                </div>
                {!isSidebarCollapsed && (
                  <span style={{ fontSize: '0.875rem', fontWeight: isActive ? 600 : 500, flexGrow: 1 }}>
                    {item.name}
                  </span>
                )}
                {!isSidebarCollapsed && item.badge && item.badge > 0 ? (
                  <span style={{
                    fontSize: '0.7rem',
                    background: 'var(--red)',
                    color: '#ffffff',
                    padding: '2px 6px',
                    borderRadius: '10px',
                    fontWeight: 700
                  }}>
                    {item.badge}
                  </span>
                ) : null}
              </button>
            );
          })}
        </nav>

        {/* Connected Node Pulsing footer */}
        <div style={{
          padding: '16px',
          borderTop: '1px solid var(--border-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          justifyContent: isSidebarCollapsed ? 'center' : 'flex-start',
          height: '60px',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
          background: 'rgba(0,0,0,0.1)'
        }}>
          <span className="pulse-green"></span>
          {!isSidebarCollapsed && (
            <span style={{ fontWeight: 500 }}>Node: Connected (MySQL Active)</span>
          )}
        </div>

      </aside>

      {/* Main Panel Viewport */}
      <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, minWidth: 0 }}>
        
        {/* Header bar */}
        <header style={{
          height: '70px',
          borderBottom: '1px solid var(--border-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          background: 'rgba(15, 23, 42, 0.3)',
          backdropFilter: 'blur(8px)',
          position: 'sticky',
          top: 0,
          zIndex: 90
        }}>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, letterSpacing: '-0.2px' }}>
              {activeView}
            </h1>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            
            {/* ── Custom Time Range Dropdown ── */}
            <div style={{ position: 'relative' }}>
              {/* Trigger button */}
              <button
                onClick={() => { setShowTimeDropdown(p => !p); setShowNotifications(false); }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'rgba(15, 23, 42, 0.7)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '8px',
                  padding: '6px 12px',
                  color: 'var(--text-primary)',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'border-color 0.2s',
                  whiteSpace: 'nowrap'
                }}
                onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--cyan)')}
                onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border-primary)')}
              >
                <Clock size={13} style={{ color: 'var(--text-muted)' }} />
                {timeOptions.find(o => o.value === timeRange)?.label ?? timeRange}
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ marginLeft: '2px', opacity: 0.5, transform: showTimeDropdown ? 'rotate(180deg)' : 'none', transition: '0.2s' }}>
                  <path d="M1 3l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              {/* Overlay to close on outside click */}
              {showTimeDropdown && (
                <div
                  onClick={() => setShowTimeDropdown(false)}
                  style={{ position: 'fixed', inset: 0, zIndex: 998 }}
                />
              )}

              {/* Options list */}
              {showTimeDropdown && (
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 6px)',
                  right: 0,
                  minWidth: '180px',
                  background: '#0f1729',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '10px',
                  boxShadow: '0 12px 40px rgba(0,0,0,0.7)',
                  overflow: 'hidden',
                  zIndex: 999
                }}>
                  {timeOptions.map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => { setTimeRange(opt.value); setShowTimeDropdown(false); }}
                      style={{
                        width: '100%',
                        textAlign: 'left',
                        padding: '10px 14px',
                        background: timeRange === opt.value ? 'rgba(6,182,212,0.12)' : 'transparent',
                        border: 'none',
                        color: timeRange === opt.value ? 'var(--cyan)' : 'var(--text-primary)',
                        fontSize: '0.78rem',
                        fontWeight: timeRange === opt.value ? 600 : 400,
                        cursor: 'pointer',
                        transition: 'background 0.15s',
                        borderLeft: timeRange === opt.value ? '2px solid var(--cyan)' : '2px solid transparent'
                      }}
                      onMouseEnter={e => { if (timeRange !== opt.value) (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.04)'; }}
                      onMouseLeave={e => { if (timeRange !== opt.value) (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* ── Notification Bell ── */}
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => { setShowNotifications(p => !p); setShowTimeDropdown(false); }}
                style={{
                  background: showNotifications ? 'rgba(6,182,212,0.1)' : 'none',
                  border: showNotifications ? '1px solid rgba(6,182,212,0.3)' : '1px solid transparent',
                  borderRadius: '50%',
                  color: showNotifications ? 'var(--cyan)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '7px',
                  transition: '0.2s'
                }}
              >
                <Bell size={18} />
                <span style={{
                  position: 'absolute',
                  top: '4px',
                  right: '4px',
                  width: '7px',
                  height: '7px',
                  borderRadius: '50%',
                  background: 'var(--red)',
                  boxShadow: '0 0 6px var(--red)',
                  animation: 'glow-pulse 1.5s ease-in-out infinite'
                }} />
              </button>

              {/* Click-outside overlay */}
              {showNotifications && (
                <div
                  onClick={() => setShowNotifications(false)}
                  style={{ position: 'fixed', inset: 0, zIndex: 998 }}
                />
              )}

              {/* Notification panel */}
              {showNotifications && (
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 10px)',
                  right: 0,
                  width: '340px',
                  background: '#0c1220',
                  border: '1px solid var(--border-primary)',
                  borderRadius: '12px',
                  boxShadow: '0 16px 48px rgba(0,0,0,0.8)',
                  zIndex: 999,
                  overflow: 'hidden'
                }}>
                  {/* Header */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px 16px',
                    borderBottom: '1px solid var(--border-primary)',
                    background: 'rgba(6,182,212,0.05)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Bell size={14} style={{ color: 'var(--cyan)' }} />
                      <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)' }}>Intrusion System Logs</span>
                      <span style={{
                        background: 'var(--red)',
                        color: '#fff',
                        borderRadius: '10px',
                        padding: '1px 6px',
                        fontSize: '0.65rem',
                        fontWeight: 700
                      }}>{notifications.length}</span>
                    </div>
                    <button
                      onClick={() => setShowNotifications(false)}
                      style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px' }}
                    >
                      ✕ Fermer
                    </button>
                  </div>

                  {/* Notification items */}
                  <div style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {notifications.map((n, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: '10px 12px',
                          borderRadius: '8px',
                          background: 'rgba(255,255,255,0.03)',
                          borderLeft: `3px solid ${n.type === 'critical' ? 'var(--red)' : n.type === 'warning' ? 'var(--amber)' : 'var(--cyan)'}`,
                          cursor: 'default'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{
                            marginTop: '2px',
                            width: '7px',
                            height: '7px',
                            borderRadius: '50%',
                            flexShrink: 0,
                            background: n.type === 'critical' ? 'var(--red)' : n.type === 'warning' ? 'var(--amber)' : 'var(--cyan)'
                          }} />
                          <div>
                            <div style={{ color: 'var(--text-primary)', fontSize: '0.76rem', lineHeight: '1.4', marginBottom: '3px' }}>{n.text}</div>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>{n.time}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Footer */}
                  <div style={{ padding: '10px 16px', borderTop: '1px solid var(--border-primary)', textAlign: 'center' }}>
                    <button
                      onClick={() => { setActiveView('Security Events'); setShowNotifications(false); }}
                      style={{ background: 'none', border: 'none', color: 'var(--cyan)', fontSize: '0.72rem', cursor: 'pointer', fontWeight: 500 }}
                    >
                      Voir tous les logs →
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              borderLeft: '1px solid var(--border-primary)',
              paddingLeft: '20px'
            }}>
              <div style={{
                background: 'var(--bg-tertiary)',
                color: 'var(--cyan)',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 600,
                fontSize: '0.85rem',
                border: '1px solid rgba(6,182,212,0.3)'
              }}>
                R
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>rayane-vm</span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Admin SOC</span>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              title="Déconnexion"
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                color: 'var(--red)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '7px 12px',
                fontSize: '0.75rem',
                fontWeight: 600,
                transition: 'var(--transition-smooth)'
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(239, 68, 68, 0.2)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 0 10px rgba(239,68,68,0.2)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(239, 68, 68, 0.1)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = 'none';
              }}
            >
              <LogOut size={14} />
              Logout
            </button>

          </div>
        </header>

        {/* Viewport Content Area */}
        <main style={{ padding: '24px', flexGrow: 1, overflowY: 'auto' }}>
          {renderActiveView()}
        </main>

      </div>

    </div>
  );
};

export default App;
