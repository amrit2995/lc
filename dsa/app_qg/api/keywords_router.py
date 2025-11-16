import logging

from fastapi import APIRouter,HTTPException
from models.product_request import ProductRequest
from models.keyword_request import KeywordRequest
from models.error_response import ErrorResponse
from service.keyword_service import KeywordService
from helpers.common import UtilityClass

router: APIRouter = APIRouter()

logger = logging.getLogger(__name__)

ks = KeywordService()


@router.post('/fetch-keywords')
async def fetchKeyWords(pr: ProductRequest):
    UtilityClass.handleInfoLogs("Product Request",pr)
    response = await ks.get_keywords(pr)
    if response is not None:
        return response
    else:
        error_response = ErrorResponse(
            status_code=404,
            message="OminItemId  not found in QGEN",
            detail=f"No Search termns found for  ID {pr.omniItemIds}"
        )
        raise HTTPException(status_code=404, detail=error_response.model_dump())
    


@router.post('/validate-keywords')
async def validateKeyWords(kr: KeywordRequest):
    UtilityClass.handleInfoLogs("Keyword Request",kr)
    response = await ks.validate_keywords(kr)
    if response is not None:
        return response
    else:
        error_response = ErrorResponse(
            status_code=404,
            message="OminItemId  not found in QGEN",
            detail=f"No product found for  ID {kr.omniItemIds}"
        )
        raise HTTPException(status_code=404, detail=error_response.model_dump())
