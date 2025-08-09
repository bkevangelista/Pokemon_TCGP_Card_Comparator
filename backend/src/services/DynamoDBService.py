import asyncio

from dotenv import load_dotenv
import os
from boto3.dynamodb.conditions import Key
import aioboto3

from backend.src.models.CardMetadata import CardMetadata

load_dotenv()

class DynamoDBService:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.region = os.getenv("AWS_DEFAULT_REGION")
        self.session = aioboto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )

    async def insert_card(self, card: CardMetadata):
        async with self.session.resource("dynamodb", region_name=self.region) as client:
            table = await client.Table(self.table_name)
            await table.put_item(Item=card.model_dump())

    async def get_card(self, card_id):
        async with self.session.resource("dynamodb", region_name=self.region) as client:
            table = await client.Table(self.table_name)
            response = await table.get_item(Key={"id": card_id})
            return response.get("Item")

    async def batch_insert_cards(self, cards: list[CardMetadata], batch_size: int = 25):
        async with self.session.resource("dynamodb", region_name=self.region) as client:
            # Split input into batches of batch_size (limit is 25)
            batches = [
                cards[i : i + batch_size]
                for i in range(0, len(cards), batch_size)
            ]

            tasks = [self._write_batch(client, batch) for batch in batches]
            await asyncio.gather(*tasks)

    async def _write_batch(self, client, batch: list[CardMetadata]):
        request_items = {
            self.table_name: [
                {"PutRequest": {"Item": card.model_dump()}}
                for card in batch
            ]
        }

        await client.batch_write_item(RequestItems=request_items)

    async def get_cards_by_set_id(self, set_id: str):
        async with self.session.resource("dynamodb", region_name=self.region) as client:
            table = await client.Table(self.table_name)
            response = await table.query(
                IndexName="set_id-local_id-index",
                KeyConditionExpression=Key("set_id").eq(set_id),
            )

            return response["Items"]