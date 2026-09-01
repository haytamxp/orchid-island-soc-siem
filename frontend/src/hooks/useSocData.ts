import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

import { BACKEND_URL } from '../config';

import type {
  Agent,
  AiReport,
  Alert,
  SecurityEvent,
} from '../data/mockData';

import {
  initialAgents,
  initialAiReports,
  initialAlerts,
  initialEvents,
} from '../data/mockData';

/** Aggregate counters returned by `GET /api/dashboard/stats`. */
export interface SocStats {
  total_events: number;
  total_alerts: number;
  new_alerts: number;
  critical_alerts: number;
  agents_online: number;
  agents_offline: number;
  threat_index: number;
}

/** One hourly bucket returned by `GET /api/dashboard/traffic`. */
export interface TrafficPoint {
  hour: string;
  total: number;
  blocked: number;
  allowed: number;
}

export type DataSource = 'live' | 'mock';

export interface UseSocDataResult {
  loading: boolean;
  error: string | null;
  backendHealthy: boolean;
  dataSource: DataSource;
  stats: SocStats | null;
  traffic: TrafficPoint[];
  events: SecurityEvent[];
  alerts: Alert[];
  agents: Agent[];
  reports: AiReport[];
  refresh: () => Promise<void>;
}

/** `GET /api/events` is paginated and wraps its rows in an envelope. */
interface EventsResponse {
  total: number;
  page: number;
  data: SecurityEvent[];
}

const POLL_INTERVAL_MS = 15_000;

async function getJson<T>(
  path: string,
  signal: AbortSignal,
): Promise<T> {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    headers: { Accept: 'application/json' },
    signal,
  });

  if (!response.ok) {
    throw new Error(`${path} -> HTTP ${response.status}`);
  }

  return (await response.json()) as T;
}

function isAbortError(err: unknown): boolean {
  return (
    err instanceof DOMException && err.name === 'AbortError'
  );
}

/**
 * Central data source for the SOC dashboard.
 *
 * Fetches every backend collection in parallel, re-polls on an interval,
 * and transparently falls back to the bundled demo datasets when the
 * Flask API cannot be reached so the UI stays usable offline.
 */
export function useSocData(): UseSocDataResult {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [dataSource, setDataSource] = useState<DataSource>('mock');

  const [stats, setStats] = useState<SocStats | null>(null);
  const [traffic, setTraffic] = useState<TrafficPoint[]>([]);
  const [events, setEvents] = useState<SecurityEvent[]>(initialEvents);
  const [alerts, setAlerts] = useState<Alert[]>(initialAlerts);
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [reports, setReports] = useState<AiReport[]>(initialAiReports);

  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const { signal } = controller;

    try {
      const [
        statsRes,
        trafficRes,
        eventsRes,
        alertsRes,
        agentsRes,
        reportsRes,
      ] = await Promise.all([
        getJson<SocStats>('/api/dashboard/stats', signal),
        getJson<TrafficPoint[]>('/api/dashboard/traffic', signal),
        getJson<EventsResponse>('/api/events?per_page=200', signal),
        getJson<Alert[]>('/api/alerts', signal),
        getJson<Agent[]>('/api/agents', signal),
        getJson<AiReport[]>('/api/reports', signal),
      ]);

      setStats(statsRes);
      setTraffic(Array.isArray(trafficRes) ? trafficRes : []);
      setEvents(Array.isArray(eventsRes?.data) ? eventsRes.data : []);
      setAlerts(Array.isArray(alertsRes) ? alertsRes : []);
      setAgents(Array.isArray(agentsRes) ? agentsRes : []);
      setReports(Array.isArray(reportsRes) ? reportsRes : []);

      setBackendHealthy(true);
      setDataSource('live');
      setError(null);
    } catch (err) {
      if (signal.aborted || isAbortError(err)) {
        return;
      }

      // Backend unreachable — keep the app usable with bundled demo data.
      setBackendHealthy(false);
      setDataSource('mock');
      setStats(null);
      setTraffic([]);
      setEvents(initialEvents);
      setAlerts(initialAlerts);
      setAgents(initialAgents);
      setReports(initialAiReports);
      setError(
        `Backend unreachable at ${BACKEND_URL} — showing demo data (${
          err instanceof Error ? err.message : 'unknown error'
        }).`,
      );
    } finally {
      if (!signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void load();

    const timer = window.setInterval(() => {
      void load();
    }, POLL_INTERVAL_MS);

    return () => {
      window.clearInterval(timer);
      abortRef.current?.abort();
    };
  }, [load]);

  return {
    loading,
    error,
    backendHealthy,
    dataSource,
    stats,
    traffic,
    events,
    alerts,
    agents,
    reports,
    refresh: load,
  };
}
