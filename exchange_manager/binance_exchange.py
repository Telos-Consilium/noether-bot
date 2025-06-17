import aiohttp

class BinanceExchange:
    BASE_URL = "https://fapi.binance.com"

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
