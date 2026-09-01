import React, {
  useMemo,
  useState,
} from 'react';

import { useSocData } from './hooks/useSocData';

import {
  getAuthSession,
  clearAuthSession,
} from './services/auth';

import type {
  UserRole,
} from './types/rbac';

import { hasPermission } from './types/rbac';

import { AdminLogin } from './components/AdminLogin';
import { RoleBadge } from './components/RoleBadge';
import { AccessDenied } from './components/AccessDenied';

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
  LogOut,
  Database,
  Users,
} from 'lucide-react';

const TIME_OPTIONS = [
  {
    value: 'Live',
    label: '🔴 Live Feed',
  },
  {
    value: 'Last 24h',
    label: '⏱ Dernières 24h',
  },
  {
    value: 'Last 7 days',
    label: '📅 7 derniers jours',
  },
  {
    value: 'Custom',
    label: '✏️ Personnalisé',
  },
];

function filterByTimeRange<
  T extends { timestamp: string },
>(
  items: T[],
  timeRange: string,
): T[] {
  if (timeRange === 'Live') {
    return items;
  }

  const now = new Date();
  const limit = new Date(now);

  if (timeRange === 'Last 24h') {
    limit.setHours(
      limit.getHours() - 24,
    );
  } else if (
    timeRange === 'Last 7 days'
  ) {
    limit.setDate(
      limit.getDate() - 7,
    );
  } else if (timeRange === 'Custom') {
    limit.setDate(
      limit.getDate() - 3,
    );
  }

  return items.filter((item) => {
    if (!item.timestamp) {
      return false;
    }

    const normalized =
      item.timestamp.includes('T')
        ? item.timestamp
        : item.timestamp.replace(
            ' ',
            'T',
          );

    const date =
      new Date(normalized);

    return (
      !Number.isNaN(
        date.getTime(),
      ) &&
      date >= limit
    );
  });
}

