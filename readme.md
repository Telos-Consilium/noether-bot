# EulerSwap Hackathon: Delta Neutral Hedging Bot Technical Documentation

## Background

EulerSwap is a recently launched DeFi protocol that offers a native swapping layer tightly integrated with Euler’s lending vaults. Unlike traditional DEXes, EulerSwap enables JIT (Just-In-Time) liquidity, allowing sophisticated pool operators to dynamically borrow and supply tokens precisely when a trade occurs.

At the heart of this architecture is the ability for pool operators to borrow assets on the fly from Euler’s lending markets and temporarily provide them to the swap pool, earning both swap fees and lending interest in the process. This opens up powerful new strategies for capital-efficient liquidity provisioning.

One of the most compelling use cases enabled by this model is the ability to tap into the high yields of volatile trading pairs like USDT/WETH without being directly exposed to the price fluctuations of WETH—and thus avoiding impermanent loss. Because liquidity is provided dynamically and for a very short duration, operators can benefit from the elevated fee environment of such pairs while maintaining a stable exposure, making this an attractive opportunity for risk-conscious liquidity managers.

In this specific setup, the pool operator owns USDT and wants to:
	
	•	Provide JIT liquidity for WETH-USDT swaps,
	•	Earn swap fees from traders interacting with the pool,
	•	Simultaneously earn lending yields from Euler’s USDT vault,
	•	Avoid price exposure to WETH entirely.

To enable this, the operator borrows WETH from EulerVault whenever a trader initiates a WETH-to-USDT swap. After the swap, the pool holds WETH—which exposes the operator to market risk. To neutralize this risk, the operator opens a short WETH position of equivalent size on an off-chain venue like Binance Perpetuals.

Maintaining delta neutrality is crucial. Without it, price fluctuations in WETH can lead to impermanent loss or directional exposure the operator does not want. This is where NoETHerBot comes in. Additionally, NoETHerBot achieves another desirable arbitrage by leveraging the difference between the low cost of borrowing WETH (2.5% as of June 2025) and the higher yield from going short ETH (8.3%), further enhancing profitability and efficiency.

### Why This Bot

This project provides a modular, extensible python framework that automates the risk management lifecycle for EulerSwap JIT pool operators. The bot continuously:
	
	•	Monitors on-chain reserves using getReserves() via RPC polling,
	•	Tracks off-chain short positions,
	•	Calculates the net delta exposure,
	•	Executes hedge trades (short/cover) if delta exceeds a configurable threshold,
	•	Maintains logs and live visualization in a terminal ui dashboard.

By automating hedging, pool operators can focus on strategy design and liquidity management—while the bot handles the grunt work of staying neutral in real-time.

## Overview

A Python framework for automated delta-neutral strategies on EulerSwap, specifically designed for USDC/WETH pools. The framework constantly monitors the pool status, and automatically hedges ETH exposure on CEX to maintain delta neutrality

![Screenshot 2025-07-02 at 6.52.53 PM.png](EulerSwap%20Hackathon%20Delta%20Neutral%20Hedging%20Bot%20Tech%202246da066a74800d9899e1370c9f1068/Screenshot_2025-07-02_at_6.52.53_PM.png)

The frontend of this bot is a functional Terminal UI (TUI) which makes it very convenient to see the status of your positions, monitor bot hedging and trades, and keep an eye on risk parameters and on-chain metadata

## Architecture Diagram

```jsx
┌──────────────────────┐    ┌─────────────────────┐    ┌────────────────────┐
│     SwapMonitor      │───▶│   StrategyEngine    │───▶│    RiskManager     │
│                      │    │                     │    │                    │
│ - RPC Polling (get)  │    │ - Hedge Logic       │    │ - Risk Checks      │
│ - Reserve Snapshot   │    │ - Delta Calculation │    │ - Slippage Limits  │
│ - Emits Snapshots    │    │ - Threshold Mgmt    │    │ - Exchange Choice  │
└──────────────────────┘    └─────────────────────┘    └────────────────────┘
           │                          │                          │
           │                          ▼                          ▼
           │                ┌────────────────────┐    ┌────────────────────┐
           │                │  PositionSnapshot  │    │  ExchangeManager   │
           │                │                    │    │                    │
           │                │ - USDC/WETH State  │    │ - IExchange Impl   │
           │                │ - Short Positions  │    │ - Binance API      │
           │                │ - Timestamps       │    │ - Order Execution  │
           │                └────────────────────┘    └────────────────────┘
           │                          │                          │
           ▼                          ▼                          ▼
┌──────────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│   DatabaseManager    │◀───┤    ConfigManager   │    │    LoggerManager   │
│                      │    │                    │    │                    │
│ - SQLite Storage     │    │ - Strategy Params  │    │ - RichLog to TUI   │
│ - Snapshots + PnL    │    │ - ABI / RPC / Keys │    │ - Alerts / Tags    │
│ - Historical Access  │    │ - Pool Address Info│    │ - Time-stamped     │
└──────────────────────┘    └────────────────────┘    └────────────────────┘
```

