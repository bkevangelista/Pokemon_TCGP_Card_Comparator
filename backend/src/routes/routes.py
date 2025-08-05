from http import HTTPStatus

from fastapi import APIRouter, Depends
from tcgdexsdk import TCGdex

from backend.src.models.TCGSetPayload import TCGSetPayload
from backend.src.services.CardFetcherService import CardFetcherService

router = APIRouter()

def get_tcgdex():
    return TCGdex()

def get_card_fetcher(tcgdex: TCGdex = Depends(get_tcgdex)):
    return CardFetcherService(tcgdex)

'''
Base APIs
'''
@router.get("/")
def landing_api():
    return {"message": "Welcome to the Pokemon TCGP Card Comparator!"}

@router.get("/health")
def health_check():
    return {"message": "Health check returned successful response!"}

'''
APIs for TCGDex Service
'''
tcgBaseEndpoint = "/external/tcg"
@router.post(f"{tcgBaseEndpoint}/addCards")
async def addCards(
        set_payload: TCGSetPayload,
        card_service: CardFetcherService = Depends(get_card_fetcher),
):
    set_name = set_payload.set_name
    await card_service.getAllCardsBySet(set_name)

    return {
        "message": f"Would add cards from set: {set_name}",
        "statusCode": HTTPStatus.ACCEPTED,
    }

@router.get(f"{tcgBaseEndpoint}/getCards")
async def getCards(set_name: str | None):
   return {"message": f"Return all cards from set: {set_name}"}
