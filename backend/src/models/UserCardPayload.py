from pydantic import BaseModel

from backend.src.models.UserCard import UserCard

class UserCardPayload(BaseModel):
    cards: list[UserCard]
