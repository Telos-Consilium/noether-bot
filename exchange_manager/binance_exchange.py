import aiohttp

from exchange_manager.exchange import IExchange
import ccxt.async_support as ccxt

class BinanceExchange(IExchange):
    BASE_URL = "https://fapi.binance.com"
    def __init__(self, api_key: str, api_secret: str):
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'},
            })
            self.exchange.set_sandbox_mode(True)

    async def get_current_price(self, symbol: str) -> float:
        """
        Fetches the current mark price (fair price) for a perpetual symbol like 'ETHUSDT'.
        """
        url = f"{self.BASE_URL}/fapi/v1/premiumIndex"
        params = {"symbol": symbol.upper()}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return float(data["markPrice"])

    async def get_funding_rate(self, symbol: str) -> float:
        """
        Fetches the most recent funding rate for a perpetual symbol like 'ETHUSDT'.
        """
        url = f"{self.BASE_URL}/fapi/v1/premiumIndex"
        params = {"symbol": symbol.upper()}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return float(data["lastFundingRate"])

    async def open_short_position(self, symbol: str, size: float, leverage: int):
        await self.exchange.load_markets()
        await self.exchange.set_leverage(leverage, symbol)
        order = await self.exchange.create_order(symbol, 'market', 'sell', size)
        return order

    async def close_position(self, symbol: str, size: float, leverage: int):
        await self.exchange.load_markets()
        await self.exchange.set_leverage(leverage, symbol)
        order = await self.exchange.create_order(symbol, 'market', 'buy', size)
        return order

    async def get_current_perpetual_position(self, symbol: str):
        await self.exchange.load_markets()
        positions = await self.exchange.fetch_positions([symbol])
        for position in positions:
               if position['symbol'] == symbol:
                   return float(str(position['contracts']))
        return 0.0


    async def close(self):
        await self.exchange.close()
