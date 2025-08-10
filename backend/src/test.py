from fastapi import Depends
from tcgdexsdk import TCGdex

from backend.src.factories.DynamoDBProvider import get_tcg_card_dynamodb_service
from backend.src.services.DynamoDBService import DynamoDBService
from services.CardFetcherService import CardFetcherService

import asyncio

async def main():
    tcgdex = TCGdex()
    db_service = get_tcg_card_dynamodb_service()
    card_service = CardFetcherService(tcgdex, db_service)
    all_cards = await card_service.getAllCardsBySet(None)

    cards_to_insert = []
    for set_name, cards in all_cards.items():
        if set_name != "Promos-A" and set_name != "Genetic Apex":
            print(f"Preparing to insert cards of set: {set_name}")
            cards_to_insert.append(cards)
    tasks = [db_service.batch_insert_cards(cards) for cards in cards_to_insert]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())