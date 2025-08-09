from backend.src.services.DynamoDBService import DynamoDBService

def get_tcg_card_dynamodb_service() -> DynamoDBService:
    return DynamoDBService(table_name="TCG_Cards")