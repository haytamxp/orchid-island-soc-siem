import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type Dispatch,
  type SetStateAction,
} from 'react';

import type {
  FimBaseline,
  FimEvent,
  FimFilters,
  FimStats,
} from '../types/fim';

import {
  disableFimBaseline,
  enableFimBaseline,
  getFimBaselines,
  getFimEvents,
} from '../services/fim';

const POLL_INTERVAL_MS = 10_000;

function matchesSearch(
  event: FimEvent,
  search: string,
): boolean {
  const normalized =
    search.trim().toLowerCase();

  if (!normalized) {
    return true;
  }

  const values = [
    event.hostname,
    event.file_path,
    event.change_type,
    event.severity,
    event.actor ?? '',
    event.process_name ?? '',
    event.agent_id ?? '',
  ];

  return values.some((value) =>
    value.toLowerCase().includes(normalized),
  );
}

function calculateStats(
  events: FimEvent[],
): FimStats {
  return {
    total: events.length,
    critical: events.filter(
      (event) => event.severity === 'Critical',
    ).length,
    high: events.filter(
      (event) => event.severity === 'High',
    ).length,
    modified: events.filter(
      (event) => event.change_type === 'modified',
    ).length,
    deleted: events.filter(
      (event) => event.change_type === 'deleted',
    ).length,
    added: events.filter(
      (event) => event.change_type === 'added',
    ).length,
  };
}

export interface UseFimDataResult {
  events: FimEvent[];
  baselines: FimBaseline[];
  filteredEvents: FimEvent[];
  stats: FimStats;
  loading: boolean;
  backendHealthy: boolean;
  error: string | null;
  filters: FimFilters;
  setFilters: Dispatch<SetStateAction<FimFilters>>;
  refresh: () => Promise<void>;
  disableBaseline: (id: number) => Promise<void>;
  enableBaseline: (id: number) => Promise<void>;
}

export function useFimData(): UseFimDataResult {
  const [events, setEvents] = useState<FimEvent[]>([]);
  const [baselines, setBaselines] = useState<FimBaseline[]>([]);
  const [loading, setLoading] = useState(true);
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState<FimFilters>({
    hostname: '',
    severity: '',
    change_type: '',
    search: '',
  });

  const refresh = useCallback(async () => {
    setLoading(true);

    try {
      const [
        fetchedEvents,
        fetchedBaselines,
      ] = await Promise.all([
        getFimEvents({
          hostname: filters.hostname || undefined,
          severity: filters.severity || undefined,
          change_type: filters.change_type || undefined,
          limit: 200,
        }),
        getFimBaselines(
          filters.hostname || undefined,
          true,
        ),
      ]);

      setEvents(
        Array.isArray(fetchedEvents)
          ? fetchedEvents
          : [],
      );

      setBaselines(
        Array.isArray(fetchedBaselines)
          ? fetchedBaselines
          : [],
      );

      setBackendHealthy(true);
      setError(null);
    } catch (err) {
      setBackendHealthy(false);
      setEvents([]);
      setBaselines([]);

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to retrieve FIM data',
      );
    } finally {
      setLoading(false);
    }
  }, [
    filters.hostname,
    filters.severity,
    filters.change_type,
  ]);

  useEffect(() => {
    void refresh();

    const timer = window.setInterval(
      () => {
        void refresh();
      },
      POLL_INTERVAL_MS,
    );

    return () => {
      window.clearInterval(timer);
    };
  }, [refresh]);

  const filteredEvents = useMemo(
    () =>
      events.filter((event) =>
        matchesSearch(
          event,
          filters.search,
        ),
      ),
    [events, filters.search],
  );

  const stats = useMemo(
    () => calculateStats(filteredEvents),
    [filteredEvents],
  );

  const disableBaseline = useCallback(
    async (id: number) => {
      await disableFimBaseline(id);
      await refresh();
    },
    [refresh],
  );

  const enableBaseline = useCallback(
    async (id: number) => {
      await enableFimBaseline(id);
      await refresh();
    },
    [refresh],
  );

  return {
    events,
    baselines,
    filteredEvents,
    stats,
    loading,
    backendHealthy,
    error,
    filters,
    setFilters,
    refresh,
    disableBaseline,
    enableBaseline,
  };
}
