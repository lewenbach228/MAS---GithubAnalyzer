import os
from mcp.server.fastmcp import FastMCP
from analyzer import get_code_structure
from scanner import scan_vulnerabilities as run_scan
from cloner import clone_repository
from tracer import tracer

# Initialiser le serveur FastMCP
mcp = FastMCP("GitHub Repository Analyzer")

@mcp.tool()
def list_repo_files(directory_path: str = ".") -> str:
    """
    Lister l'arborescence des fichiers du dépôt local spécifié.
    """
    with tracer.start_as_current_span("list_repo_files"):
        if not os.path.exists(directory_path):
            return f"Erreur : Le dossier '{directory_path}' n'existe pas."
        
        files_list = []
        for root, dirs, files in os.walk(directory_path):
            dirs[:] = [d for dirs[:] in [dirs] for d in dirs if not d.startswith('.') and d not in ('node_modules', 'venv', '__pycache__', 'dist', 'build')]
            
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), directory_path)
                files_list.append(rel_path)
        
        return "\n".join(sorted(files_list)) if files_list else "Vide."

@mcp.tool()
def read_repo_file(file_path: str) -> str:
    """
    Lire le contenu textuel complet d'un fichier du dépôt.
    """
    with tracer.start_as_current_span("read_repo_file"):
        if not os.path.exists(file_path):
            return f"Erreur : '{file_path}' inexistant."
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return f"--- Contenu de {file_path} ---\n{content}"
        except Exception as e:
            return f"Erreur : {str(e)}"

@mcp.tool()
def analyze_code_structure(file_path: str) -> str:
    """
    Analyse la structure d'un fichier Python (classes et fonctions) via AST.
    """
    with tracer.start_as_current_span("analyze_code_structure"):
        content = read_repo_file(file_path)
        if content.startswith("Erreur"): return content
        code = content.split("--- Contenu de", 1)[-1].split("\n", 1)[-1]
        return get_code_structure(code)

@mcp.tool()
def clone_repo(github_url: str, target_folder: str = "repo_analysis") -> str:
    """
    Clone un dépôt GitHub distant pour analyse.
    """
    with tracer.start_as_current_span("clone_repo"):
        return clone_repository(github_url, target_folder)

@mcp.tool()
def scan_vulnerabilities(target_path: str = ".") -> str:
    """
    Scanne le répertoire cible pour détecter des vulnérabilités via Semgrep.
    """
    with tracer.start_as_current_span("scan_vulnerabilities"):
        return run_scan(target_path)

if __name__ == "__main__":
    mcp.run()
