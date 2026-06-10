interface FileContentProps {
  content: string | null;
  language: string;
  lines: number;
  sizeKb: number;
  loading: boolean;
  error: string | null;
}

export function FileContent({ content, language, lines, sizeKb, loading, error }: FileContentProps) {
  if (loading) return <div className="card"><div className="loading">Chargement du fichier...</div></div>;
  if (error) return <div className="card error">{error}</div>;
  if (!content) return null;

  const lineNumbers = content.split('\n').map((_, i) => i + 1);

  return (
    <div className="card">
      <div className="file-meta">
        <span className="file-lang-badge">{language}</span>
        <span className="file-stat">{lines} lignes</span>
        <span className="file-stat">{sizeKb} KB</span>
      </div>
      <div className="file-content-wrapper">
        <div className="line-numbers">
          {lineNumbers.map((n) => (
            <span key={n} className="line-num">{n}</span>
          ))}
        </div>
        <pre className="file-content">{content}</pre>
      </div>
    </div>
  );
}