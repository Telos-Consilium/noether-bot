from typing import List
from datetime import datetime
from models.position_snapshot import PositionSnapshot


class LoggerManager:
    def __init__(self):
        self._logs: List[str] = []

    def _log(self, tag: str, message: str):
        timestamp = datetime.utcnow().isoformat()
        entry = f"[{tag}] {message} | Timestamp: {timestamp}"
        self._logs.append(entry)
        print(entry)

    def log_position_polling(self, snapshot: PositionSnapshot):
        self._log(
            "POSITION_POLLING",
            f"USDC: {snapshot.reserve_token0}, WETH: {snapshot.reserve_token1}, WETH Short Position: {snapshot.short_position_size}"
        )

    def log_calculated_hedge(self, hedge_amount: float):
        self._log("CALCULATED_HEDGE", f"Calculated Hedge: {hedge_amount}")

    def log_leverage(self, leverage: float):
        self._log("LEVERAGE", f"Leverage: {leverage}")

    def log_open_short_position(self, order: dict):
        self._log(
            "OPEN_SHORT_POSITION",
            f"Side: {order.get('side')}, Amount: {order.get('amount')}, "
            f"Price: {order.get('price')}, Symbol: {order.get('symbol')}, Status: {order.get('status')}"
        )

    def log_close_short_position(self, order: dict):
        self._log(
            "CLOSE_SHORT_POSITION",
            f"Side: {order.get('side')}, Amount: {order.get('amount')}, "
            f"Price: {order.get('price')}, Symbol: {order.get('symbol')}, Status: {order.get('status')}"
        )

    def get_all_logs(self) -> List[str]:
        return self._logs

    def clear_logs(self):
        self._logs.clear()
