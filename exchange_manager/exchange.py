from abc import ABC, abstractmethod

class IExchange(ABC):
    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> float: ...

    @abstractmethod
    async def get_current_price(self, symbol: str) -> float: ...

    # @abstractmethod
    # async def open_short_position(self, symbol: str, size: float, leverage: int) -> Position: ...

    # @abstractmethod
    # async def close_position(self, position_id: str) -> PositionResult: ...

    # @abstractmethod
    # async def get_position_status(self, position_id: str) -> Position: ...
