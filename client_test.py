import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client_test():
    print("[INIT] Demarrage du test client MCP...")
    
    # Configurer les parametres pour lancer le serveur local
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=None
    )
    
    print("[CONN] Connexion au serveur MCP...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialiser la session MCP
            print("[SYS] Initialisation de la session...")
            await session.initialize()
            
            # 1. Lister les outils disponibles
            print("\n[STEP 1] Recuperation des outils exposes par le serveur...")
            tools_response = await session.list_tools()
            tools = tools_response.tools
            
            print(f"[OK] {len(tools)} outil(s) trouve(s) :")
            for tool in tools:
                print(f"   - {tool.name} : {tool.description}")
                
            # 2. Tester l'outil 'list_repo_files'
            print("\n[STEP 2] Test de l'outil 'list_repo_files'...")
            # On liste le dossier courant '.'
            list_result = await session.call_tool("list_repo_files", arguments={"directory_path": "."})
            
            print("[INFO] Reponse du serveur :")
            # Le resultat est dans content, qui est une liste d'objets TextContent
            for text_content in list_result.content:
                print(text_content.text)
                
            # 3. Tester l'outil 'read_repo_file'
            print("\n[STEP 3] Test de l'outil 'read_repo_file' sur 'requirements.txt'...")
            read_result = await session.call_tool("read_repo_file", arguments={"file_path": "requirements.txt"})
            
            print("[INFO] Reponse du serveur :")
            for text_content in read_result.content:
                print(text_content.text)
                
    print("\n[SUCCESS] Test du Walking Skeleton MCP termine avec succes !")

if __name__ == "__main__":
    # Lancer l'execution asynchrone du client de test
    asyncio.run(run_client_test())
