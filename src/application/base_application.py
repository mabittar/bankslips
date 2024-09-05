from abc import ABC
from typing import Any


class BaseApplication(ABC):
    async def execute(self, parsed_data: Any):
        raise NotImplementedError
