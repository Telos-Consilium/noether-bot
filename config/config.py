# config_manager.py

from pydantic import BaseModel
from typing import Any, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class APICredentials(BaseModel):
    api_key: str
    api_secret: str


class StrategyConfig(BaseModel):
    min_hedge_size: float
    max_slippage: float
    preferred_exchanges: list[str]
    leverage_limits: dict[str, float]
    poll_interval_sec: int


class RiskConfig(BaseModel):
    max_position_size: float
    liquidation_buffer_pct: float
    pnl_stop_threshold: float

class ConfigManager:
    def __init__(self):
        self._strategy_config = StrategyConfig(
            min_hedge_size=100.0,
            max_slippage=0.005,
            preferred_exchanges=["binance"],
            leverage_limits={"binance": 5},
            poll_interval_sec=5,
        )

        self._risk_config = RiskConfig(
            max_position_size=1000.0,
            liquidation_buffer_pct=10.0,
            pnl_stop_threshold=-0.05,
        )

        self._credentials = {
            "binance": APICredentials(
                api_key=os.getenv("BINANCE_API_KEY", ""),
                api_secret=os.getenv("BINANCE_API_SECRET", ""),
            )
        }

    def get_exchange_credentials(self, exchange: str) -> APICredentials:
        return self._credentials[exchange]

    def get_strategy_parameters(self) -> StrategyConfig:
        return self._strategy_config

    def get_risk_limits(self) -> RiskConfig:
        return self._risk_config

    def get_eulerswap_pool_address(self) -> str:
        return os.getenv("EULERSWAP_POOL", "")

    def update_parameter(self, key: str, value: Any) -> None:
        if hasattr(self._strategy_config, key):
            setattr(self._strategy_config, key, value)
        elif hasattr(self._risk_config, key):
            setattr(self._risk_config, key, value)
        else:
            raise KeyError(f"Invalid config key: {key}")
