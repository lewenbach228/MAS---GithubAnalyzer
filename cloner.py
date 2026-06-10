import subprocess
import os
import shutil

def clone_repository(github_url: str, target_folder: str = "repo_analysis") -> str:
    """
    Clone un dépôt GitHub distant dans un dossier local pour analyse.
    """
    if os.path.exists(target_folder):
        for root, dirs, files in os.walk(target_folder):
            for f in files:
                try:
                    os.chmod(os.path.join(root, f), 0o777)
                except:
                    pass
        shutil.rmtree(target_folder, ignore_errors=True)
        
    try:
        subprocess.run(["git", "clone", "--depth", "1", github_url, target_folder], check=True, capture_output=True)
        return f"Dépôt cloné avec succès dans : {target_folder}"
    except subprocess.CalledProcessError as e:
        return f"Erreur lors du clonage : {e.stderr.decode()}"
