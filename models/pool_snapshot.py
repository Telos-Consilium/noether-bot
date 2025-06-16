from datetime import datetime
from pydantic import BaseModel, Field

class PoolSnapshot(BaseModel):
    reserve_token0: int = Field(..., description="Reserve amount of token0 (e.g., USDC) in smallest units")
    reserve_token1: int = Field(..., description="Reserve amount of token1 (e.g., WETH) in smallest units")
    timestamp: datetime = Field(..., description="Unix timestamp of when the snapshot was taken")
