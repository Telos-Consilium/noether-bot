import asyncio
from swap_monitor.rpc_swap_monitor import RPCSwapMonitor
from models.pool_snapshot import PoolSnapshot
from config.config import ConfigManager
import os

config = ConfigManager()
RPC_URL = config.get_rpc_url()
POOL_ADDRESS = config.get_eulerswap_pool_address()
ABI_PATH = "abi/euler_swap_pool_abi.json"

def on_reserve_change(snapshot: PoolSnapshot):
    print(f"[{snapshot.timestamp}] Reserve Snapshot:")
    print(f"Token0: {snapshot.reserve_token0}, Token1: {snapshot.reserve_token1}")

async def main():
    monitor = RPCSwapMonitor(rpc_url=RPC_URL, abi_path=ABI_PATH)
    monitor.on_reserve_change(on_reserve_change)
    monitor.start_monitoring(POOL_ADDRESS)

    print(f"Started monitoring pool at {POOL_ADDRESS}")
    while True:
        await asyncio.sleep(3600)  # keep process alive (or use asyncio.Event for clean exit)

if __name__ == "__main__":
    asyncio.run(main())
