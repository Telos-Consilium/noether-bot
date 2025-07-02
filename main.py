import asyncio
from risk_manager.risk_manager import RiskManager
from swap_monitor.rpc_swap_monitor import RPCSwapMonitor
from models.position_snapshot import PositionSnapshot
from config.config import ConfigManager
from exchange_manager.binance_exchange import BinanceExchange
from strategy_engine.strategy_engine import StrategyEngine
from database_manager.database_manager import DatabaseManager
from logger_manager.logger_manager import LoggerManager
from datetime import datetime

import os

config = ConfigManager()
database = DatabaseManager()
risk_manager = RiskManager()
RPC_URL = config.get_rpc_url()
POOL_ADDRESS = config.get_eulerswap_pool_address()
ABI_PATH = "abi/euler_swap_pool_abi.json"

def on_reserve_change(snapshot: PositionSnapshot):
    print(f"[{snapshot.timestamp}] Reserve Snapshot:")
    print(f"Token0: {snapshot.reserve_token0}, Token1: {snapshot.reserve_token1}")
    print(f"Short Position (in ETH): {snapshot.short_position_size}")
    # shift above to logger
    database.save_position_snapshot(snapshot)

async def main():
    await test_strategy_engine()

    # binance_exchange = config.get_exchange('binance')
    # # binance_exchange_creds = config.get_exchange_credentials('binance')
    # # binance_exchange = BinanceExchange(api_key=binance_exchange_creds.api_key, api_secret=binance_exchange_creds.api_secret)
    # symbol_ccxt = "ETH/USDT:USDT"

    # monitor = RPCSwapMonitor(rpc_url=RPC_URL, abi_path=ABI_PATH, exchange=binance_exchange, symbol_perpetual=symbol_ccxt)
    # monitor.on_reserve_change(on_reserve_change)
    # monitor.start_monitoring(POOL_ADDRESS)

    # print(f"Started monitoring pool at {POOL_ADDRESS}")


    # symbol_raw = "ETHUSDT"
    # mark_price = await binance_exchange.get_current_price(symbol_raw)
    # funding_rate = await binance_exchange.get_funding_rate(symbol_raw)


    # print(f"Current Mark Price for {symbol_raw}: {mark_price}")
    # print(f"Current Funding Rate for {symbol_raw}: {funding_rate:.6%}")


    # sample_short_size = 0.01
    # sample_leverage = 1 # for now, hardcoded to one

    # print("Opening short position with sample sizes ...")
    # order = await binance_exchange.open_short_position(symbol_ccxt, sample_short_size, sample_leverage)
    # print("Order result", order)

    # print("Current perpetual position on binance: ")
    # res = await binance_exchange.get_current_perpetual_position(symbol_ccxt)
    # print(res)
    # await binance_exchange.close()
    while True:
        await asyncio.sleep(3600)

async def test_strategy_engine():
    logger = LoggerManager()
    strategy_engine = StrategyEngine(logger, config, database, risk_manager)

    # t = 0s
    snapshot_open_short = PositionSnapshot(
        reserve_token0=2000.0,
        reserve_token1=0.05,
        short_position_size=0.038,
        timestamp=datetime.now()
    )

    # t = 5s
    snapshot_close_short = PositionSnapshot(
        reserve_token0=2500.0,
        reserve_token1=0.02,
        short_position_size=0.05,  # Reflects hedge at t=0s
        timestamp=datetime.now()
    )

    # t = 0s simulation
    snapshot = snapshot_open_short
    logger.log_position_polling(snapshot)
    await strategy_engine.process_position_snapshot(snapshot)
    print()
    # t = 5s simulation
    snapshot = snapshot_close_short
    logger.log_position_polling(snapshot)
    await strategy_engine.process_position_snapshot(snapshot)

if __name__ == "__main__":
    asyncio.run(main())
