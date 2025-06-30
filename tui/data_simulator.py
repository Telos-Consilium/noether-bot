from models.position_snapshot import PositionSnapshot
from datetime import datetime, timedelta
import random
import asyncio

class SnapshotSimulator:
    def __init__(self):
        self._usdc = 10000.0
        self._weth = 0.05
        self._short_position = 0.04
        self._time = datetime.now()

    def next_snapshot(self) -> PositionSnapshot:
        # Simulate tiny random change in WETH
        self._weth += random.uniform(-0.002, 0.002)
        self._weth = max(0, round(self._weth, 4))

        # Simulate hedging response
        delta = self._weth - self._short_position
        if abs(delta) > 0.005:
            self._short_position += 0.003 * (1 if delta > 0 else -1)
            self._short_position = max(0, round(self._short_position, 4))

        self._time += timedelta(seconds=5)

        return PositionSnapshot(
            reserve_token0=self._usdc,
            reserve_token1=self._weth,
            short_position_size=self._short_position,
            timestamp=self._time
        )

    async def generate_snapshots(self):
        while True:
            yield self.next_snapshot()
            await asyncio.sleep(5)
