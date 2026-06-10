import subprocess
import json
import sys

def scan_vulnerabilities(target_path: str = ".") -> str:
    """
    Scanne le répertoire cible pour détecter des vulnérabilités via Semgrep.
    """
    try:
        # Appel de semgrep en format JSON
        # On utilise une config 'auto' pour couvrir les standards de sécurité
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import semgrep.main; sys.argv=['semgrep', 'scan', '--json', '--config', 'auto', sys.argv[1]]; sys.exit(semgrep.main.main())",
                target_path
            ],
            capture_output=True,
            text=True
        )
        
        # Le code 1 signifie qu'il a trouvé des problèmes, 0 aucun
        if result.returncode not in [0, 1]:
            return f"Erreur Semgrep: {result.stderr}"
            
        data = json.loads(result.stdout)
        results = data.get("results", [])
        
        if not results:
            return "Aucune vulnérabilité trouvée."
            
        output = [f"Vulnerabilités trouvées : {len(results)}\n"]
        for res in results:
            check_id = res.get("check_id", "Unknown")
            message = res.get("extra", {}).get("message", "No message")
            path = res.get("path", "Unknown")
            line = res.get("start", {}).get("line", 0)
            output.append(f"- [{check_id}] {message} dans {path}:{line}")
            
        return "\n".join(output)
        
    except Exception as e:
        return f"Erreur lors du scan : {str(e)}"
