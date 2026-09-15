import { BACKEND_URL } from '../config';

import type {
  FimBaseline,
  FimEvent,
} from '../types/fim';

async function getJson<T>(
  path: string,
): Promise<T> {
  const response = await fetch(
    `${BACKEND_URL}${path}`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `${path} -> HTTP ${response.status}`,
    );
  }

  return (await response.json()) as T;
}

export async function getFimEvents(
  params: {
    hostname?: string;
    severity?: string;
    change_type?: string;
    limit?: number;
  } = {},
): Promise<FimEvent[]> {
  const searchParams =
    new URLSearchParams();

  if (params.hostname) {
    searchParams.set(
      'hostname',
      params.hostname,
    );
  }

  if (params.severity) {
    searchParams.set(
      'severity',
      params.severity,
    );
  }

  if (params.change_type) {
    searchParams.set(
      'change_type',
      params.change_type,
    );
  }

  searchParams.set(
    'limit',
    String(params.limit ?? 200),
  );

  return getJson<FimEvent[]>(
    `/api/fim?${searchParams.toString()}`,
  );
}

export async function getFimBaselines(
  hostname?: string,
): Promise<FimBaseline[]> {
  const searchParams =
    new URLSearchParams();

  if (hostname) {
    searchParams.set(
      'hostname',
      hostname,
    );
  }

  const query =
    searchParams.toString();

  return getJson<FimBaseline[]>(
    `/api/fim/baselines${
      query ? `?${query}` : ''
    }`,
  );
}