from datetime import datetime
from pydantic import BaseModel, Field

class PoolSnapshot(BaseModel):
    reserve_token0: float = Field(..., description="Reserve amount of token0 (USDC)")
    reserve_token1: float = Field(..., description="Reserve amount of token1 (WETH)")
    timestamp: datetime = Field(..., description="Unix timestamp of when the snapshot was taken")
