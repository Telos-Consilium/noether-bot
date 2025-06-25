from datetime import datetime
from pydantic import BaseModel


class HedgeSnapshot(BaseModel):
    timestamp: datetime
    symbol: str
    side: str
    amount: float
    avg_price: float
    total_cost: float
    order_id: str
    client_order_id: str
    leverage_used: int
