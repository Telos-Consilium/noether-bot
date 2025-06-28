# tui/graph_widget.py

from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text

class LineGraphWidget(Widget):
    def __init__(self, title: str, color: str = "green", max_points: int = 30):
        super().__init__()
        self.title = title
        self.color = color
        self.max_points = max_points
        self.data_points = []

    def update_data(self, label: str, value: float):
        self.data_points.append(value)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        self.refresh()

    def render(self) -> Text:
        if not self.data_points:
            return Text("No data yet", style="dim")

        max_val = max(self.data_points)
        min_val = min(self.data_points)
        range_val = max_val - min_val or 1e-6
        height = 10  # number of text rows for vertical space

        # build graph grid
        grid = [[" " for _ in range(len(self.data_points))] for _ in range(height)]

        for i, val in enumerate(self.data_points):
            bar_height = int((val - min_val) / range_val * (height - 1))
            grid[height - 1 - bar_height][i] = "•"

        lines = [Text("".join(row), style=self.color) for row in grid]
        header = Text(self.title, style="bold underline")
        return Text("\n").join([header] + lines)
