import os
import sys
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import get_code_structure
from scanner import scan_vulnerabilities as run_scan
from cloner import clone_repository
from explainer import explain_file
from tracer import tracer

app = FastAPI(title="GitHub Repository Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CloneRequest(BaseModel):
    url: str
    target_folder: str = "repo_analysis"


class AnalyzeRequest(BaseModel):
    file_path: str


class ScanRequest(BaseModel):
    target_path: str = "."


class ExplainRequest(BaseModel):
    file_path: str


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "github-analyzer-api"


TRACES_FILE = "traces.jsonl"


def list_files(directory_path: str = ".") -> list[str]:
    if not os.path.exists(directory_path):
        raise HTTPException(status_code=404, detail=f"Le dossier '{directory_path}' n'existe pas.")

    files_list = []
    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'venv', '__pycache__', 'dist', 'build')]

        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), directory_path)
            full_rel_path = os.path.join(directory_path, rel_path).replace('\\', '/')
            files_list.append(full_rel_path)

    return sorted(files_list)


def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"'{file_path}' inexistant.")

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/api/clone")
async def clone_repo(req: CloneRequest):
    with tracer.start_as_current_span("api.clone_repo") as span:
        span.set_attribute("http.route", "/api/clone")
        span.set_attribute("github.url", req.url)
        span.set_attribute("repo.target", req.target_folder)
        try:
            result = clone_repository(req.url, req.target_folder)
            span.set_attribute("status", "success")
            return {"message": result}
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files")
async def get_files(path: str = Query(default=".", description="Chemin du repertoire a lister")):
    with tracer.start_as_current_span("api.list_files") as span:
        span.set_attribute("http.route", "/api/files")
        span.set_attribute("repo.path", path)
        try:
            files = list_files(path)
            span.set_attribute("file.count", len(files))
            span.set_attribute("status", "success")
            return {"files": files, "path": path}
        except HTTPException as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e.detail))
            raise
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/file")
async def get_file(path: str = Query(description="Chemin du fichier a lire")):
    with tracer.start_as_current_span("api.read_file") as span:
        span.set_attribute("http.route", "/api/file")
        span.set_attribute("file.path", path)
        try:
            content = read_file(path)
            span.set_attribute("file.size_bytes", len(content.encode("utf-8")))
            span.set_attribute("status", "success")
            return {"content": content, "path": path}
        except HTTPException as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e.detail))
            raise
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_code(req: AnalyzeRequest):
    with tracer.start_as_current_span("api.analyze_code") as span:
        span.set_attribute("http.route", "/api/analyze")
        span.set_attribute("file.path", req.file_path)
        try:
            content = read_file(req.file_path)
            result = get_code_structure(content)
            span.set_attribute("status", "success")
            return {"result": result, "file_path": req.file_path}
        except HTTPException as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e.detail))
            raise
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan")
async def scan_vulns(req: ScanRequest):
    with tracer.start_as_current_span("api.scan_vulnerabilities") as span:
        span.set_attribute("http.route", "/api/scan")
        span.set_attribute("repo.target", req.target_path)
        try:
            result = run_scan(req.target_path)
            span.set_attribute("status", "success")
            return {"result": result, "target_path": req.target_path}
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain")
async def explain(req: ExplainRequest):
    with tracer.start_as_current_span("api.explain_file") as span:
        span.set_attribute("http.route", "/api/explain")
        span.set_attribute("file.path", req.file_path)
        try:
            result = explain_file(req.file_path)
            span.set_attribute("file.language", result.get("language", "unknown"))
            span.set_attribute("llm.tokens", result.get("tokens", 0))
            span.set_attribute("status", "success")
            return result
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/traces")
async def get_traces(limit: int = Query(default=100, ge=1, le=500)):
    with tracer.start_as_current_span("api.get_traces") as span:
        span.set_attribute("http.route", "/api/traces")
        span.set_attribute("trace.limit", limit)
        if not os.path.exists(TRACES_FILE):
            span.set_attribute("trace.count", 0)
            return {"traces": [], "count": 0}

        traces = []
        with open(TRACES_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    traces.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        traces = traces[-limit:]
        traces.reverse()
        span.set_attribute("trace.count", len(traces))
        return {"traces": traces, "count": len(traces)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
