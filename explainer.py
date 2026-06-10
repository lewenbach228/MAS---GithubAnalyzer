import os
from openai import OpenAI

LANG_MAP = {
    '.py': 'Python', '.sql': 'SQL', '.js': 'JavaScript',
    '.ts': 'TypeScript', '.jsx': 'React JSX', '.tsx': 'React TypeScript',
    '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
    '.md': 'Markdown', '.html': 'HTML', '.css': 'CSS',
    '.toml': 'TOML', '.ini': 'INI', '.cfg': 'INI',
    '.txt': 'Text', '.sh': 'Shell', '.bash': 'Shell',
    '.bat': 'Batch', '.ps1': 'PowerShell',
    '.env': 'Environment', '.gitignore': 'Git config',
    '.dockerfile': 'Dockerfile', 'dockerfile': 'Dockerfile',
    '.xml': 'XML', '.svg': 'SVG', '.go': 'Go',
    '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
    '.java': 'Java', '.kt': 'Kotlin', '.swift': 'Swift',
    '.c': 'C', '.h': 'C Header', '.cpp': 'C++', '.hpp': 'C++ Header',
    '.cs': 'C#', '.r': 'R', '.lua': 'Lua',
    '.ex': 'Elixir', '.exs': 'Elixir',
}

MAX_CHARS = 8000


def explain_file(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"explanation": f"Erreur : '{file_path}' inexistant.", "language": "?", "tokens": 0}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    ext = os.path.splitext(file_path)[1].lower()
    language = LANG_MAP.get(ext, 'Code')
    lines = content.count('\n') + 1
    size_kb = len(content.encode('utf-8')) / 1024

    truncated = content[:MAX_CHARS]
    if len(content) > MAX_CHARS:
        truncated += f"\n\n[... fichier tronqué à {MAX_CHARS} caractères sur {len(content)}]"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "explanation": "_Clé API OpenAI non configurée. Définissez `OPENAI_API_KEY` dans l'environnement._",
            "language": language,
            "tokens": 0,
            "lines": lines,
            "size_kb": round(size_kb, 1),
        }

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un analyste de code expert. Explique ce que fait ce fichier, "
                        "ses structures clés, et les patterns importants. "
                        "Sois concis mais précis. Réponds en markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Fichier : {os.path.basename(file_path)}\n"
                        f"Langage : {language}\n"
                        f"Lignes : {lines}\n"
                        f"Taille : {size_kb:.1f} KB\n\n"
                        f"Contenu :\n```\n{truncated}\n```"
                    ),
                },
            ],
            max_tokens=600,
            temperature=0.3,
        )

        explanation = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0

        return {
            "explanation": explanation,
            "language": language,
            "tokens": tokens,
            "lines": lines,
            "size_kb": round(size_kb, 1),
        }
    except Exception as e:
        return {
            "explanation": f"Erreur API : {str(e)}",
            "language": language,
            "tokens": 0,
            "lines": lines,
            "size_kb": round(size_kb, 1),
        }
