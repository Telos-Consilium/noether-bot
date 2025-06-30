## How to run the bot

### 1. Install Dependencies
`poetry` is the package manager used in this bot, and the dependencies can be installed through `poetry` after the repository is cloned

### 2. Setup .env variables
A sample list of env variables that the bot expects are present in the `.env.sample` file

### 3. Core Bot Execution
`main.py` contains code that can either simulate user positions and run all the bot actions, or run the actual RPC polling on a pool and then execute bot actions based on the commented/uncommented lines. Code for both the flows is present in `main.py`

To run, simply execute
```bash
poetry run python main.py
```

### 4. TUI Execution
Currently the TUI simulates the position data, and works on this data only to display charts and sample logs/metrics
In the current implementation the TUI should run even without .env variables being Setup

For now, to run the TUI just execute

```bash
PYTHONPATH=. poetry run python tui/hedge_tui.py
```
