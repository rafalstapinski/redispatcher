from pydantic import BaseModel


class MessageContainer(BaseModel):
    headers: BaseModel
    body: BaseModel
