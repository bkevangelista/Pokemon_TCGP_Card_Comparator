import asyncio
from collections import defaultdict

from tcgdexsdk import TCGdex

async def main():
    # Init the SDK
    tcgdex = TCGdex()
    tcgp_series = await tcgdex.serie.get("tcgp")
    tcgp_sets = tcgp_series.sets

    cards_by_set = defaultdict(list)

    for tcgp_set in tcgp_sets:
        set_name = tcgp_set.name
        set_data = await tcgdex.set.get(tcgp_set.id)
        cards = set_data.cards

        for card in cards:
            card_metadata = await tcgdex.card.get(card.id)
            c = {
                "id": card.id,
                "name": card.name,
                "localId": card.localId,
                "rarity": card_metadata.rarity,
            }
            print("Card being processed: ", c)

            cards_by_set[set_name].append(c)

    print(cards_by_set)

if __name__ == "__main__":
    asyncio.run(main())