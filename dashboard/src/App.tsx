import { useState, useCallback, useMemo } from 'react';
import { RepoForm } from './components/RepoForm';
import { FileTree } from './components/FileTree';
import { FileContent } from './components/FileContent';
import { FileExplainer } from './components/FileExplainer';
import { AnalyzeResult } from './components/AnalyzeResult';
import { ScanResult } from './components/ScanResult';
import { TelemetryPanel } from './components/TelemetryPanel';
import { api } from './api';
import './App.css';

function App() {
  const [target, setTarget] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const displayPath = useMemo(() => {
    if (!selectedFile || !target) return null;
    if (selectedFile.startsWith(target + '/')) return selectedFile.slice(target.length + 1);
    return selectedFile;
  }, [selectedFile, target]);

  const [fileContent, setFileContent] = useState<string | null>(null);
  const [fileMeta, setFileMeta] = useState<{ language: string; lines: number; size_kb: number } | null>(null);
  const [fileLoading, setFileLoading] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);

  const [explanation, setExplanation] = useState<string | null>(null);
  const [explanationTokens, setExplanationTokens] = useState(0);
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [explanationError, setExplanationError] = useState<string | null>(null);

  const [analyzeResult, setAnalyzeResult] = useState<string | null>(null);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  const [scanResult, setScanResult] = useState<string | null>(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);

  const handleCloned = useCallback((t: string) => {
    setTarget(t);
    setSelectedFile(null);
    setAnalyzeResult(null);
    setScanResult(null);
    setAnalyzeError(null);
    setScanError(null);
    setFileContent(null);
    setExplanation(null);
    setFileError(null);
    setExplanationError(null);
  }, []);

  const handleFileSelect = async (filePath: string) => {
    setSelectedFile(filePath);
    setFileContent(null);
    setExplanation(null);
    setAnalyzeResult(null);
    setFileError(null);
    setExplanationError(null);
    setAnalyzeError(null);

    setFileLoading(true);
    setExplanationLoading(true);
    setAnalyzeLoading(true);

    const calls: Promise<void>[] = [];

    calls.push(
      api.readFile(filePath)
        .then((res) => {
          const ext = filePath.split('.').pop()?.toLowerCase() || '';
          const langMap: Record<string, string> = {
            py: 'Python', sql: 'SQL', js: 'JavaScript', ts: 'TypeScript',
            json: 'JSON', yaml: 'YAML', yml: 'YAML', md: 'Markdown',
            html: 'HTML', css: 'CSS', toml: 'TOML', sh: 'Shell',
          };
          setFileContent(res.content);
          setFileMeta({
            language: langMap[ext] || ext.toUpperCase(),
            lines: res.content.split('\n').length,
            size_kb: Math.round(new Blob([res.content]).size / 102.4) / 10,
          });
        })
        .catch((err) => setFileError(err.message))
        .finally(() => setFileLoading(false))
    );

    calls.push(
      api.explain(filePath)
        .then((res) => {
          setExplanation(res.explanation);
          setExplanationTokens(res.tokens);
        })
        .catch((err) => setExplanationError(err.message))
        .finally(() => setExplanationLoading(false))
    );

    if (filePath.endsWith('.py')) {
      calls.push(
        api.analyze(filePath)
          .then((res) => setAnalyzeResult(res.result))
          .catch((err) => setAnalyzeError(err.message))
          .finally(() => setAnalyzeLoading(false))
      );
    } else {
      setAnalyzeLoading(false);
    }

    await Promise.all(calls);
  };

  const handleScan = async () => {
    if (!target) return;
    setScanResult(null);
    setScanError(null);
    setScanLoading(true);

    try {
      const res = await api.scan(target);
      setScanResult(res.result);
    } catch (err) {
      setScanError(err instanceof Error ? err.message : 'Erreur scan sécurité');
    } finally {
      setScanLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>GitHub Repository Analyzer</h1>
        <p className="subtitle">Analyse AST + Scan de sécurité par dépôt GitHub</p>
      </header>

      <section className="section">
        <RepoForm onCloned={handleCloned} />
      </section>

      {target && (
        <>
          <section className="section split">
            <div className="panel-left">
              <h2>Fichiers du dépôt</h2>
              <FileTree
                target={target}
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile || undefined}
              />
            </div>
            <div className="panel-right">
              <h2>Analyse</h2>
              {selectedFile ? (
                <>
                  <p className="file-label">{displayPath}</p>
                  <FileContent
                    content={fileContent}
                    language={fileMeta?.language || ''}
                    lines={fileMeta?.lines || 0}
                    sizeKb={fileMeta?.size_kb || 0}
                    loading={fileLoading}
                    error={fileError}
                  />
                  <FileExplainer
                    explanation={explanation}
                    loading={explanationLoading}
                    error={explanationError}
                    tokens={explanationTokens}
                  />
                  {selectedFile.endsWith('.py') && (
                    <AnalyzeResult
                      result={analyzeResult}
                      loading={analyzeLoading}
                      error={analyzeError}
                    />
                  )}
                </>
              ) : (
                <p className="hint">Sélectionnez un fichier dans l'arborescence.</p>
              )}
            </div>
          </section>

          <section className="section">
            <h2>Scan de sécurité</h2>
            <p className="hint">Analyse le dépôt entier avec Semgrep pour détecter des vulnérabilités.</p>
            <button
              className="scan-btn"
              onClick={handleScan}
              disabled={scanLoading}
            >
              {scanLoading ? 'Scan en cours...' : 'Lancer le scan Semgrep'}
            </button>
            <ScanResult
              result={scanResult}
              loading={scanLoading}
              error={scanError}
            />
          </section>

          <TelemetryPanel />
        </>
      )}
    </div>
  );
}

export default App;
