from pydantic import BaseModel


class JournalCreate(BaseModel):
    body: str
