# strategy_engine/strategy_engine.py

from models.position_snapshot import PositionSnapshot
from config.config import ConfigManager
from risk_manager.risk_manager import RiskManager
from logger_manager.logger_manager import LoggerManager
from database_manager.database_manager import DatabaseManager

symbol_ccxt = "ETH/USDT:USDT"

class StrategyEngine:
    def __init__(
        self,
        logger: LoggerManager,
        config: ConfigManager,
        database: DatabaseManager,
        risk_manager: RiskManager
    ):
        self.logger = logger
        self.config = config
        self.database = database
        self.risk_manager = risk_manager
        self.binance_exchange = self.config.get_exchange('binance')

    def calculate_required_hedge(self, position_snapshot: PositionSnapshot) -> float:
        delta = position_snapshot.reserve_token1 - position_snapshot.short_position_size
        return round(delta, 8)

    def should_execute_hedge(self, amount: float, market_conditions):
        return abs(amount) >= 0.005

    async def process_position_snapshot(self, position_snapshot: PositionSnapshot):
        if position_snapshot.reserve_token1 != position_snapshot.short_position_size:
            calculated_hedge = self.calculate_required_hedge(position_snapshot)
            self.logger.log_calculated_hedge(calculated_hedge)
            if self.should_execute_hedge(calculated_hedge, None):
                leverage = self.risk_manager.calculate_optimal_leverage(None)
                self.logger.log_leverage(leverage)
                if calculated_hedge > 0:
                    order = await self.binance_exchange.open_short_position(
                        symbol_ccxt, calculated_hedge, leverage
                    )
                    self.logger.log_open_short_position(order)
                else:
                    order = await self.binance_exchange.close_position(
                        symbol_ccxt, abs(calculated_hedge), leverage
                    )
                    self.logger.log_close_short_position(order)
                self.database.save_hedge_snapshot(order, leverage)