## Project Structure

```jsx
eulerswap-hackathon/
├── abi/                           # Contract ABIs
├── config/                        # Configuration manager
├── database_manager/              # SQLite / DB interface
├── exchange_manager/              # Perpetual exchange (e.g., Binance) interface
├── logger_manager/                # Log persistence and pretty display
├── models/                        # Data models (e.g., PositionSnapshot)
├── risk_manager/                  # Risk logic (limits, validation)
├── strategy_engine/               # Core hedging logic
├── swap_monitor/                  # On-chain reserve monitor via RPC
├── tui/                           # Textual TUI built with textual + plotext
└── main.py                        # Non TUI Entrypoint (optional)
```

## Installation

### Prerequisites

- Python 3.11+
- `poetry`

### Steps

1. Clone the repository
2. Install Dependencies:
```bash
poetry install
```
3. **Configure Environment Variables**
    - Create a .env file in the root of the project:
    `touch .env`  or modify and rename and `.env.sample`  file

    The following environment variables must be present in the `.env` file:

    ```bash
    BINANCE_API_KEY=your_binance_api_key
    BINANCE_API_SECRET=your_binance_api_secret
    RPC_URL=https://your_rpc_url
    EULERSWAP_POOL=0xYourEulerSwapPoolAddress
    ```


### How to run the bot TUI

```bash
PYTHONPATH=. poetry run python tui/hedge_tui.py
```

This will launch a real-time interface that:

- Polls on-chain data
- Executes strategy decisions
- Renders logs and visual plots
- Displays config info

To close the bot, just press the `q` key

## TUI Interface

![Screenshot 2025-07-02 at 6.52.53 PM.png](EulerSwap%20Hackathon%20Delta%20Neutral%20Hedging%20Bot%20Tech%202246da066a74800d9899e1370c9f1068/Screenshot_2025-07-02_at_6.52.53_PM.png)

Through this terminal UI, a pool operator can get a very functional at-a-glance information of all the important parameters related to position, exposure, hedging as well as being able to conveniently monitor the trades executed by the bot

The left pain contains two graphs:

- WETH reserve in the EulerSwap pool plotted over time, with updates every five seconds
- Size of ETHUSDT Perpetual on Binance Perpetuals Exchange in the same timestamp

These graphs give an at-a-glance idea of the WETH exposure of the pool operator

**Current Position Snapshot**

This section contains information of the latest snapshot of the current reserves in the pool as well as the the WETH Short Position

**Hedge Strategy:**

This section contains information regarding the hedge strategy parameters (such as minimum hedge size for which a trade will be executed) as well as related metadata

**Logs:**

At every polling interval of 5 seconds, the following metrics are logged:

- Position Polling: Snapshot of latest fetched position
- Calculated Hedge: The hedge that is computed by the Strategy Engine
- Leverage: Leverage that is pre-configured/computed by the RiskManager
- Close Short Position/Open Short Position: Based on whether the calculated hedge is positive or negative, it either opens a short position on the ETHUSDT perpetual or closes the short position

# Data Flow

The hedge bot operates on a simple feedback loop powered by live data from the on-chain pool and off-chain exchanges. Below is a walkthrough of the **data flow** using two simulated snapshots.

1. **Polling via RPCSwapMonitor**
    - The bot periodically calls getReserves() from the EulerSwap pool smart contract.
    - Simultaneously, it fetches the current short position from Binance via CCXT.
2. **Snapshot Creation**
    - The raw values are structured into a PositionSnapshot, containing:
        - reserve_token0: USDC reserve in pool
        - reserve_token1: WETH reserve in pool
        - short_position_size: Short position on Binance
        - timestamp: Snapshot timestamp
