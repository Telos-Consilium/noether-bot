# tui/hedge_tui.py
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.binding import Binding
from textual_plotext import PlotextPlot
from datetime import datetime
from models.position_snapshot import PositionSnapshot
import asyncio
import numpy as np
import time

class HedgeStatus(Static):
    def update_status(self, s: PositionSnapshot):
        self.update(
            f"[b]USDC:[/b] {s.reserve_token0:.2f}\n"
            f"[b]WETH in Pool:[/b] {s.reserve_token1:.4f}\n"
            f"[b]WETH Short Pos:[/b] {s.short_position_size:.4f}\n"
            f"[b]Timestamp:[/b] {s.timestamp.strftime('%H:%M:%S')}"
        )

class LogViewer(Static):
    def __init__(self):
        super().__init__()
        self.logs = []

    def log(self, msg: str):
        ts = datetime.now().strftime('%H:%M:%S')
        self.logs.append(f"[{ts}] {msg}")
        if len(self.logs) > 30:
            self.logs.pop(0)
        self.update("\n".join(self.logs))

class HedgeBotTUI(App):
    BINDINGS = [Binding("q", "quit", "Quit")]
    CSS_PATH = 'styles.tcss'

    def __init__(self, simulator):
        super().__init__()
        self.sim = simulator
        self.status = HedgeStatus()
        self.logs = LogViewer()

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
                yield Static("[b]Current Position Snapshot[/b]")
                yield self.status
                yield Static("[b]Logs[/b]")
                yield self.logs
        yield Footer()

    async def on_mount(self):
        self.res_x, self.res_y = [], []
        self.short_x, self.short_y = [], []
        self.start_time = time.time()

        async def poller():
            # Get references to both plots
            weth_plot = self.query_one("#weth_plot", PlotextPlot)
            short_plot = self.query_one("#short_plot", PlotextPlot)

            counter = 0
            while True:
                # Simulate time-based data
                current_time = time.time()

                # Generate simulated WETH reserve data (sinusoidal with noise)
                weth_reserve = 10 + 2 * np.sin(current_time * 0.5) + 0.5 * np.random.randn()

                # Generate simulated short position data (different pattern)
                short_position = 5 + 1.5 * np.cos(current_time * 0.3) + 0.3 * np.random.randn()

                # Store data points
                self.res_x.append(current_time)
                self.res_y.append(weth_reserve)
                self.short_x.append(current_time)
                self.short_y.append(short_position)

                # Update WETH reserve plot
                weth_plot.plt.clear_data()
                weth_plot.plt.scatter(self.res_x, self.res_y, marker="dot")
                weth_plot.plt.plot(self.res_x, self.res_y, color="green")
                weth_plot.plt.title("WETH Reserve in Pool")
                weth_plot.plt.xlabel("Time (seconds)")
                weth_plot.plt.ylabel("WETH Reserve")

                # Update Short position plot
                short_plot.plt.clear_data()
                short_plot.plt.scatter(self.short_x, self.short_y, marker="dot")
                short_plot.plt.plot(self.short_x, self.short_y, color="red")
                short_plot.plt.title("ETHUSDT Perpetual")
                short_plot.plt.xlabel("Time (seconds)")
                short_plot.plt.ylabel("Short Position Size")

                # Refresh the plots
                weth_plot.refresh()
                short_plot.refresh()

                # Create a simulated snapshot for status update
                simulated_snapshot = type('obj', (object,), {
                    'reserve_token0': 1000 + 100 * np.random.randn(),
                    'reserve_token1': weth_reserve,
                    'short_position_size': short_position,
                    'timestamp': datetime.now()
                })

                # Update status and logs
                self.status.update_status(simulated_snapshot)
                self.logs.log(
                    f"RESERVE {weth_reserve:.4f}, SHORT {short_position:.4f}"
                )

                # Keep only last 50 data points for performance
                if len(self.res_x) > 50:
                    self.res_x.pop(0)
                    self.res_y.pop(0)
                    self.short_x.pop(0)
                    self.short_y.pop(0)

                counter += 1
                await asyncio.sleep(5)  # Poll every second for demo purposes

        # Start the poller as a background task
        self.run_worker(poller, exclusive=True)

if __name__ == "__main__":
    from data_simulator import SnapshotSimulator
    sim = SnapshotSimulator()
    HedgeBotTUI(sim).run()
