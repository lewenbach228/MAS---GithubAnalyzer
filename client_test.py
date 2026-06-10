import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client_test():
    print("[INIT] Demarrage du test client MCP avec URL GitHub réelle...")
    
    # Paramètres du serveur
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            repo_url = "https://github.com/lewenbach228/1WIN_AUTO_AVIATOR.git"
            target = "repo_analysis"
            
            # 1. (Clonage déjà fait manuellement)
            print("\n[STEP 1] Dépôt déjà cloné.")
            
            # 2. Lister les fichiers
            print("\n[STEP 2] Arborescence du dépôt :")
            list_res = await session.call_tool("list_repo_files", arguments={"directory_path": target})
            files = list_res.content[0].text
            print(files)
            
            # 3. Analyser un fichier clé (ex: main.py)
            # On cherche un fichier .py dans la liste
            py_files = [f for f in files.split('\n') if f.endswith('.py')]
            if py_files:
                # Priorité au main.py ou équivalent
                target_file = os.path.join(target, py_files[0])
                for f in py_files:
                    if "main" in f: target_file = os.path.join(target, f)
                
                print(f"\n[STEP 3] Analyse de structure sur : {target_file}")
                ana_res = await session.call_tool("analyze_code_structure", arguments={"file_path": target_file})
                print(ana_res.content[0].text)
            else:
                print("\n[WARN] Aucun fichier Python trouvé pour l'analyse AST.")

            # 4. Tester l'outil 'scan_vulnerabilities' sur le repo analysé
            print(f"\n[STEP 4] Scan de sécurité via Semgrep sur '{target}'...")
            scan_res = await session.call_tool("scan_vulnerabilities", arguments={"target_path": target})
            
            print("[INFO] Résultat du scan :")
            for text_content in scan_res.content:
                print(text_content.text)

    print("\n[SUCCESS] Analyse du dépôt réel terminée.")

if __name__ == "__main__":
    asyncio.run(run_client_test())
