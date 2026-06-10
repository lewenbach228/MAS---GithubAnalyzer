import { useState } from 'react';
import { api } from '../api';

interface RepoFormProps {
  onCloned: (target: string) => void;
}

export function RepoForm({ onCloned }: RepoFormProps) {
  const [url, setUrl] = useState('https://github.com/');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url || url === 'https://github.com/') return;

    setLoading(true);
    setError(null);
    try {
      const target = 'repo_analysis';
      await api.clone(url, target);
      onCloned(target);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="repo-form">
      <div className="input-group">
        <label htmlFor="repo-url">URL du dépôt GitHub</label>
        <input
          id="repo-url"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo.git"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Clonage...' : 'Cloner & Analyser'}
        </button>
      </div>
      {error && <div className="error">{error}</div>}
    </form>
  );
}