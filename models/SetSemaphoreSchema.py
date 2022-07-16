from typing import Literal
from pydantic import BaseModel


class SetSemaphoreSchema(BaseModel):
    state: Literal["red", "green", "off"]
