interface AnalyzeResultProps {
  result: string | null;
  loading: boolean;
  error: string | null;
}

export function AnalyzeResult({ result, loading, error }: AnalyzeResultProps) {
  if (loading) return <div className="card"><div className="loading">Analyse AST en cours...</div></div>;
  if (error) return <div className="card error">{error}</div>;
  if (!result) return null;

  return (
    <div className="card">
      <h3>Analyse AST</h3>
      <pre className="code-block">{result}</pre>
    </div>
  );
}