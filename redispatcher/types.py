from typing import Any, Callable

from pydantic import BaseModel


class MessageContainer(BaseModel):
    headers: dict
    body: dict


class Logger:
    info: Callable[[str, Any, Any], None]
    warning: Callable[[str, Any, Any], None]
    exception: Callable[[str, Any, Any], None]
