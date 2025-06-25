from typing import List
from models.position_snapshot import PositionSnapshot
from models.hedge_snapshot import HedgeSnapshot
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self._position_snapshots: List[PositionSnapshot] = []
        self._hedge_snapshots: List[HedgeSnapshot] = []

    def save_position_snapshot(self, snapshot: PositionSnapshot):
        self._position_snapshots.append(snapshot)

    def get_all_position_snapshots(self) -> List[PositionSnapshot]:
        return self._position_snapshots

    def get_latest_position_snapshot(self) -> PositionSnapshot:
        if not self._position_snapshots:
               raise RuntimeError("No position snapshots available.")
        return self._position_snapshots[-1]

    def save_hedge_snapshot(self, order: dict, leverage: int):
        hedge_snapshot = HedgeSnapshot(
            timestamp= datetime.fromtimestamp(order['timestamp'] / 1000),
            symbol=order['info']['symbol'],
            side=order['side'],
            amount=order['amount'],
            avg_price=order['average'],
            total_cost=order['cost'],
            order_id=order['id'],
            client_order_id=order['clientOrderId'],
            leverage_used=leverage,
        )
        self._hedge_snapshots.append(hedge_snapshot)

    def get_all_hedge_snapshots(self) -> List[HedgeSnapshot]:
        return self._hedge_snapshots

    def get_latest_hedge_snapshot(self) -> HedgeSnapshot:
        if not self._hedge_snapshots:
            raise RuntimeError("No hedge snapshots available.")
        return self._hedge_snapshots[-1]
