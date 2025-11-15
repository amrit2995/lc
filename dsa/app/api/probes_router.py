import logging

from fastapi import APIRouter
from config.configs import SERVER_READY, SERVER_LIVE

router: APIRouter = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/probes/ready')
async def ready():
    return {
        'status': SERVER_READY,
        'code': 200
    }


@router.get('/probes/live')
async def live():
    return {'status': SERVER_LIVE, 'code': 200}
