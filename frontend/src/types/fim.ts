export type FimChangeType =
  | 'added'
  | 'modified'
  | 'deleted';

export type FimSeverity =
  | 'Low'
  | 'Medium'
  | 'High'
  | 'Critical';

export interface FimEvent {
  id: number;
  hostname: string;
  timestamp: string;
  file_path: string;
  change_type: FimChangeType;
  old_hash: string | null;
  new_hash: string | null;
  old_size: number | null;
  new_size: number | null;
  severity: FimSeverity;
  actor: string | null;
  process_name: string | null;
  agent_id: string | null;
  details: string | null;
}

export interface FimBaseline {
  id: number;
  hostname: string;
  file_path: string;
  sha256: string;
  file_size: number;
  mode: string | null;
  owner_name: string | null;
  monitored: boolean;
  created_at: string;
  updated_at: string;
}

export interface FimFilters {
  hostname: string;
  severity: string;
  change_type: string;
  search: string;
}

export interface FimStats {
  total: number;
  critical: number;
  high: number;
  modified: number;
  deleted: number;
  added: number;
}