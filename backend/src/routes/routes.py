import asyncio

from fastapi import APIRouter, Depends, BackgroundTasks, status
from tcgdexsdk import TCGdex

from backend.src.factories.DynamoDBProvider import get_tcg_card_dynamodb_service
from backend.src.models.TCGSetPayload import TCGSetPayload
from backend.src.services.CardFetcherService import CardFetcherService
from backend.src.services.DynamoDBService import DynamoDBService

router = APIRouter()

def get_tcgdex():
    return TCGdex()

def get_card_fetcher(
        tcgdex: TCGdex = Depends(get_tcgdex),
        db_service: DynamoDBService = Depends(get_tcg_card_dynamodb_service)
):
    return CardFetcherService(tcgdex, db_service)

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
@router.post(f"{tcgBaseEndpoint}/addCards", status_code=status.HTTP_202_ACCEPTED)
async def addCards(
        set_payload: TCGSetPayload,
        background_tasks: BackgroundTasks,
        card_service: CardFetcherService = Depends(get_card_fetcher),
):
    set_name = set_payload.set_name
    def run_sync():
        asyncio.run(card_service.insertAllCards(set_name))

    background_tasks.add_task(run_sync)

    return {
        "message": f"Accepted task to add cards from set: {set_name}",
    }

@router.get(f"{tcgBaseEndpoint}/getCards")
async def getCards(
        set_id: str | None,
        card_service: CardFetcherService = Depends(get_card_fetcher),
):
    cards_from_set = await card_service.db_service.get_cards_by_set_id(set_id)
    return {
        "message": f"Number of cards from set {set_id}: {len(cards_from_set)}",
        "cards": cards_from_set,
    }

@router.get(f"{tcgBaseEndpoint}/getSets")
async def getSets(
        card_service: CardFetcherService = Depends(get_card_fetcher),
):
    set_mapping = await card_service.getSets()
    return {
        "message": "Successfully fetched set ID to set name mapping",
        "tcgSets": set_mapping,
    }
