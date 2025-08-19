import asyncio
from collections import defaultdict

from tcgdexsdk import TCGdex

from backend.src.constants.CardRarity import CardRarity
from backend.src.models.CardMetadata import CardMetadata
from backend.src.models.TCGSetMapping import TCGSetMapping
from backend.src.models.UserCard import UserCard
from backend.src.services.DynamoDBService import DynamoDBService

class CardFetcherService:
    def __init__(self, tcgdex: TCGdex, db_service: DynamoDBService):
        self.tcgdex = tcgdex
        self.db_service = db_service

    def findSetObjectFromSetName(self, set_name: str, tcgp_sets: list):
        for set_brief in tcgp_sets:
            if set_brief.name == set_name:
                return set_brief

        return None

    async def _fetchCardData(self, card, set_name, set_id):
        card_metadata = await self.tcgdex.card.get(card.id)
        return CardMetadata(
            id=card.id,
            name=card_metadata.name,
            local_id=card_metadata.localId,
            set_name=set_name,
            set_id=set_id,
            rarity=card_metadata.rarity if card_metadata.rarity != "None" else None,
            image=card_metadata.image,
        )

    async def getAllCardsBySet(self, set_name: str | None):
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
                    self._fetchCardData(card, set_name, set_id)
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
                    self._fetchCardData(card, set_name, set_id)
                    for card in cards
                ]
                card_results = await asyncio.gather(*card_tasks)

                cards_by_set[set_name].extend(card_results)

        return cards_by_set

    async def insertAllCards(self, set_name: str | None):
        cards_by_set = await self.getAllCardsBySet(set_name)
        tasks = [self.db_service.batch_insert_cards(cards) for cards in cards_by_set.values()]
        await asyncio.gather(*tasks)

    async def getSets(self):
        tcgp_series = await self.tcgdex.serie.get("tcgp")
        tcgp_sets = tcgp_series.sets

        return [
            TCGSetMapping(
                set_id=tcgp_set.id,
                set_name=tcgp_set.name,
            )
            for tcgp_set in tcgp_sets
        ]

    async def insertCardsForUser(self, user_cards: list[UserCard]):
        tasks = [self.db_service.batch_insert_cards(user_cards)]
        await asyncio.gather(*tasks)

    async def getCardsOwnedByUserAndBySet(self, user_id: str, set_id: str):
        card_response = await self.db_service.get_cards_by_user_and_set(user_id, set_id)
        return [
            UserCard(
                user_id=user_id,
                card_id=card["card_id"],
                set_id=set_id,
                no_owned=int(card["no_owned"]),
            )
            for card in card_response
        ]

    def _convertUserCardsIntoMap(self, user_cards: list[UserCard]):
        return {user_card.card_id: user_card for user_card in user_cards if user_card.no_owned > 0}

    async def compareCardsForUsersToTrade(self, user1: str, user2: str, set_id: str, cards_in_set: list[CardMetadata]):
        user1_cards = await self.getCardsOwnedByUserAndBySet(user1, set_id)
        user2_cards = await self.getCardsOwnedByUserAndBySet(user2, set_id)

        # Convert user cards into hash map
        user1_map, user2_map = self._convertUserCardsIntoMap(user1_cards), self._convertUserCardsIntoMap(user2_cards)

        tradeable_cards = []

        for card in cards_in_set:
            # A card is tradeable if only one user has it and they own more than one
            # We also want to filter out cards that are 3-Star or Crown rarity
            if (
                card["rarity"] and
                CardRarity.CARD_RARITY[card["rarity"]] < CardRarity.CARD_RARITY["Three Star"] and
                (card["id"] in user1_map and card["id"] not in user2_map and user1_map[card["id"]].no_owned > 1) or
                (card["id"] in user2_map and card["id"] not in user1_map and user2_map[card["id"]].no_owned > 1)
            ):
                card_to_add = user1_map[card["id"]] if card["id"] in user1_map else user2_map[card["id"]]

                card_to_add.image = card["image"]
                card_to_add.rarity = card["rarity"]
                card_to_add.name = card["name"]

                tradeable_cards.append(card_to_add)

        return tradeable_cards
