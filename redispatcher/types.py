from typing import Any, Callable, Optional

from pydantic import BaseModel


class MessageContainer(BaseModel):
    headers: dict
    body: dict


class Logger:
    info: Callable[[str, Optional[Any], Optional[Any]], None]
    warning: Callable[[str, Optional[Any], Optional[Any]], None]
    exception: Callable[[str, Optional[Any], Optional[Any]], None]
