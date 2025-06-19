import asyncio
from typing import Callable, Optional
from web3 import Web3
from models.pool_snapshot import PoolSnapshot
from swap_monitor.swap_monitor import ISwapMonitor
from datetime import datetime
import json
import os

POLL_INTERVAL_SEC = 5

class RPCSwapMonitor(ISwapMonitor):
    def __init__(self, rpc_url: str, abi_path: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = None
        self.pool_address = None
        self._callback: Optional[Callable[[PoolSnapshot], None]] = None
        self._running = False
        self.abi = json.load(open(abi_path))

    def on_reserve_change(self, callback: Callable[[PoolSnapshot], None]) -> None:
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
        prev_reserves = None
        while self._running:
            reserves = self.contract.functions.getReserves().call()
            current = PoolSnapshot(reserve_token0=reserves[0]/10**6, reserve_token1=reserves[1]/10**18, timestamp=datetime.utcnow())

            if prev_reserves is None or current != prev_reserves:
                prev_reserves = current
                if self._callback:
                    self._callback(current)

            await asyncio.sleep(POLL_INTERVAL_SEC)