3. **Strategy Engine Analysis**
    - The snapshot is passed to StrategyEngine.
    - It calculates the **delta** (difference) between reserve_token1 and the current short position.
    - If the delta crosses a configurable threshold, the engine decides to **hedge**.
4. **Risk Check & Execution**
    - RiskManager determines leverage (e.g., 1x).
    - Based on delta sign:
        - If **positive**, the bot opens a short on Binance.
        - If **negative**, it closes a portion of the existing short.
    - The trade is executed via the Binance API wrapper.
5. **Persistence & Logging**
    - The executed trade is saved as a HedgeSnapshot in memory (or database if extended).
    - A detailed log is generated and displayed in the TUI.

## Core Components

### PositionSnapshot Model

Model that captures the entire position snapshot for the operator at a timestamp including the pool reserves and the short CEX position

Central model containing:

- reserve_token0 (USDC) in the EulerSwap pool
- reserve_token1 (WETH) in the EulerSwap pool
- short_position_size
- timestamp

 

### RPCSwapMonitor

RPCSwapMonitor is the component responsible for querying the on-chain state of the EulerSwap liquidity pool using an Ethereum RPC node. It periodically fetches reserve data from the smart contract and combines it with the current perpetual short position (fetched from the exchange) to produce a unified PositionSnapshot object.

This snapshot is then saved to the database and optionally streamed to any subscribed consumers (e.g., the StrategyEngine or TUI display).

### Responsibilities

- Connects to an on-chain smart contract via a JSON-RPC provider.
- Periodically polls the getReserves() method from the smart contract.
- Fetches the current short position from a centralized exchange via the IExchange interface.
- Emits a complete PositionSnapshot (USDC reserves, WETH reserves, short position, timestamp).
- Stores the snapshot to db via DatabaseManager.
- Provides callback subscription support for real-time consumers.
- Exposes an optional fetch_snapshot() method for on-demand snapshot access.

### Data Flow

1. getReserves() → Gets on-chain token0/token1 balances (USDC/WETH).
2. exchange.get_current_perpetual_position() → Gets current short size from exchange (e.g., Binance).
3. Constructs a PositionSnapshot.
4. Logs snapshot.
5. Stores snapshot to SQLite.
6. Emits snapshot via callback (if set).

---

### Constructor

```python
def __init__(
    rpc_url: str,
    abi_path: str,
    exchange: IExchange,
    symbol_perpetual: str
)
```

- rpc_url: Ethereum node endpoint (e.g., Alchemy, Infura).
- abi_path: Filesystem path to the pool contract’s ABI JSON.
- exchange: Instance of a class implementing the IExchange interface.
- symbol_perpetual: e.g., "ETH/USDT", passed to the exchange to fetch short position size.

---

## Strategy Engine

The StrategyEngine is the core decision-making unit of the bot. It ingests the latest PositionSnapshot from the on-chain pool and the centralized exchange, and determines whether a hedge operation is required. If conditions are met, it places a hedging trade using the configured exchange (e.g., Binance).

### Responsibilities

- Compute delta between on-chain WETH reserves and existing short positions.
- Decide whether a hedge action should be taken based on minimum thresholds.
- Compute leverage through the RiskManager.
- Execute short or close orders on a perpetual exchange.
- Log key decisions and events.
- Persist hedging operations to the database for auditing.

### Example Flow

Let’s say:

- Pool has 0.10 WETH.
- Current short position is 0.05 WETH.

Then, `delta = 0.10 - 0.05 = 0.05`

Since this exceeds the 0.005 threshold:

- A short order of 0.05 WETH will be placed.
- Leverage is fetched.
- Order is sent to Binance.
- Event is logged and stored.

### Exchange Used

- Set to "ETH/USDT:USDT" (Binance Futures format).
- Fetched via ConfigManager.get_exchange().

### Logs Produced

- [CALCULATED_HEDGE] — logs the computed delta.
- [LEVERAGE] — logs leverage used for the trade.
- [OPEN_SHORT_POSITION] or [CLOSE_SHORT_POSITION] — logs the exact trade data sent to the exchange.

## IExchange

The IExchange is an abstract base class that defines the contract for any exchange implementation used in the bot (e.g., Binance, OKX, Bybit).

It standardizes:

- Price fetching
- Funding rate access
- Short/close order execution
- Position querying
- Cleanup routines

