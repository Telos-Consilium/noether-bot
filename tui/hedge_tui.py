# tui/hedge_tui.py
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.binding import Binding
from textual_plotext import PlotextPlot
from datetime import datetime
from models.position_snapshot import PositionSnapshot
from config.config import ConfigManager
from risk_manager.risk_manager import RiskManager
from strategy_engine.strategy_engine import StrategyEngine
from database_manager.database_manager import DatabaseManager
from logger_manager.logger_manager import LoggerManager
from exchange_manager.binance_exchange import BinanceExchange
from pathlib import Path
from textual.widgets import Log, RichLog
from typing import List, Optional
import asyncio
import numpy as np
import time

from swap_monitor.rpc_swap_monitor import RPCSwapMonitor
from test.test_importlib.test_abc import init


class HedgeStatus(Static):
    def update_status(self, s: PositionSnapshot):
        self.update(
            f"[b]USDC:[/b] {s.reserve_token0:.2f}\n"
            f"[b]WETH in Pool:[/b] {s.reserve_token1:.4f}\n"
            f"[b]WETH Short Pos:[/b] {s.short_position_size:.4f}\n"
            f"[b]Timestamp:[/b] {s.timestamp.strftime('%H:%M:%S')}"
        )


class ConfigStatus(Static):
    def update_status(self):
        curr_config = ConfigManager()
        curr_risk_config = curr_config.get_risk_limits()
        curr_strategy_params = curr_config.get_strategy_parameters()

        self.update(
            # f"[b]Max Position Size:[/b] {curr_risk_config.max_position_size:.2f}\n"
            # f"[b]Liquidation Buffer:[/b] {curr_risk_config.liquidation_buffer_pct:.2f}\n"
            f"[b]Min Hedge Size:[/b] {curr_strategy_params.min_hedge_size:.4f} WETH\n"
            f"[b]Current Perpetual Exchange:[/b] Binance\n"
            f"[b]Current EulerSwap Pool:[/b] {curr_config.get_eulerswap_pool_address()[:6]}...{curr_config.get_eulerswap_pool_address()[-4:]}\n"
        )


