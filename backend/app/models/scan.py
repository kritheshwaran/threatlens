from pydantic import BaseModel

class Scan(BaseModel):
    url: str
    result: str
