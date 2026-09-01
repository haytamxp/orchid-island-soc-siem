import React from 'react';
import type { SecurityEvent, Alert, Agent } from '../data/mockData';
import type { SocStats, TrafficPoint, DataSource } from '../hooks/useSocData';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { Shield, AlertTriangle, Cpu, Users, ArrowUpRight, TrendingUp } from 'lucide-react';

interface DashboardViewProps {
  events: SecurityEvent[];
  alerts: Alert[];
  agents: Agent[];
  stats: SocStats | null;
  traffic: TrafficPoint[];
  dataSource: DataSource;
  setView: (view: string) => void;
}

// Fallback traffic curve used when the backend has no hourly data yet.
const FALLBACK_TRAFFIC = [
  { time: '04:00', Allowed: 340, Blocked: 12 },
  { time: '06:00', Allowed: 450, Blocked: 24 },
  { time: '08:00', Allowed: 780, Blocked: 56 },
  { time: '10:00', Allowed: 950, Blocked: 89 },
  { time: '12:00', Allowed: 1100, Blocked: 120 },
  { time: '14:00', Allowed: 920, Blocked: 154 },
  { time: '15:00', Allowed: 1240, Blocked: 210 },
];

export const DashboardView: React.FC<DashboardViewProps> = ({ events, alerts, agents, stats, traffic, dataSource, setView }) => {
  // Prefer authoritative backend aggregates; fall back to what we can derive locally.
  const totalEvents = stats ? stats.total_events : events.length;
  const criticalAlerts = stats ? stats.critical_alerts : alerts.filter(a => a.severity === 'Critical').length;
  const onlineAgents = stats ? stats.agents_online : agents.filter(a => a.status === 'Online').length;
  const totalAgentsCount = stats ? stats.agents_online + stats.agents_offline : agents.length;

  // SIEM Server Resources (Based on VM rayane-virtual-machine)
  const rayaneVM = agents.find(a => a.name === 'rayane-virtual-machine') || { cpu_usage: 68, ram_usage: 74 };
  const cpuUsage = rayaneVM.cpu_usage;
  const ramUsage = rayaneVM.ram_usage;

  // Threat Index: use the backend value when present, otherwise a local heuristic.
  const heuristicThreatIndex = Math.min(100, 35 + (criticalAlerts * 15) + (alerts.filter(a => a.severity === 'High').length * 8));
  const rawThreatIndex = stats ? stats.threat_index : heuristicThreatIndex;
  // Backend may report the index on a 0–1 or 0–100 scale depending on seed data.
  const normalizedThreatIndex = rawThreatIndex > 0 && rawThreatIndex <= 1 ? rawThreatIndex * 100 : rawThreatIndex;
  const threatIndexValue = Math.round(Math.min(100, Math.max(0, normalizedThreatIndex)));

  // Data for Area Chart: Blocked vs Allowed per hour, from the backend when available.
  const trafficData = traffic.length > 0
    ? traffic.map(point => ({ time: point.hour, Allowed: point.allowed, Blocked: point.blocked }))
    : FALLBACK_TRAFFIC;

  // Data for Attack Vectors Pie Chart
  const pieData = [
    { name: 'SQL Injection', value: 35, color: '#ef4444' }, // Red
    { name: 'Brute Force SSH', value: 30, color: '#f59e0b' }, // Amber
    { name: 'Port Scan', value: 20, color: '#06b6d4' }, // Cyan
    { name: 'DDoS / Floods', value: 15, color: '#8b5cf6' }, // Purple
  ];

  // Helper for gauge colors
  const getThreatColor = (val: number) => {
    if (val < 40) return '#10b981'; // Emerald
    if (val < 75) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  const getThreatLabel = (val: number) => {
    if (val < 40) return 'Niveau Faible';
    if (val < 75) return 'Niveau Modéré';
    return 'Niveau Élevé';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {dataSource === 'mock' && (
        <div style={{
          padding: '8px 14px',
          borderRadius: '8px',
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          color: 'var(--amber)',
          fontSize: '0.75rem',
          fontWeight: 600,
        }}>
          Demo data — the SOC backend is unreachable, showing bundled sample datasets.
        </div>
      )}

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        
        {/* Total Events Card */}
        <div className="glass-panel" style={{ padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Total Security Events</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(6, 182, 212, 0.1)', color: 'var(--cyan)' }}>
              <Shield size={20} />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>{totalEvents.toLocaleString()}</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--emerald)', display: 'flex', alignItems: 'center', gap: '2px' }}>
              <TrendingUp size={12} /> +12.4%
            </span>
          </div>
          {/* Sparkline mini-SVG */}
          <div style={{ width: '100%', height: '30px', marginTop: '16px' }}>
            <svg width="100%" height="30" viewBox="0 0 100 30" preserveAspectRatio="none">
              <path d="M0,25 Q15,5 30,18 T60,8 T90,22 L100,10" fill="none" stroke="var(--cyan)" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* Critical Alerts Card */}
        <div className="glass-panel" style={{ padding: '20px', position: 'relative', overflow: 'hidden', borderLeft: '3px solid var(--red)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Critical Alerts</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--red)' }}>
              <AlertTriangle size={20} />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>{criticalAlerts}</span>
            <span className="pulse-red"></span>
            <span style={{ fontSize: '0.75rem', color: 'var(--red)', fontWeight: 500 }}>Action Requise</span>
          </div>
          {/* Sparkline mini-SVG */}
          <div style={{ width: '100%', height: '30px', marginTop: '16px' }}>
            <svg width="100%" height="30" viewBox="0 0 100 30" preserveAspectRatio="none">
              <path d="M0,20 L20,10 L40,25 L60,5 L80,18 L100,2" fill="none" stroke="var(--red)" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* Active Agents Card */}
        <div className="glass-panel" style={{ padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Active Agents</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--emerald)' }}>
              <Users size={20} />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>{onlineAgents}/{totalAgentsCount}</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Online</span>
          </div>
          {/* Sparkline mini-SVG */}
          <div style={{ width: '100%', height: '30px', marginTop: '16px' }}>
            <svg width="100%" height="30" viewBox="0 0 100 30" preserveAspectRatio="none">
              <path d="M0,15 L30,15 L50,15 L70,15 L100,15" fill="none" stroke="var(--emerald)" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* Server Resources Card */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>VM Resources</span>
            <Cpu size={16} style={{ color: 'var(--purple)' }} />
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>CPU Usage</span>
              <span style={{ fontWeight: 600 }}>{cpuUsage.toFixed(1)}%</span>
            </div>
            <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${cpuUsage}%`, background: 'var(--purple)', borderRadius: '3px', transition: 'width 1s ease-in-out' }}></div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>RAM Usage</span>
              <span style={{ fontWeight: 600 }}>{ramUsage.toFixed(1)}%</span>
            </div>
            <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${ramUsage}%`, background: 'var(--cyan)', borderRadius: '3px', transition: 'width 1s ease-in-out' }}></div>
            </div>
          </div>
        </div>

      </div>

      {/* Middle Visuals Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 1.25fr', gap: '20px', alignItems: 'stretch' }}>
        
        {/* Main Traffic Chart */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Traffic Analysis</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Allowed network actions vs intrusion blocks</p>
            </div>
            <div style={{ display: 'flex', gap: '12px', fontSize: '0.75rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--cyan)' }}></span> Allowed
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--red)' }}></span> Blocked
              </span>
            </div>
          </div>
          
          <div style={{ width: '100%', height: '280px', minHeight: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trafficData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAllowed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--cyan)" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="var(--cyan)" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--red)" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="var(--red)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                    border: '1px solid var(--border-primary)', 
                    borderRadius: '8px',
                    color: 'var(--text-primary)' 
                  }} 
                />
                <Area type="monotone" dataKey="Allowed" stroke="var(--cyan)" strokeWidth={2} fillOpacity={1} fill="url(#colorAllowed)" />
                <Area type="monotone" dataKey="Blocked" stroke="var(--red)" strokeWidth={2} fillOpacity={1} fill="url(#colorBlocked)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Gauge */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>Threat Index</h3>
          
          <div style={{ position: 'relative', width: '160px', height: '120px', overflow: 'hidden', display: 'flex', justifyContent: 'center' }}>
            <svg width="150" height="150" style={{ transform: 'rotate(-180deg)' }}>
              {/* Background semi-circle */}
              <circle
                cx="75"
                cy="75"
                r="60"
                fill="none"
                stroke="rgba(255,255,255,0.05)"
                strokeWidth="12"
                strokeDasharray="188.4"
                strokeDashoffset="0"
                strokeLinecap="round"
              />
              {/* Foreground colored arc */}
              <circle
                cx="75"
                cy="75"
                r="60"
                fill="none"
                stroke={getThreatColor(threatIndexValue)}
                strokeWidth="12"
                strokeDasharray="188.4"
                strokeDashoffset={188.4 - (188.4 * threatIndexValue) / 100}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
              />
            </svg>
            <div style={{ position: 'absolute', bottom: '0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={{ fontSize: '2rem', fontWeight: 800, color: getThreatColor(threatIndexValue) }}>
                {threatIndexValue}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 100</span>
            </div>
          </div>
          
          <div style={{ marginTop: '16px' }}>
            <span style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              color: '#ffffff',
              backgroundColor: getThreatColor(threatIndexValue) + '15',
              border: `1px solid ${getThreatColor(threatIndexValue)}30`,
              padding: '4px 12px',
              borderRadius: '20px'
            }}>
              {getThreatLabel(threatIndexValue)}
            </span>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
              Index dynamique basé sur l'activité réseau et les vulnérabilités actives.
            </p>
          </div>
        </div>

      </div>

      {/* Lower Row: Table & Pie Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        
        {/* Left Side: Recent Alerts */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Active Security Incidents</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Top severe alerts pending mitigation</p>
            </div>
            <button 
              onClick={() => setView('Alerts & AI Insights')}
              className="btn-secondary" 
              style={{ fontSize: '0.75rem', padding: '4px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              See All <ArrowUpRight size={12} />
            </button>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flexGrow: 1 }}>
            {alerts.slice(0, 5).map(alert => (
              <div 
                key={alert.id} 
                className="glass-panel" 
                style={{ 
                  padding: '12px', 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  background: 'rgba(255,255,255,0.01)',
                  borderLeft: `3px solid ${alert.severity === 'Critical' ? 'var(--red)' : alert.severity === 'High' ? 'var(--amber)' : 'var(--cyan)'}`
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxWidth: '75%' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{alert.title}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {alert.description}
                  </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    backgroundColor: alert.severity === 'Critical' ? 'rgba(239, 68, 68, 0.15)' : alert.severity === 'High' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                    color: alert.severity === 'Critical' ? 'var(--red)' : alert.severity === 'High' ? 'var(--amber)' : 'var(--cyan)'
                  }}>
                    {alert.severity}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Prob: {alert.xgboost_probability}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: Attack Vectors Pie */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '10px' }}>Vector Attack Distribution</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                    border: '1px solid var(--border-primary)', 
                    borderRadius: '8px',
                    color: 'var(--text-primary)' 
                  }} 
                />
                <Legend 
                  verticalAlign="bottom" 
                  align="center"
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: '11px', color: 'var(--text-secondary)' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="glass-panel" style={{ padding: '10px', marginTop: '10px', fontSize: '0.75rem', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.2)' }}>
            <strong>Indicateur SOC :</strong> Les tentatives d'injection SQL dominent ce cycle réseau. Assurez-vous que les pare-feu applicatifs (WAF) bloquent les signatures associées.
          </div>
        </div>

      </div>

    </div>
  );
};
