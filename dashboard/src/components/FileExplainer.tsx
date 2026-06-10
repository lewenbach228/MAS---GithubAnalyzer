import ReactMarkdown from 'react-markdown';

interface FileExplainerProps {
  explanation: string | null;
  loading: boolean;
  error: string | null;
  tokens?: number;
}

export function FileExplainer({ explanation, loading, error, tokens }: FileExplainerProps) {
  if (loading) return <div className="card"><div className="loading">Analyse par IA en cours...</div></div>;
  if (error) return <div className="card error">{error}</div>;
  if (!explanation) return null;

  return (
    <div className="card explainer-card">
      <div className="explainer-header">
        <span>Analyse par IA</span>
        {tokens !== undefined && tokens > 0 && (
          <span className="explainer-meta">{tokens} tokens</span>
        )}
      </div>
      <div className="explainer-content">
        <ReactMarkdown
          components={{
            code({ className, children, ...props }) {
              const isBlock = className?.startsWith('language-');
              if (isBlock) {
                return (
                  <pre className="md-pre">
                    <code className={className} {...props}>{children}</code>
                  </pre>
                );
              }
              return <code className="md-inline-code" {...props}>{children}</code>;
            },
            pre({ children }) {
              return <pre className="md-pre">{children}</pre>;
            },
            ul({ children }) {
              return <ul className="md-ul">{children}</ul>;
            },
            ol({ children }) {
              return <ol className="md-ol">{children}</ol>;
            },
            li({ children }) {
              return <li className="md-li">{children}</li>;
            },
            p({ children }) {
              return <p className="md-p">{children}</p>;
            },
            h1({ children }) {
              return <h3 className="md-heading">{children}</h3>;
            },
            h2({ children }) {
              return <h4 className="md-heading">{children}</h4>;
            },
            h3({ children }) {
              return <h5 className="md-heading">{children}</h5>;
            },
            strong({ children }) {
              return <strong className="md-strong">{children}</strong>;
            },
          }}
        >
          {explanation}
        </ReactMarkdown>
      </div>
    </div>
  );
}