import asyncio
from collections import defaultdict

from tcgdexsdk import TCGdex

class CardFetcherService:
    def __init__(self, tcgdex: TCGdex):
        self.tcgdex = tcgdex

    def findSetObjectFromSetName(self, set_name: str, tcgp_sets: list):
        for set_brief in tcgp_sets:
            if set_brief.name == set_name:
                return set_brief

        return None

    async def fetchCardData(self, card, set_name, set_id):
        card_metadata = await self.tcgdex.card.get(card.id)
        return {
            "id": card.id,
            "name": card.name,
            "localId": card.localId,
            "rarity": card_metadata.rarity if card_metadata.rarity != "None" else None,
            "set_name": set_name,
            "set_id": set_id,
        }

    async def getAllCardsBySet(self, set_name: str | None):
        # Init the SDK
        tcgp_series = await self.tcgdex.serie.get("tcgp")
        tcgp_sets = tcgp_series.sets

        cards_by_set = defaultdict(list)
        if not set_name:
            for tcgp_set in tcgp_sets:
                set_name = tcgp_set.name
                set_id = tcgp_set.id
                set_data = await self.tcgdex.set.get(tcgp_set.id)
                cards = set_data.cards

                card_tasks = [
                    self.fetchCardData(card, set_name, set_id)
                    for card in cards
                ]
                card_results = await asyncio.gather(*card_tasks)

                cards_by_set[set_name].extend(card_results)

            return cards_by_set
        else:
            tcgp_set = self.findSetObjectFromSetName(set_name, tcgp_sets)
            if tcgp_set:
                set_id = tcgp_set.id

                set_data = await self.tcgdex.set.get(tcgp_set.id)
                cards = set_data.cards

                card_tasks = [
                    self.fetchCardData(card, set_name, set_id)
                    for card in cards
                ]
                card_results = await asyncio.gather(*card_tasks)

                cards_by_set[set_name].extend(card_results)

        return cards_by_set
