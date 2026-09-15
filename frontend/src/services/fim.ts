import { BACKEND_URL } from '../config';

import type {
  FimBaseline,
  FimEvent,
} from '../types/fim';

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(
    `${BACKEND_URL}${path}`,
    {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.headers ?? {}),
      },
    },
  );

  const contentType =
    response.headers.get('content-type') ?? '';

  let payload: unknown = null;

  if (contentType.includes('application/json')) {
    payload = await response.json();
  }

  if (!response.ok) {
    let message =
      `${path} -> HTTP ${response.status}`;

    if (
      payload &&
      typeof payload === 'object' &&
      'message' in payload &&
      typeof payload.message === 'string'
    ) {
      message = payload.message;
    }

    throw new Error(message);
  }

  return payload as T;
}

export async function getFimEvents(
  params: {
    hostname?: string;
    severity?: string;
    change_type?: string;
    limit?: number;
  } = {},
): Promise<FimEvent[]> {
  const searchParams = new URLSearchParams();

  if (params.hostname) {
    searchParams.set('hostname', params.hostname);
  }

  if (params.severity) {
    searchParams.set('severity', params.severity);
  }

  if (params.change_type) {
    searchParams.set('change_type', params.change_type);
  }

  searchParams.set(
    'limit',
    String(params.limit ?? 200),
  );

  return requestJson<FimEvent[]>(
    `/api/fim?${searchParams.toString()}`,
  );
}

export async function getFimBaselines(
  hostname?: string,
  includeDisabled = true,
): Promise<FimBaseline[]> {
  const searchParams = new URLSearchParams();

  if (hostname) {
    searchParams.set('hostname', hostname);
  }

  if (includeDisabled) {
    searchParams.set('include_disabled', 'true');
  }

  const query = searchParams.toString();

  return requestJson<FimBaseline[]>(
    `/api/fim/baselines${query ? `?${query}` : ''}`,
  );
}

export async function disableFimBaseline(
  id: number,
): Promise<void> {
  await requestJson(
    `/api/fim/baselines/${id}/disable`,
    {
      method: 'POST',
    },
  );
}

export async function enableFimBaseline(
  id: number,
): Promise<void> {
  await requestJson(
    `/api/fim/baselines/${id}/enable`,
    {
      method: 'POST',
    },
  );
}