This abstraction allows the bot to easily swap out exchange backends with minimal code changes. New exchanges can be added simply by implementing IExchange

## BinanceExchange

BinanceExchange is the implementation of IExchange using Binance Perpetual Futures via ccxt.async_support.

### Key Characteristics:

- Uses Binance Futures API
- Handles:
    - Fetching mark prices and funding rates
    - Executing market short and buy orders
    - Querying current perpetual positions
    - Managing leverage settings

## Risk Manager

This class contains all risk related logic based on the the positions and market conditions.



RiskManager is queried by the StrategyEngine whenever a hedge needs to be executed. It contains the logic for computations for things like:

- What leverage should be used for this trade?
- Are current market conditions safe to hedge?
- Should this trade be avoided due to slippage or volatility?

Currently it is very minimal but the idea is for all risk-related logic to be here and easily integrate with the `Strategy Engine`

The ConfigManager is the central configuration layer of the bot, responsible for managing all runtime parameters, credentials, and exchange connections. It abstracts away environment-specific setup and provides a unified interface to access configuration data throughout the application.

## Config Manager

The ConfigManager is the central configuration layer of the bot, responsible for managing all runtime parameters, credentials, and exchange connections. It abstracts away environment-specific setup and provides a unified interface to access configuration data throughout the application.

- Manages strategy and risk parameters.
- Load sAPI credentials securely via .env using python-dotenv.
- Provides pre-configured exchange instances (e.g., Binance).
- Exposes chain-level metadata (e.g., pool address, RPC endpoint).
- Allows runtime configuration updates for dynamic strategies.

## Logger Manager

The LoggerManager is a lightweight centralized logging utility used across the bot to record events related to position polling, hedge execution, leverage, and exchange orders. It maintains an in-memory list of log entries and formats logs in a consistent, styled manner compatible with the TUI display. While it stores log in-memory now it can be easily extended to integrate with a db

Each log is prepended with:

- A bold green tag (e.g., [POSITION_POLLING])
- A human-readable message
- A timestamp (in ISO 8601 UTC format, internally)

## Database Manager

The DatabaseManager is an in-memory persistence layer responsible for storing and retrieving all critical snapshots generated by the bot, including:

- PositionSnapshots: Representing on-chain and account positions at specific times.
- HedgeSnapshots: Representing hedge trades executed on an exchange.

It enables other components (like the TUI, Strategy Engine, or analytics tools) to access both real-time and historical bot state.

Currently, it uses lists to store data in memory, but can be easily integrated with a db. The rest of the codebase interacts with the exposed functions here, so there would be no changes required in any other part of the codebase on switching db methods

# Terminal Frontend UI Spec

The TUI for this bot is a terminal-based dashboard built using [Textual](https://textual.textualize.io/) that provides a **real-time visual and interactive interface** to monitor and interact with the EulerSwap hedging bot. It combines data polling, strategy execution, plotting, and log inspection in one responsive UI.

- Fetch and display live data from the on-chain EulerSwap pool via RPCSwapMonitor.
- Forward snapshots to StrategyEngine for hedging decisions.
- Visualize WETH reserves and short positions over time using PlotextPlot.
- Display logs, config, and runtime status in the terminal.
- Support real-time log updates and snapshot visualizations.
- Handle keyboard shortcuts and clean shutdown.

---

### **Main Components**

| **Component** | **Description** |
| --- | --- |
| **HedgeStatus** | Renders the current position snapshot (USDC, WETH, short size, timestamp). |
| **ConfigStatus** | Displays current strategy/risk config like min hedge size, pool address, etc. |
| **RichLog** | Scrollable, color-formatted terminal log for strategy decisions and errors. |
| **WETH Plot** | Line + scatter plot of on-chain WETH reserves. |
| **Short Plot** | Line + scatter plot of exchange short position size. |

### **Polling Logic**

Runs inside a background coroutine (poller):

1. Fetches a snapshot via RPCSwapMonitor.fetch_snapshot().
2. Logs and forwards it to StrategyEngine.process_position_snapshot().
3. Updates PlotextPlot graphs with historical data.
4. Refreshes HedgeStatus, ConfigStatus, and RichLog.
5. Retains only last 50 points for performance.

**Key Bindings**

| **Key** | **Action** |
| --- | --- |
| q | Quit application |
