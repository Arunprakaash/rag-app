from pydantic import BaseModel

class Tenant(BaseModel):
    name: str

class Query(BaseModel):
    text: str
    k: int = 5