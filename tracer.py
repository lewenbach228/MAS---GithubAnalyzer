from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import json
import sys
from datetime import datetime, timezone

# Custom Exporter pour écrire dans un fichier sans polluer stdout
class FileSpanExporter(SpanExporter):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def export(self, spans: list[Span]) -> SpanExportResult:
        with open(self.filepath, "a") as f:
            for span in spans:
                duration_ns = span.end_time - span.start_time
                f.write(json.dumps({
                    "name": span.name,
                    "trace_id": format(span.context.trace_id, "032x"),
                    "span_id": format(span.context.span_id, "016x"),
                    "attributes": dict(span.attributes) if span.attributes else {},
                    "duration_ns": duration_ns,
                    "duration_ms": round(duration_ns / 1_000_000, 3),
                    "started_at": datetime.fromtimestamp(span.start_time / 1_000_000_000, tz=timezone.utc).isoformat(),
                    "ended_at": datetime.fromtimestamp(span.end_time / 1_000_000_000, tz=timezone.utc).isoformat(),
                }) + "\n")
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

# Initialiser le fournisseur de traces
resource = Resource(attributes={"service.name": "github-analyzer-mcp"})
provider = TracerProvider(resource=resource)

# Utiliser notre exporteur fichier
file_exporter = FileSpanExporter("traces.jsonl")
processor = BatchSpanProcessor(file_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Créer un tracer global
tracer = trace.get_tracer(__name__)
