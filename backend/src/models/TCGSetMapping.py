from pydantic import BaseModel

class TCGSetMapping(BaseModel):
    set_id: str
    set_name: str
