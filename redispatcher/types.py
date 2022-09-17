from typing import Any, Callable, Optional

from pydantic import BaseModel


class MessageContainer(BaseModel):
    headers: dict
    body: dict


class LoggerType:
    info: Callable[[str, Optional[Any], Optional[Any]], None]
    error: Callable[[str, Optional[Any], Optional[Any]], None]
    warning: Callable[[str, Optional[Any], Optional[Any]], None]
    exception: Callable[[str, Optional[Any], Optional[Any]], None]
