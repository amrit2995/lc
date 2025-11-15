from typing import Callable, Coroutine
from fastapi import FastAPI
from helpers.common import UtilityClass



EventHandlerType = Callable[[], Coroutine[None, None, None]]


def on_starting(server):
    UtilityClass.handleInfoLogs('Executing on_starting')


def on_exit(server):
    UtilityClass.handleInfoLogs('Executing on_exit')


def worker_int(worker):
    UtilityClass.handleInfoLogs('Executing worker_int')


def worker_abort(worker):
    UtilityClass.handleInfoLogs('Executing worker_abort')


def create_startup_events_handler(app: FastAPI) -> EventHandlerType:
    async def startup() -> None:
        UtilityClass.handleInfoLogs('Executing startup')
        UtilityClass.handleInfoLogs('Finished startup')

    return startup


def create_shutdown_events_handler(app: FastAPI) -> EventHandlerType:
    async def shutdown() -> None:
        UtilityClass.handleInfoLogs('Executing shutdown')
        UtilityClass.handleInfoLogs('Finished shutdown')

    return shutdown
