interface ScanResultProps {
  result: string | null;
  loading: boolean;
  error: string | null;
}

export function ScanResult({ result, loading, error }: ScanResultProps) {
  if (loading) return <div className="card"><div className="loading">Scan de sécurité en cours (cela peut prendre plusieurs minutes)...</div></div>;
  if (error) return <div className="card error">{error}</div>;
  if (!result) return null;

  return (
    <div className="card">
      <h3>Résultats du scan de sécurité</h3>
      <pre className="code-block">{result}</pre>
    </div>
  );
}