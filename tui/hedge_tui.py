# tui/hedge_tui.py

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from tui.graph_widget import LineGraphWidget
from datetime import datetime
from models.position_snapshot import PositionSnapshot
from textual.binding import Binding
import asyncio

class HedgeStatus(Static):
    def update_status(self, snapshot: PositionSnapshot):
        self.update(
            f"[b]USDC:[/b] {snapshot.reserve_token0:.2f}\n"
            f"[b]WETH in Pool:[/b] {snapshot.reserve_token1:.4f}\n"
            f"[b]WETH Short Position:[/b] {snapshot.short_position_size:.4f}\n"
            f"[b]Timestamp:[/b] {snapshot.timestamp.strftime('%H:%M:%S')}"
        )

class LogViewer(Static):
    def __init__(self):
        super().__init__()
        self.logs = []

    def log(self, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 30:
            self.logs.pop(0)
        self.update("\n".join(self.logs))


class HedgeBotTUI(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [Binding("q", "quit", "Quit")]

    async def action_quit(self) -> None:
        self.exit()

    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.graph_reserve = LineGraphWidget("WETH in Pool", "green")
        self.graph_short = LineGraphWidget("Short Position on Binance", "red")
        self.status_panel = HedgeStatus()
        self.log_panel = LogViewer()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical():
                yield self.graph_reserve
                yield self.graph_short
            with Vertical():
                yield Static("[b]Status", id="status-title")
                yield self.status_panel
                yield Static("[b]Logs", id="log-title")
                yield self.log_panel
        yield Footer()

    async def on_mount(self):
        async def poll_data():
            async for snapshot in self.simulator.generate_snapshots():
                ts = snapshot.timestamp.strftime('%H:%M:%S')
                self.status_panel.update_status(snapshot)
                self.graph_reserve.update_data(ts, snapshot.reserve_token1)
                self.graph_short.update_data(ts, snapshot.short_position_size)
                self.log_panel.log(
                    f"[POSITION_POLLING] USDC: {snapshot.reserve_token0:.2f}, WETH: {snapshot.reserve_token1:.4f}, Short: {snapshot.short_position_size:.4f}"
                )
                await asyncio.sleep(0.1)

        self.set_interval(0.5, lambda: None)  # allow UI refresh
        self.run_worker(poll_data, exclusive=True)


if __name__ == "__main__":
    from data_simulator import SnapshotSimulator
    sim = SnapshotSimulator()
    app = HedgeBotTUI(sim)
    app.run()