class NoETHerBotTUI(App):
    BINDINGS = [Binding("q", "quit", "Quit")]
    CSS_PATH = "styles.tcss"

    def __init__(self, simulator):
        super().__init__()
        self.sim = simulator
        self.status = HedgeStatus()
        self.params = ConfigStatus()
        self.logs = RichLog(auto_scroll=True, wrap=True, max_lines=100, min_width=78, markup=True)
        self.db = DatabaseManager()
        self.logger = LoggerManager()
        self.risk_manager = RiskManager()
        self.strategy_engine = None
        self.config = ConfigManager()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical():
                # WETH Reserve Plot
                yield PlotextPlot(id="weth_plot")
                # Short Position Plot
                yield PlotextPlot(id="short_plot")
            with Vertical():
                # yield Static("[b]Status[/b]")
                # yield HedgeStatus(id="status")
                # yield Static("[b]Logs[/b]")
                # # yield LogViewer(id="log")
                # yield self.status
                # yield self.logs
                with Horizontal():
                    with Vertical():
                        yield Static("[b]Current Position Snapshot[/b]")
                        yield self.status
                    with Vertical():
                        yield Static("[b]Hedge Strategy[/b]")
                        yield self.params
                yield Static("[b]Logs[/b]")
                yield self.logs
        yield Footer()

    async def on_mount(self):
        self.theme = "tokyo-night"
        self.res_x, self.res_y = [], []
        self.short_x, self.short_y = [], []
        self.start_time = time.time()

        RPC_URL = self.config.get_rpc_url()
        POOL_ADDRESS = self.config.get_eulerswap_pool_address()
        ABI_PATH = Path(__file__).resolve().parent.parent / "abi" / "euler_swap_pool_abi.json"
        binance_exchange = self.config.get_exchange("binance")
        binance_exchange_creds = self.config.get_exchange_credentials("binance")
        binance_exchange = BinanceExchange(
            api_key=binance_exchange_creds.api_key, api_secret=binance_exchange_creds.api_secret
        )
        symbol_ccxt = "ETH/USDT:USDT"

        rpc_monitor = RPCSwapMonitor(
            rpc_url=RPC_URL, abi_path=str(ABI_PATH), exchange=binance_exchange, symbol_perpetual=symbol_ccxt
        )
        rpc_monitor.init_contract(POOL_ADDRESS)

        self.strategy_engine = StrategyEngine(
            logger=self.logger,
            config=ConfigManager(),
            database=self.db,
            risk_manager=RiskManager(),
        )

        async def poller():
            weth_plot = self.query_one("#weth_plot", PlotextPlot)
            short_plot = self.query_one("#short_plot", PlotextPlot)
            logger = self.logger

            last_seen_logs = 0
            # count = -1

            while True and self.strategy_engine is not None:
                snapshot = await rpc_monitor.fetch_snapshot()
                # can be used to simulate alternating positions
                # count += 1
                # snapshot_open_short = PositionSnapshot(
                #      reserve_token0=2000.0,
                #      reserve_token1=0.05,
                #      short_position_size=0.038,
                #      timestamp=datetime.now()
                # )
                # snapshot_close_short = PositionSnapshot(
                #     reserve_token0=2500.0,
                #     reserve_token1=0.02,
                #     short_position_size=0.05,
                #     timestamp=datetime.now()
                # )
                # snapshot = snapshot_open_short
                # if count % 2 != 0:
                #     snapshot = snapshot_close_short
                logger.log_position_polling(snapshot)
                await self.strategy_engine.process_position_snapshot(snapshot)

                timestamp_label = snapshot.timestamp.strftime("%H:%M:%S")
                # Generate simulated WETH reserve data
                weth_reserve = snapshot.reserve_token1
                # Generate simulated short position data
                short_position = snapshot.short_position_size
                timestamp_float = snapshot.timestamp.timestamp()
                self.res_x.append(timestamp_float)
                self.res_y.append(weth_reserve)
                self.short_x.append(timestamp_float)
                self.short_y.append(short_position)

                weth_plot.plt.clear_data()
                weth_plot.plt.scatter(self.res_x, self.res_y, marker="dot")
                weth_plot.plt.plot(self.res_x, self.res_y, color="green")
                weth_plot.plt.title("WETH Reserve in Pool")
                weth_plot.plt.xlabel("Time (seconds)")
                weth_plot.plt.ylabel("WETH Reserve")
                weth_plot.plt.xticks(self.res_x, [datetime.fromtimestamp(x).strftime("%H:%M:%S") for x in self.res_x])

                short_plot.plt.clear_data()
                short_plot.plt.scatter(self.short_x, self.short_y, marker="dot")
                short_plot.plt.plot(self.short_x, self.short_y, color="red")
                short_plot.plt.title("ETHUSDT Perpetual")
                short_plot.plt.xlabel("Time (seconds)")
                short_plot.plt.ylabel("Short Position Size")
                short_plot.plt.xticks(
                    self.short_x, [datetime.fromtimestamp(x).strftime("%H:%M:%S") for x in self.short_x]
                )

                weth_plot.refresh()
                short_plot.refresh()

                self.status.update_status(snapshot)
                self.params.update_status()

                new_logs = self.logger.get_all_logs()[last_seen_logs:]
                self.logs.write(f"[bold][TIMESTAMP][/bold] {timestamp_label}\n")
                for log in new_logs:
                    self.logs.write(log)
                last_seen_logs += len(new_logs)
                self.logs.write("\n\n")

                # Keep only last 50 data points for (for now)
                if len(self.res_x) > 50:
                    self.res_x.pop(0)
                    self.res_y.pop(0)
                    self.short_x.pop(0)
                    self.short_y.pop(0)

                await asyncio.sleep(5)  # Polling interval

        self.run_worker(poller, exclusive=True)

    async def on_shutdown(self) -> None:
        if self.strategy_engine is not None:
            await self.strategy_engine.binance_exchange.close()


if __name__ == "__main__":
    from data_simulator import SnapshotSimulator

    sim = SnapshotSimulator()
    NoETHerBotTUI(sim).run()
