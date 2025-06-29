# tui/graph_widget.py

from textual.widgets import Static
import plotext as plt
from datetime import datetime


class LineGraphWidget(Static):
    def __init__(self, title: str, color: str = "white"):
        super().__init__()
        self.title = title
        self.color = color
        self.timestamps = []  # datetime objects
        self.values = []
        self.max_points = 30

    def update_data(self, timestamp: datetime, value: float):
        self.timestamps.append(timestamp)
        self.values.append(value)

        if len(self.timestamps) > self.max_points:
            self.timestamps.pop(0)
            self.values.pop(0)

        self.refresh()

    def render(self) -> str:
        if not self.values:
            return "Loading..."

        try:
            plt.clear_data()
            plt.theme("dark")
            plt.plot_size(40, 10)
            plt.date_form("H:M:S")  # show time only
            plt.title(self.title)
            plt.plot_date(self.timestamps, self.values, marker="dot", color=self.color, label=self.title)
            return plt.build()
        except Exception as e:
            return f"[Graph Error: {e}]"
