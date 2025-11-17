
from fastapi import FastAPI, Request
from starlette_exporter import PrometheusMiddleware, handle_metrics
from configuration.server import run_gunicorn_server, run_uvicorn_server
from configuration.application_config import ApplicationConfig
from helpers.common import UtilityClass
parser = ApplicationConfig()
from api import probes_router
from api import keywords_router
from api import batch_router



app = FastAPI(openapi_url=parser.parse_config('service.openapi_url'),
              docs_url=parser.parse_config('service.docs_url'))


app.add_middleware(PrometheusMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and outgoing responses with traceId and spanId."""
    UtilityClass.handleInfoLogs({
        "event": "request_received",
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
    })

    response = await call_next(request)

    UtilityClass.handleInfoLogs({
        "event": "response_sent",
        "status_code": response.status_code,
        "path": request.url.path,
        "method": request.method,
    })

    return response

app.add_route(parser.parse_config('service.metrics_path'), handle_metrics)
base_path: str = parser.parse_config('service.base_path')

app.include_router(batch_router.router, prefix=base_path)
app.include_router(probes_router.router, prefix=base_path)
app.include_router(keywords_router.router, prefix=base_path)


if __name__ == '__main__':
    active_server = parser.parse_config('servers.active')
    if active_server == 'gunicorn':
        run_gunicorn_server(app, parser)
    else:
        run_uvicorn_server("application:app", parser)