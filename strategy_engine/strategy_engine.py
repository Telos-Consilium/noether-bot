from database_manager.database_manager import DatabaseManager
from models.position_snapshot import PositionSnapshot
from config.config import ConfigManager
from risk_manager.risk_manager import RiskManager
from logger_manager.logger_manager import LoggerManager

config = ConfigManager()
database = DatabaseManager()
binance_exchange = config.get_exchange('binance')
risk_manager = RiskManager()
logger = LoggerManager()
symbol_ccxt = "ETH/USDT:USDT"


class StrategyEngine:
    def calculate_required_hedge(self, position_snapshot: PositionSnapshot) -> float:
        delta = position_snapshot.reserve_token1 - position_snapshot.short_position_size
        return round(delta, 8)

    def should_execute_hedge(self, amount: float, market_conditions):
        # delta threshold only beyond which hedge is executed
        if abs(amount) >= 0.005:
            return True
        else:
            return False

    async def process_position_snapshot(self, position_snapshot: PositionSnapshot):
        if position_snapshot.reserve_token1 != position_snapshot.short_position_size:
            calculated_hedge = self.calculate_required_hedge(position_snapshot)
            logger.log_calculated_hedge(calculated_hedge)
            if self.should_execute_hedge(calculated_hedge, None):
                leverage = risk_manager.calculate_optimal_leverage(None)
                logger.log_leverage(leverage)
                if calculated_hedge > 0:
                    order = await binance_exchange.open_short_position(
                        symbol_ccxt,
                        calculated_hedge,
                        leverage
                    )
                    logger.log_open_short_position(order)
                else:
                    order = await binance_exchange.close_position(
                        symbol_ccxt,
                        abs(calculated_hedge),
                        leverage
                    )
                    logger.log_close_short_position(order)
                database.save_hedge_snapshot(order, leverage)
