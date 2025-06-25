from abc import ABC, abstractmethod

from pydantic.functional_validators import AnyType

class IExchange(ABC):
    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> float: ...

    @abstractmethod
    async def get_current_price(self, symbol: str) -> float: ...

    @abstractmethod
    async def open_short_position(self, symbol: str, size: float, leverage: int) -> AnyType: ...

    @abstractmethod
    async def close_position(self, symbol: str, size: float, leverage: int) -> AnyType: ...

    @abstractmethod
    async def get_current_perpetual_position(self, symbol: str) -> AnyType: ...

    @abstractmethod
    async def close(self) -> None: ...
