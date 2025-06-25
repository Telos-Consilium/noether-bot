from abc import ABC, abstractmethod
from typing import Callable
from models.position_snapshot import PositionSnapshot

class ISwapMonitor(ABC):
    @abstractmethod
    def start_monitoring(self, pool_address: str) -> None:
        pass

    @abstractmethod
    def stop_monitoring(self) -> None:
        pass

    @abstractmethod
    def on_reserve_change(self, callback: Callable[[PositionSnapshot], None]) -> None:
        pass
