from abc import ABC, abstractmethod
from typing import Callable
from models.pool_snapshot import PoolSnapshot

class ISwapMonitor(ABC):
    @abstractmethod
    def start_monitoring(self, pool_address: str) -> None:
        pass

    @abstractmethod
    def stop_monitoring(self) -> None:
        pass

    @abstractmethod
    def on_reserve_change(self, callback: Callable[[PoolSnapshot], None]) -> None:
        pass
