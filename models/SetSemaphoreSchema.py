from typing import Literal
from pydantic import BaseModel


class SetSemaphoreSchema(BaseModel):
    id: int
    state: Literal["red", "yellow", "green", "redyellow", "off"]
