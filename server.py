import os
from mcp.server.fastmcp import FastMCP

# Initialiser le serveur FastMCP
mcp = FastMCP("GitHub Repository Analyzer")

@mcp.tool()
def list_repo_files(directory_path: str = ".") -> str:
    """
    Lister l'arborescence des fichiers du dépôt local spécifié.
    Permet à l'agent de comprendre la structure globale du projet.
    """
    if not os.path.exists(directory_path):
        return f"Erreur : Le dossier '{directory_path}' n'existe pas."
    
    files_list = []
    for root, dirs, files in os.walk(directory_path):
        # Ignorer les dossiers cachés et les dépendances lourdes pour rester propre
        dirs[:] = [d for dirs[:] in [dirs] for d in dirs if not d.startswith('.') and d not in ('node_modules', 'venv', '__pycache__', 'dist', 'build')]
        
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), directory_path)
            files_list.append(rel_path)
            
    if not files_list:
        return "Le dossier est vide ou ne contient aucun fichier lisible."
        
    return "\n".join(sorted(files_list))

@mcp.tool()
def read_repo_file(file_path: str) -> str:
    """
    Lire le contenu textuel complet d'un fichier du dépôt.
    Indispensable pour l'analyse syntaxique fine du code.
    """
    if not os.path.exists(file_path):
        return f"Erreur : Le fichier '{file_path}' n'existe pas."
        
    if os.path.isdir(file_path):
        return f"Erreur : '{file_path}' est un dossier, pas un fichier."
        
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return f"--- Contenu de {file_path} ---\n{content}"
    except Exception as e:
        return f"Erreur de lecture du fichier : {str(e)}"

if __name__ == "__main__":
    # Lancer le serveur (par défaut FastMCP écoute sur stdio pour s'intégrer aux clients MCP)
    mcp.run()
