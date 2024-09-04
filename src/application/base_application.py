from abc import ABC, abstractmethod
from typing import Any


class BaseApplication(ABC):
    async def execute(self, input: Any):
        raise NotImplementedError
