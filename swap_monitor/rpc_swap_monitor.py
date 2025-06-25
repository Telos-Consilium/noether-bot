import asyncio
from typing import Callable, Optional
from web3 import Web3
from exchange_manager.exchange import IExchange
from models.position_snapshot import PositionSnapshot
from swap_monitor.swap_monitor import ISwapMonitor
from logger_manager.logger_manager import LoggerManager
from database_manager.database_manager import DatabaseManager
from datetime import datetime
import json


logger = LoggerManager()
database = DatabaseManager()

POLL_INTERVAL_SEC = 5000

class RPCSwapMonitor(ISwapMonitor):
    def __init__(self, rpc_url: str, abi_path: str, exchange: IExchange, symbol_perpetual: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = None
        self.pool_address = None
        self._callback: Optional[Callable[[PositionSnapshot], None]] = None
        self._running = False
        self.abi = json.load(open(abi_path))
        self.exchange = exchange
        self.symbol_perpetual = symbol_perpetual

    def on_reserve_change(self, callback: Callable[[PositionSnapshot], None]) -> None:
        self._callback = callback

    def start_monitoring(self, pool_address: str) -> None:
        self.pool_address = Web3.to_checksum_address(pool_address)
        self.contract = self.web3.eth.contract(address=self.pool_address, abi=self.abi)
        self._running = True
        asyncio.create_task(self._monitor_loop())

    def stop_monitoring(self) -> None:
        self._running = False

    async def _monitor_loop(self):
        if self.contract is None:
            raise RuntimeError("Contract not initialized. Call start_monitoring first.")
        while self._running:
            reserves = self.contract.functions.getReserves().call()
            position = await self.exchange.get_current_perpetual_position(self.symbol_perpetual)
            current = PositionSnapshot(reserve_token0=reserves[0]/10**6, reserve_token1=reserves[1]/10**18, timestamp=datetime.now(), short_position_size=position)
            database.save_position_snapshot(current)
            logger.log_position_polling(current)
            if self._callback:
                self._callback(current)
            await asyncio.sleep(POLL_INTERVAL_SEC)
