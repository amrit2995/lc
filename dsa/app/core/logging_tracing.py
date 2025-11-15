import logging
from pythonjsonlogger import jsonlogger
from opentelemetry.trace import get_current_span
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
import uuid

class TraceLoggingFilter(logging.Filter):
    """Custom logging filter to add traceId and spanId."""
    
    def filter(self, record):
        """Add traceId and spanId to log records, or generate fresh ones."""
        # Try to get the current active span from the OpenTelemetry context
        span = get_current_span()

        if span and span.get_span_context().is_valid:
            # If there's a valid span, use its traceId and spanId
            record.traceId = span.get_span_context().trace_id
            record.spanId = span.get_span_context().span_id
        else:
            # If no valid span, generate a new traceId and spanId
            trace_id = uuid.uuid4().hex  # Generate a new traceId
            span_id = uuid.uuid4().hex   # Generate a new spanId
            
            record.traceId = trace_id
            record.spanId = span_id


        return True

def setup_logger():
    """Set up JSON logging with traceId and spanId."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(traceId)s %(spanId)s')
    log_handler.setFormatter(formatter)

    # Add custom filter to log traceId and spanId
    log_handler.addFilter(TraceLoggingFilter())

    logger.addHandler(log_handler)

def setup_tracing():
    """Set up OpenTelemetry tracing."""
    # Create a TracerProvider and set it as the global tracer
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

    # Configure an exporter (ConsoleSpanExporter for local testing)
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    tracer_provider.add_span_processor(span_processor)

