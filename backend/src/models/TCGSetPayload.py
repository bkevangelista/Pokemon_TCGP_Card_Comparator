from pydantic import BaseModel

class TCGSetPayload(BaseModel):
    set_name: str | None