export const App: React.FC = () => {
  const initialSession =
    getAuthSession();

  const [
    session,
    setSession,
  ] = useState(initialSession);

  const [
    activeView,
    setActiveView,
  ] = useState('Dashboard');

  const [
    isSidebarCollapsed,
    setIsSidebarCollapsed,
  ] = useState(false);

  const [
    timeRange,
    setTimeRange,
  ] = useState('Last 24h');

  const [
    showNotifications,
    setShowNotifications,
  ] = useState(false);

  const [
    showTimeDropdown,
    setShowTimeDropdown,
  ] = useState(false);

  const {
    error,
    backendHealthy,
    dataSource,
    stats,
    traffic,
    events,
    alerts,
    agents,
    reports,
    refresh,
  } = useSocData();

  const role: UserRole =
    session?.role ?? 'employee';

  const isAuthenticated =
    Boolean(session);

  const newAlertCount =
    alerts.filter(
      (alert) =>
        alert.status === 'New',
    ).length;

  const notifications = useMemo(
    () =>
      alerts
        .slice(0, 5)
        .map((alert) => ({
          id: alert.id,
          text: alert.title,
          time: alert.timestamp,
          severity:
            alert.severity,
        })),
    [alerts],
  );

  const filteredEvents =
    useMemo(
      () =>
        filterByTimeRange(
          events,
          timeRange,
        ),
      [events, timeRange],
    );

  const filteredAlerts =
    useMemo(
      () =>
        filterByTimeRange(
          alerts,
          timeRange,
        ),
      [alerts, timeRange],
    );

  const handleLoginSuccess = () => {
    const authenticatedSession =
      getAuthSession();

    setSession(
      authenticatedSession,
    );

    void refresh();
  };

  const handleLogout = () => {
    clearAuthSession();
    setSession(null);
    setActiveView('Dashboard');
  };

  const navigationItems = [
    {
      name: 'Dashboard',
      icon: (
        <LayoutDashboard
          size={18}
        />
      ),
      permission:
        'dashboard.view' as const,
    },
    {
      name: 'Security Events',
      icon: (
        <Globe size={18} />
      ),
      permission:
        'events.view' as const,
    },
    {
      name: 'Alerts & AI Insights',
      icon: (
        <BrainCircuit
          size={18}
        />
      ),
      permission:
        'alerts.view' as const,
      badge: newAlertCount,
    },
    {
      name: 'Wazuh Agents',
      icon: (
        <Laptop size={18} />
      ),
      permission:
        'agents.view' as const,
    },
    {
      name: 'Suricata IDS',
      icon: (
        <Network size={18} />
      ),
      permission:
        'events.view' as const,
    },
    {
      name: 'File Integrity (FIM)',
      icon: (
        <FileCode
          size={18}
        />
      ),
      permission:
        'events.view' as const,
    },
    {
      name: 'Vulnerability Detection',
      icon: (
        <ShieldAlert
          size={18}
        />
      ),
      permission:
        'agents.view' as const,
    },
    {
      name: 'VirusTotal Scan',
      icon: (
        <Search size={18} />
      ),
      permission:
        'threat_intel.view' as const,
    },
    {
      name: 'Threat Intelligence',
      icon: (
        <Target size={18} />
      ),
      permission:
        'threat_intel.view' as const,
    },
    {
      name: 'Reports & Configurations',
      icon: (
        <Settings
          size={18}
        />
      ),
      permission:
        'reports.view' as const,
    },
    {
      name: 'Administration',
      icon: (
        <Users size={18} />
      ),
      permission:
        'administration.view' as const,
    },
  ];

  const visibleNavigation =
    navigationItems.filter(
      (item) =>
        hasPermission(
          role,
          item.permission,
        ),
    );

  const renderActiveView = () => {
    const activeNavigation =
      visibleNavigation.find(
        (item) =>
          item.name ===
          activeView,
      );

    if (
      !activeNavigation
    ) {
      return (
        <AccessDenied />
      );
    }

    switch (activeView) {
      case 'Dashboard':
        return (
          <DashboardView
            events={
              filteredEvents
            }
            alerts={
              filteredAlerts
            }
            agents={
              agents
            }
            stats={
              stats
            }
            traffic={
              traffic
            }
            dataSource={
              dataSource
            }
            setView={
              setActiveView
            }
          />
        );

      case 'Security Events':
        return (
          <EventsView
            events={
              filteredEvents
            }
          />
        );

      case 'Alerts & AI Insights':
        return (
          <AlertsView
            alerts={
              filteredAlerts
            }
            aiReports={
              reports
            }
            setAlerts={() =>
              undefined
            }
            setAiReports={() =>
              undefined
            }
          />
        );

      case 'Wazuh Agents':
        return (
          <AgentsView
            agents={
              agents
            }
            setAgents={() =>
              undefined
            }
          />
        );

      case 'Suricata IDS':
        return (
          <SuricataView
            events={
              filteredEvents
            }
          />
        );

      case 'File Integrity (FIM)':
        return (
          <FimView
            fimEvents={
              []
            }
          />
        );

      case 'Vulnerability Detection':
        return (
          <VulnerabilitiesView
            vulnerabilities={
              []
            }
            setVulnerabilities={() =>
              undefined
            }
          />
        );

      case 'VirusTotal Scan':
        return (
          <VirusTotalView />
        );

      case 'Threat Intelligence':
        return (
          <ThreatIntelView
            iocs={[]}
            setIocs={() =>
              undefined
            }
          />
        );

      case 'Reports & Configurations':
        return (
          <ReportsConfigView />
        );

      case 'Administration':
        return (
          <div
            className="glass-panel"
            style={{
              padding:
                '24px',
            }}
          >
            <div
              style={{
                display:
                  'flex',
                alignItems:
                  'center',
                gap: '10px',
                marginBottom:
                  '8px',
              }}
            >
              <Users
                size={20}
                style={{
                  color:
                    'var(--cyan)',
                }}
              />

              <h2
                style={{
                  margin: 0,
                  fontSize:
                    '1.1rem',
                }}
              >
                Administration
              </h2>

              <RoleBadge
                role={
                  role
                }
              />
            </div>

            <p
              style={{
                color:
                  'var(--text-secondary)',
                fontSize:
                  '0.75rem',
                lineHeight: 1.5,
              }}
            >
              User and role
              administration
              will be
              implemented in the
              next security
              batch.
            </p>
          </div>
        );

      default:
        return (
          <DashboardView
            events={
              filteredEvents
            }
            alerts={
              filteredAlerts
            }
            agents={
              agents
            }
            stats={
              stats
            }
            traffic={
              traffic
            }
            dataSource={
              dataSource
            }
            setView={
              setActiveView
            }
          />
        );
    }
  };

  if (
    !isAuthenticated
  ) {
    return (
      <AdminLogin
        onLoginSuccess={
          handleLoginSuccess
        }
      />
    );
  }

  return (
    <div
      style={{
        display:
          'flex',
        minHeight:
          '100vh',
        background:
          'var(--bg-primary)',
      }}
    >
      <aside
        className="glass-panel"
        style={{
          width:
            isSidebarCollapsed
              ? '72px'
              : '260px',
          minWidth:
            isSidebarCollapsed
              ? '72px'
              : '260px',
          borderRight:
            '1px solid var(--border-primary)',
          borderRadius: 0,
          display:
            'flex',
          flexDirection:
            'column',
          position:
            'sticky',
          top: 0,
          height:
            '100vh',
          zIndex: 100,
          boxShadow:
            '4px 0 30px rgba(0,0,0,0.5)',
        }}
      >
        <div
          style={{
            height:
              '70px',
            padding:
              '20px 16px',
            borderBottom:
              '1px solid var(--border-primary)',
            display:
              'flex',
            alignItems:
              'center',
            justifyContent:
              isSidebarCollapsed
                ? 'center'
                : 'space-between',
          }}
        >
          {!isSidebarCollapsed && (
            <div
              style={{
                display:
                  'flex',
                alignItems:
                  'center',
                gap: '8px',
              }}
            >
              <BrainCircuit
                size={20}
                style={{
                  color:
                    'var(--cyan)',
                }}
              />

              <span
                style={{
                  fontWeight:
                    800,
                  fontSize:
                    '1rem',
                }}
              >
                ORCHID
                <span
                  style={{
                    color:
                      'var(--cyan)',
                  }}
                >
                  SOC
                </span>
              </span>
            </div>
          )}

          {isSidebarCollapsed && (
            <BrainCircuit
              size={24}
              style={{
                color:
                  'var(--cyan)',
              }}
            />
          )}

          <button
            onClick={() =>
              setIsSidebarCollapsed(
                (value) =>
                  !value,
              )
            }
            style={{
              background:
                'none',
              border:
                'none',
              color:
                'var(--text-secondary)',
              cursor:
                'pointer',
            }}
          >
            {isSidebarCollapsed ? (
              <ChevronRight
                size={18}
              />
            ) : (
              <ChevronLeft
                size={18}
              />
            )}
          </button>
        </div>

        <nav
          style={{
            padding:
              '16px 8px',
            display:
              'flex',
            flexDirection:
              'column',
            gap: '5px',
            flexGrow: 1,
            overflowY:
              'auto',
          }}
        >
          {visibleNavigation.map(
            (item) => {
              const active =
                activeView ===
                item.name;

              return (
                <button
                  key={
                    item.name
                  }
                  onClick={() =>
                    setActiveView(
                      item.name,
                    )
                  }
                  title={
                    item.name
                  }
                  style={{
                    width:
                      '100%',
                    display:
                      'flex',
                    alignItems:
                      'center',
                    gap: '11px',
                    padding:
                      '11px 13px',
                    borderRadius:
                      '8px',
                    border:
                      'none',
                    borderLeft:
                      active
                        ? '3px solid var(--cyan)'
                        : '3px solid transparent',
                    cursor:
                      'pointer',
                    textAlign:
                      'left',
                    background:
                      active
                        ? 'rgba(6,182,212,0.1)'
                        : 'transparent',
                    color:
                      active
                        ? '#fff'
                        : 'var(--text-secondary)',
                    justifyContent:
                      isSidebarCollapsed
                        ? 'center'
                        : 'flex-start',
                  }}
                >
                  {item.icon}

                  {!isSidebarCollapsed && (
                    <span
                      style={{
                        flexGrow:
                          1,
                        fontSize:
                          '0.78rem',
                        fontWeight:
                          active
                            ? 600
                            : 500,
                      }}
                    >
                      {
                        item.name
                      }
                    </span>
                  )}

                  {!isSidebarCollapsed &&
                    item.badge &&
                    item.badge >
                      0 && (
                      <span
                        style={{
                          background:
                            'var(--red)',
                          color:
                            '#fff',
                          borderRadius:
                            '10px',
                          padding:
                            '2px 6px',
                          fontSize:
                            '0.58rem',
                          fontWeight:
                            800,
                        }}
                      >
                        {
                          item.badge
                        }
                      </span>
                    )}
                </button>
              );
            },
          )}
        </nav>

        <div
          style={{
            padding:
              '12px',
            borderTop:
              '1px solid var(--border-primary)',
          }}
        >
          {!isSidebarCollapsed && (
            <>
              <div
                style={{
                  display:
                    'flex',
                  alignItems:
                    'center',
                  gap: '7px',
                  fontSize:
                    '0.65rem',
                }}
              >
                <span
                  className={
                    backendHealthy
                      ? 'pulse-green'
                      : 'pulse-red'
                  }
                />

                <span>
                  API:{' '}
                  {backendHealthy
                    ? 'Healthy'
                    : 'Degraded'}
                </span>
              </div>

              <div
                style={{
                  display:
                    'flex',
                  alignItems:
                    'center',
                  gap: '6px',
                  marginTop:
                    '7px',
                  fontSize:
                    '0.62rem',
                  color:
                    'var(--text-muted)',
                }}
              >
                <Database
                  size={11}
                />

                Data:{' '}
                {dataSource.toUpperCase()}
              </div>
            </>
          )}
        </div>
      </aside>

      <div
        style={{
          flexGrow:
            1,
          minWidth: 0,
          display:
            'flex',
          flexDirection:
            'column',
        }}
      >
        <header
          style={{
            height:
              '70px',
            borderBottom:
              '1px solid var(--border-primary)',
            display:
              'flex',
            alignItems:
              'center',
            justifyContent:
              'space-between',
            padding:
              '0 22px',
            position:
              'sticky',
            top: 0,
            zIndex: 90,
            background:
              'rgba(15,23,42,0.35)',
            backdropFilter:
              'blur(8px)',
          }}
        >
          <div>
            <h1
              style={{
                margin: 0,
                fontSize:
                  '1.15rem',
              }}
            >
              {
                activeView
              }
            </h1>

            {error && (
              <div
                style={{
                  marginTop:
                    '3px',
                  fontSize:
                    '0.62rem',
                  color:
                    'var(--amber)',
                }}
              >
                {error}
              </div>
            )}
          </div>

          <div
            style={{
              display:
                'flex',
              alignItems:
                'center',
              gap: '14px',
            }}
          >
            <div
              style={{
                position:
                  'relative',
              }}
            >
              <button
                onClick={() =>
                  setShowTimeDropdown(
                    (value) =>
                      !value,
                  )
                }
                style={{
                  display:
                    'flex',
                  alignItems:
                    'center',
                  gap: '7px',
                  padding:
                    '7px 10px',
                  borderRadius:
                    '7px',
                  border:
                    '1px solid var(--border-primary)',
                  background:
                    'rgba(15,23,42,0.7)',
                  color:
                    'var(--text-primary)',
                  cursor:
                    'pointer',
                  fontSize:
                    '0.68rem',
                }}
              >
                <Clock size={12} />

                {
                  TIME_OPTIONS.find(
                    (option) =>
                      option.value ===
                      timeRange,
                  )?.label
                }
              </button>

              {showTimeDropdown && (
                <div
                  style={{
                    position:
                      'absolute',
                    right: 0,
                    top:
                      'calc(100% + 6px)',
                    width:
                      '180px',
                    background:
                      '#0f1729',
                    border:
                      '1px solid var(--border-primary)',
                    borderRadius:
                      '8px',
                    overflow:
                      'hidden',
                    zIndex: 200,
                  }}
                >
                  {TIME_OPTIONS.map(
                    (option) => (
                      <button
                        key={
                          option.value
                        }
                        onClick={() => {
                          setTimeRange(
                            option.value,
                          );
                          setShowTimeDropdown(
                            false,
                          );
                        }}
                        style={{
                          width:
                            '100%',
                          padding:
                            '9px 12px',
                          textAlign:
                            'left',
                          border:
                            'none',
                          background:
                            timeRange ===
                            option.value
                              ? 'rgba(6,182,212,0.1)'
                              : 'transparent',
                          color:
                            'var(--text-primary)',
                          cursor:
                            'pointer',
                          fontSize:
                            '0.68rem',
                        }}
                      >
                        {
                          option.label
                        }
                      </button>
                    ),
                  )}
                </div>
              )}
            </div>

            <div
              style={{
                position:
                  'relative',
              }}
            >
              <button
                onClick={() =>
                  setShowNotifications(
                    (value) =>
                      !value,
                  )
                }
                style={{
                  background:
                    'none',
                  border:
                    'none',
                  color:
                    'var(--text-secondary)',
                  cursor:
                    'pointer',
                  position:
                    'relative',
                }}
              >
                <Bell size={18} />

                {newAlertCount >
                  0 && (
                  <span
                    style={{
                      position:
                        'absolute',
                      top:
                        '-3px',
                      right:
                        '-4px',
                      minWidth:
                        '14px',
                      height:
                        '14px',
                      borderRadius:
                        '50%',
                      background:
                        'var(--red)',
                      color:
                        '#fff',
                      fontSize:
                        '8px',
                      fontWeight:
                        800,
                      display:
                        'flex',
                      alignItems:
                        'center',
                      justifyContent:
                        'center',
                    }}
                  >
                    {
                      newAlertCount
                    }
                  </span>
                )}
              </button>

              {showNotifications && (
                <div
                  style={{
                    position:
                      'absolute',
                    right: 0,
                    top:
                      'calc(100% + 10px)',
                    width:
                      '330px',
                    background:
                      '#0c1220',
                    border:
                      '1px solid var(--border-primary)',
                    borderRadius:
                      '10px',
                    zIndex: 200,
                    boxShadow:
                      '0 16px 48px rgba(0,0,0,0.8)',
                  }}
                >
                  <div
                    style={{
                      padding:
                        '11px 14px',
                      borderBottom:
                        '1px solid var(--border-primary)',
                      fontWeight:
                        700,
                      fontSize:
                        '0.76rem',
                    }}
                  >
                    Security Notifications
                  </div>

                  <div
                    style={{
                      padding:
                        '8px',
                      maxHeight:
                        '300px',
                      overflowY:
                        'auto',
                    }}
                  >
                    {notifications.length ===
                    0 ? (
                      <div
                        style={{
                          padding:
                            '20px',
                          color:
                            'var(--text-muted)',
                          textAlign:
                            'center',
                          fontSize:
                            '0.7rem',
                        }}
                      >
                        No active
                        notifications.
                      </div>
                    ) : (
                      notifications.map(
                        (
                          notification,
                        ) => (
                          <button
                            key={
                              notification.id
                            }
                            onClick={() => {
                              setActiveView(
                                'Alerts & AI Insights',
                              );
                              setShowNotifications(
                                false,
                              );
                            }}
                            style={{
                              width:
                                '100%',
                              textAlign:
                                'left',
                              padding:
                                '9px',
                              border:
                                'none',
                              borderLeft:
                                `3px solid ${
                                  notification.severity ===
                                  'Critical'
                                    ? 'var(--red)'
                                    : 'var(--amber)'
                                }`,
                              background:
                                'rgba(255,255,255,0.025)',
                              color:
                                'var(--text-primary)',
                              cursor:
                                'pointer',
                              marginBottom:
                                '5px',
                            }}
                          >
                            <div
                              style={{
                                fontSize:
                                  '0.7rem',
                                fontWeight:
                                  600,
                              }}
                            >
                              {
                                notification.text
                              }
                            </div>

                            <div
                              style={{
                                marginTop:
                                  '3px',
                                fontSize:
                                  '0.58rem',
                                color:
                                  'var(--text-muted)',
                              }}
                            >
                              {
                                notification.time
                              }
                            </div>
                          </button>
                        ),
                      )
                    )}
                  </div>
                </div>
              )}
            </div>

            <div
              style={{
                display:
                  'flex',
                alignItems:
                  'center',
                gap: '9px',
                borderLeft:
                  '1px solid var(--border-primary)',
                paddingLeft:
                  '14px',
              }}
            >
              <div
                style={{
                  width:
                    '31px',
                  height:
                    '31px',
                  borderRadius:
                    '50%',
                  background:
                    'var(--bg-tertiary)',
                  border:
                    '1px solid rgba(6,182,212,0.3)',
                  display:
                    'flex',
                  alignItems:
                    'center',
                  justifyContent:
                    'center',
                  color:
                    'var(--cyan)',
                  fontWeight:
                    700,
                  fontSize:
                    '0.75rem',
                }}
              >
                {(
                  session?.username ??
                  'U'
                )
                  .charAt(0)
                  .toUpperCase()}
              </div>

              <div
                style={{
                  display:
                    'flex',
                  flexDirection:
                    'column',
                  gap: '3px',
                }}
              >
                <span
                  style={{
                    fontSize:
                      '0.72rem',
                    fontWeight:
                      600,
                  }}
                >
                  {
                    session?.username ??
                    'Unknown'
                  }
                </span>

                <RoleBadge
                  role={
                    role
                  }
                  compact
                />
              </div>
            </div>

            <button
              onClick={
                handleLogout
              }
              style={{
                display:
                  'flex',
                alignItems:
                  'center',
                gap: '5px',
                padding:
                  '7px 9px',
                borderRadius:
                  '7px',
                border:
                  '1px solid rgba(239,68,68,0.3)',
                background:
                  'rgba(239,68,68,0.08)',
                color:
                  'var(--red)',
                cursor:
                  'pointer',
                fontSize:
                  '0.65rem',
              }}
            >
              <LogOut size={13} />
              Logout
            </button>
          </div>
        </header>

        <main
          style={{
            padding:
              '22px',
            flexGrow:
              1,
            overflowY:
              'auto',
          }}
        >
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
};

export default App;
