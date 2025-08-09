from pydantic import BaseModel

class CardMetadata(BaseModel):
    id: str
    name: str
    local_id: str
    set_name: str
    set_id: str
    rarity: str | None = None
    image: str | None = None