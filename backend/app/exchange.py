import asyncio,ccxt.async_support as ccxt
from .config import settings
class Exchange:
 def __init__(self):
  cls=getattr(ccxt,settings.exchange_id);cfg={"enableRateLimit":True,"timeout":15000}
  if settings.exchange_api_key:
   cfg.update(apiKey=settings.exchange_api_key,secret=settings.exchange_api_secret)
   if settings.exchange_password:cfg["password"]=settings.exchange_password
  self.client=cls(cfg);self.market=None
 async def retry(self,fn,*args):
  last=None
  for delay in (0,1,2,4):
   if delay:await asyncio.sleep(delay)
   try:return await fn(*args)
   except (ccxt.NetworkError,ccxt.RequestTimeout) as e:last=e
  raise last
 async def load(self):
  m=await self.retry(self.client.load_markets)
  if settings.symbol not in m:raise RuntimeError(f"{settings.symbol} unavailable on {settings.exchange_id}")
  self.market=m[settings.symbol]
 async def candles(self):return await self.retry(self.client.fetch_ohlcv,settings.symbol,settings.timeframe,None,150)
 async def balance(self):return await self.retry(self.client.fetch_balance)
 def validate_amount(self,amount,price):
  amount=float(self.client.amount_to_precision(settings.symbol,amount));lim=(self.market or {}).get("limits") or {}
  amin=((lim.get("amount") or {}).get("min"));cmin=((lim.get("cost") or {}).get("min"))
  if amount<=0 or (amin and amount<amin) or (cmin and amount*price<cmin):raise RuntimeError("Order below exchange minimum/precision requirements")
  return amount
 async def market_order(self,side,amount,price):
  if not settings.live_enabled:raise RuntimeError("REAL ORDER BLOCKED: explicit live confirmation missing")
  amount=self.validate_amount(amount,price)
  return await self.client.create_order(settings.symbol,"market",side,amount)
 async def reconcile_asset(self):
  b=await self.balance();base=settings.symbol.split("/")[0];return float((b.get("total") or {}).get(base) or 0)
 async def close(self):await self.client.close()
