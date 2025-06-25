from datetime import datetime
from pydantic import BaseModel, Field

class PositionSnapshot(BaseModel):
    reserve_token0: float = Field(..., description="Reserve amount of token0 (USDC)")
    reserve_token1: float = Field(..., description="Reserve amount of token1 (WETH)")
    short_position_size: float = Field(..., description="Amount of ETH shorted currently")
    timestamp: datetime = Field(..., description="Unix timestamp of when the snapshot was taken")
