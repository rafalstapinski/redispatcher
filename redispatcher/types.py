from pydantic import BaseModel


class MessageContainer(BaseModel):
    headers: dict
    body: dict
