from pydantic import BaseModel

class UserCard(BaseModel):
    user_id: str
    card_id: str
    set_id: str
    no_owned: int
    image: str | None = None
    rarity: str | None = None
    name: str | None = None