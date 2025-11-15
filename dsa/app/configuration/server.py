
import uvicorn
from fastapi import FastAPI
from gunicorn.app.base import BaseApplication
from configuration.application_config import ApplicationConfig
from configuration.listeners import on_starting, on_exit, worker_int, worker_abort


class GunicornServer(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.app = app

        super().__init__()

    def load_config(self):
        config = {key: val for key, val in self.options.items()}
        for key, val in config.items():
            self.cfg.set(key.lower(), val)

    def load(self):
        return self.app


def run_gunicorn_server(app: FastAPI, parser: ApplicationConfig):
    configs: dict = parser.parse_config('servers.gunicorn')
    options = {
        'bind': configs['bind'],
        'workers': configs['num_workers'],
        'accesslog': '-',
        'errorlog': '-',
        'worker_class': 'uvicorn.workers.UvicornH11Worker',
        'timeout': configs['timeout'],
        'graceful_timeout': configs['graceful_timeout'],
        'keepalive': configs['graceful_timeout'],
        'max_requests': configs['keepalive'],
        'max_requests_jitter': configs['max_requests_jitter'],
        'backlog': configs['backlog'],
        'preload_app': True,
        'on_starting': on_starting,
        'on_exit': on_exit,
        'worker_int': worker_int,
        'worker_abort': worker_abort,
        'loglevel': configs['loglevel'],
        # 'logconfig_dict': GUNICORN_LOGGING
    }

    GunicornServer(app, options).run()


def run_uvicorn_server(app: str, parser: ApplicationConfig):
    on_starting(None)
    configs: dict = parser.parse_config('servers.uvicorn')
    uvicorn.run(app=app,
                host=configs['host'],
                port=configs['port'],
                log_level=configs['loglevel'],
                access_log=configs['access_log'],
                workers=configs['num_workers'],
                limit_concurrency=configs['limit_concurrency'],
                # log_config=UVICORN_LOGGING
                )
