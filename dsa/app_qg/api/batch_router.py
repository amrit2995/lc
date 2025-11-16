import logging

from fastapi import APIRouter,HTTPException,BackgroundTasks
from models.product_request_file import ProductRequestFile
from models.error_response import ErrorResponse
from service.batch_service import BatchService
from helpers.common import UtilityClass

router: APIRouter = APIRouter()

logger = logging.getLogger(__name__)

bs = BatchService()

    

@router.post('/submit-batch-products')
async def submitBatchProducts(prf: ProductRequestFile, background_tasks: BackgroundTasks):
    UtilityClass.handleInfoLogs("Product Request File",prf)
    response = await bs.submit_batch_products(prf,background_tasks)
    if response is not None:
        return response
    else:
        error_response = ErrorResponse(
            status_code=404,
            message="OminItemId  not found in QGEN",
            detail=f"No Search termns found for  ID {prf.omniItemIds}"
        )
        raise HTTPException(status_code=404, detail=error_response.model_dump())
    

@router.get('/fetch-by-requestId/{request_id}')
async def fetchByRequestId(request_id: str = None):
    UtilityClass.handleInfoLogs("Request Id",request_id)
    response = await bs.fetch_by_request_id(request_id)
    if response is not None:
        return response
    else:
        error_response = ErrorResponse(
            status_code=404,
            message="Request Id not found",
            detail=f"No Request found for  ID : {request_id}"
        )
        raise HTTPException(status_code=404, detail=error_response.model_dump())