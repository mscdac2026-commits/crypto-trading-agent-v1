import ccxt.async_support as ccxt
from .config import settings
class Exchange:
    def __init__(self):
        cls=getattr(ccxt,settings.exchange_id); cfg={"enableRateLimit":True}
        if settings.exchange_api_key:
            cfg.update(apiKey=settings.exchange_api_key,secret=settings.exchange_api_secret)
            if settings.exchange_password: cfg["password"]=settings.exchange_password
        self.client=cls(cfg)
    async def load(self):
        m=await self.client.load_markets()
        if settings.symbol not in m: raise RuntimeError(f"{settings.symbol} unavailable on {settings.exchange_id}")
    async def candles(self): return await self.client.fetch_ohlcv(settings.symbol,settings.timeframe,limit=150)
    async def balance(self): return await self.client.fetch_balance()
    async def market_order(self,side,amount):
        if not settings.live_enabled: raise RuntimeError("REAL ORDER BLOCKED: explicit live confirmation missing")
        amount=float(self.client.amount_to_precision(settings.symbol,amount))
        if amount<=0: raise RuntimeError("Order amount rounded to zero")
        return await self.client.create_order(settings.symbol,"market",side,amount)
    async def close(self): await self.client.close()
