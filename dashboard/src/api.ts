const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface TraceEntry {
  name: string;
  trace_id?: string;
  span_id?: string;
  context?: number;
  attributes?: Record<string, string | number | boolean>;
  duration?: number;
  duration_ns?: number;
  duration_ms?: number;
  started_at?: string;
  ended_at?: string;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string; service: string }>('/health'),
  clone: (url: string, target_folder = 'repo_analysis') =>
    request<{ message: string }>('/clone', {
      method: 'POST',
      body: JSON.stringify({ url, target_folder }),
    }),
  listFiles: (path = '.') =>
    request<{ files: string[]; path: string }>(`/files?path=${encodeURIComponent(path)}`),
  readFile: (path: string) =>
    request<{ content: string; path: string }>(`/file?path=${encodeURIComponent(path)}`),
  analyze: (file_path: string) =>
    request<{ result: string; file_path: string }>('/analyze', {
      method: 'POST',
      body: JSON.stringify({ file_path }),
    }),
  scan: (target_path = '.') =>
    request<{ result: string; target_path: string }>('/scan', {
      method: 'POST',
      body: JSON.stringify({ target_path }),
    }),
  explain: (file_path: string) =>
    request<{ explanation: string; language: string; tokens: number; lines: number; size_kb: number }>('/explain', {
      method: 'POST',
      body: JSON.stringify({ file_path }),
    }),
  traces: (limit = 100) =>
    request<{ traces: TraceEntry[]; count: number }>(`/traces?limit=${limit}`),
};
