import { useState, useEffect, useMemo } from 'react';
import { api } from '../api';

interface FileTreeProps {
  target: string;
  onFileSelect: (fullPath: string) => void;
  selectedFile?: string;
}

interface TreeNode {
  name: string;
  type: 'file' | 'directory';
  fullPath: string;
  children: TreeNode[];
}

function buildTree(paths: string[], basePath: string): TreeNode[] {
  const stripBase = (p: string) => {
    if (p.startsWith(basePath + '/')) return p.slice(basePath.length + 1);
    if (p === basePath) return '';
    return p;
  };

  const root: TreeNode[] = [];

  for (const fullPath of paths) {
    const rel = stripBase(fullPath);
    if (!rel) continue;

    const parts = rel.split('/');
    let currentLevel = root;

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLast = i === parts.length - 1;
      const existing = currentLevel.find((n) => n.name === part);

      if (existing) {
        currentLevel = existing.children;
      } else {
        const nodeFullPath = isLast
          ? fullPath
          : basePath + '/' + parts.slice(0, i + 1).join('/');
        const node: TreeNode = {
          name: part,
          type: isLast ? 'file' : 'directory',
          fullPath: nodeFullPath,
          children: [],
        };
        currentLevel.push(node);
        currentLevel = node.children;
      }
    }
  }

  return root;
}

function FileIcon({ name, type }: { name: string; type: string }) {
  if (type === 'directory') return <span className="tree-icon tree-icon-dir">📁</span>;
  const ext = name.split('.').pop()?.toLowerCase();
  const icon =
    ext === 'py' ? '🐍' :
    ext === 'sql' ? '🗃️' :
    ext === 'json' ? '📋' :
    ext === 'md' ? '📝' :
    ext === 'yaml' || ext === 'yml' ? '⚙️' :
    ext === 'toml' ? '⚙️' :
    ext === 'txt' ? '📄' :
    ext === 'html' ? '🌐' :
    ext === 'css' ? '🎨' :
    ext === 'js' || ext === 'ts' ? '🟨' :
    '📄';
  return <span className="tree-icon">{icon}</span>;
}

function TreeNodeRow({
  node,
  depth,
  selectedFile,
  onFileSelect,
}: {
  node: TreeNode;
  depth: number;
  selectedFile?: string;
  onFileSelect: (path: string) => void;
}) {
  const [expanded, setExpanded] = useState(true);
  const isSelected = node.type === 'file' && node.fullPath === selectedFile;
  const canAnalyze = node.type === 'file' && node.name.endsWith('.py');

  if (node.type === 'directory') {
    return (
      <li>
        <button
          className="tree-dir"
          style={{ paddingLeft: `${8 + depth * 16}px` }}
          onClick={() => setExpanded(!expanded)}
        >
          <span className="tree-arrow">{expanded ? '▼' : '▶'}</span>
          <FileIcon name={node.name} type="directory" />
          <span className="tree-name">{node.name}/</span>
        </button>
        {expanded && node.children.length > 0 && (
          <ul className="tree-children">
            {node.children.map((child) => (
              <TreeNodeRow
                key={child.fullPath}
                node={child}
                depth={depth + 1}
                selectedFile={selectedFile}
                onFileSelect={onFileSelect}
              />
            ))}
          </ul>
        )}
      </li>
    );
  }

  return (
    <li>
      <button
        className={`tree-file ${isSelected ? 'selected' : ''}`}
        style={{ paddingLeft: `${8 + depth * 16}px` }}
        onClick={() => onFileSelect(node.fullPath)}
        title={canAnalyze ? 'Analyser avec AST' : `Afficher le contenu`}
      >
        <FileIcon name={node.name} type="file" />
        <span className="tree-name">{node.name}</span>
        {canAnalyze && <span className="tree-badge">AST</span>}
      </button>
    </li>
  );
}

export function FileTree({ target, onFileSelect, selectedFile }: FileTreeProps) {
  const [files, setFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadFiles = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.listFiles(target);
        setFiles(res.files);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur chargement');
      } finally {
        setLoading(false);
      }
    };
    loadFiles();
  }, [target]);

  const tree = useMemo(() => buildTree(files, target), [files, target]);

  if (loading) return <div className="loading">Chargement...</div>;
  if (error) return <div className="error">{error}</div>;
  if (tree.length === 0) return <div className="empty">Aucun fichier trouvé.</div>;

  return (
    <div className="file-tree">
      <ul className="tree-root">
        <li>
          <div className="tree-root-label">
            <span className="tree-icon">📂</span>
            <span className="tree-name">{target}/</span>
          </div>
          <ul className="tree-children">
            {tree.map((node) => (
              <TreeNodeRow
                key={node.fullPath}
                node={node}
                depth={1}
                selectedFile={selectedFile}
                onFileSelect={onFileSelect}
              />
            ))}
          </ul>
        </li>
      </ul>
    </div>
  );
}