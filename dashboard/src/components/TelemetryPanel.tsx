import { useEffect, useMemo, useState } from 'react';
import { api, type TraceEntry } from '../api';

function formatDuration(trace: TraceEntry) {
  if (typeof trace.duration_ms === 'number') return `${trace.duration_ms.toFixed(2)} ms`;
  if (typeof trace.duration_ns === 'number') return `${(trace.duration_ns / 1_000_000).toFixed(2)} ms`;
  if (typeof trace.duration === 'number') return `${(trace.duration / 1_000_000).toFixed(2)} ms`;
  return '-';
}

function formatTime(value?: string) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleTimeString();
}

function primaryAttribute(trace: TraceEntry) {
  const attrs = trace.attributes || {};
  return (
    attrs['file.path'] ||
    attrs['repo.target'] ||
    attrs['repo.path'] ||
    attrs['github.url'] ||
    attrs['http.route'] ||
    '-'
  );
}

export function TelemetryPanel() {
  const [traces, setTraces] = useState<TraceEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTraces = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.traces(100);
      setTraces(res.traces);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur chargement traces');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTraces();
  }, []);

  const stats = useMemo(() => {
    const durations = traces
      .map((trace) => trace.duration_ms ?? (trace.duration_ns ? trace.duration_ns / 1_000_000 : undefined))
      .filter((duration): duration is number => typeof duration === 'number');
    const total = durations.reduce((sum, duration) => sum + duration, 0);
    const slowest = traces.reduce<TraceEntry | null>((current, trace) => {
      const duration = trace.duration_ms ?? (trace.duration_ns ? trace.duration_ns / 1_000_000 : 0);
      const currentDuration = current?.duration_ms ?? (current?.duration_ns ? current.duration_ns / 1_000_000 : 0);
      return duration > currentDuration ? trace : current;
    }, null);

    return {
      count: traces.length,
      averageMs: durations.length ? total / durations.length : 0,
      slowest,
    };
  }, [traces]);

  return (
    <section className="section telemetry-section">
      <div className="telemetry-header">
        <div>
          <h2>Telemetry</h2>
          <p className="hint">Spans OpenTelemetry écrits dans <code>traces.jsonl</code>.</p>
        </div>
        <button className="secondary-btn" onClick={loadTraces} disabled={loading}>
          {loading ? 'Actualisation...' : 'Actualiser'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="telemetry-stats">
        <div className="telemetry-stat-card">
          <span className="telemetry-stat-label">Spans</span>
          <strong>{stats.count}</strong>
        </div>
        <div className="telemetry-stat-card">
          <span className="telemetry-stat-label">Durée moyenne</span>
          <strong>{stats.averageMs.toFixed(2)} ms</strong>
        </div>
        <div className="telemetry-stat-card">
          <span className="telemetry-stat-label">Plus lent</span>
          <strong>{stats.slowest?.name || '-'}</strong>
        </div>
      </div>

      <div className="telemetry-table-wrap">
        <table className="telemetry-table">
          <thead>
            <tr>
              <th>Span</th>
              <th>Durée</th>
              <th>Statut</th>
              <th>Contexte</th>
              <th>Heure</th>
            </tr>
          </thead>
          <tbody>
            {traces.map((trace, index) => (
              <tr key={`${trace.trace_id || trace.context || 'trace'}-${trace.span_id || index}`}>
                <td className="span-name">{trace.name}</td>
                <td>{formatDuration(trace)}</td>
                <td>
                  <span className={`status-pill ${trace.attributes?.status === 'error' ? 'status-error' : 'status-success'}`}>
                    {trace.attributes?.status || 'recorded'}
                  </span>
                </td>
                <td className="trace-context">{String(primaryAttribute(trace))}</td>
                <td>{formatTime(trace.started_at)}</td>
              </tr>
            ))}
            {!traces.length && !loading && (
              <tr>
                <td colSpan={5} className="empty-table">Aucune trace disponible.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
