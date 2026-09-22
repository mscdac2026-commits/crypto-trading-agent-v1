import asyncio
from datetime import datetime,timezone
from .config import settings
from .exchange import Exchange
from .indicators import analyze
from .db import event,trade,get_state,set_state
class Engine:
 def __init__(self):
  self.x=Exchange();self.running=False;self.killed=False;self.last={};self.position=None;self.cash=settings.paper_starting_cash;self.day_start=self.cash;self.day=datetime.now(timezone.utc).date().isoformat();self.realized=0.;self.lock=asyncio.Lock()
 def save(self):set_state("engine",{"position":self.position,"cash":self.cash,"day_start":self.day_start,"day":self.day,"realized":self.realized,"killed":self.killed})
 def restore(self):
  s=get_state("engine",{});self.position=s.get("position");self.cash=s.get("cash",self.cash);self.day_start=s.get("day_start",self.cash);self.day=s.get("day",self.day);self.realized=s.get("realized",0.);self.killed=s.get("killed",False)
 def equity(self,p):return self.cash+(self.position["amount"]*p if self.position else 0)
 def reset_day(self,p):
  today=datetime.now(timezone.utc).date().isoformat()
  if today!=self.day:self.day=today;self.day_start=self.equity(p);self.save()
 def risk_blocked(self,p):return max(0,self.day_start-self.equity(p))>=self.day_start*settings.max_daily_loss_pct
 def paper_size(self,p):
  eq=self.equity(p);return max(0,min(eq*settings.risk_per_trade/max(p*settings.stop_loss_pct,1e-9),eq*settings.max_position_pct/p))
 async def live_size(self,p):
  b=await self.x.balance();q=settings.symbol.split("/")[1];free=float((b.get("free") or {}).get(q) or 0);return max(0,min(free*settings.risk_per_trade/max(p*settings.stop_loss_pct,1e-9),free*settings.max_position_pct/p))
 async def start(self):
  await self.x.load();self.restore()
  if settings.live_enabled:
   asset=await self.x.reconcile_asset()
   if asset>0 and not self.position:self.killed=True;event("reconcile",{"status":"manual_review_required","exchange_asset":asset});self.save()
  self.running=True;event("engine",{"status":"started","live":settings.live_enabled})
  while self.running:
   try:await self.tick()
   except Exception as e:event("error",{"message":str(e)})
   await asyncio.sleep(settings.poll_seconds)
 async def tick(self):
  async with self.lock:
   s=analyze(await self.x.candles());self.last=s;p=s["price"];self.reset_day(p)
   if self.killed or self.risk_blocked(p):return
   if self.position:
    z=self.position
    if p<=z["stop"] or p>=z["take"] or s["score"]<=-settings.min_signal_score:await self.sell(p)
   elif s["score"]>=settings.min_signal_score:await self.buy(p)
 async def buy(self,p):
  a=await self.live_size(p) if settings.live_enabled else self.paper_size(p)
  if a<=0:return
  if settings.live_enabled:o=await self.x.market_order("buy",a,p);oid=o.get("id");st=o.get("status","submitted")
  else:
   if a*p>self.cash:return
   self.cash-=a*p;oid=f"paper-buy-{datetime.now(timezone.utc).timestamp()}";st="filled"
  self.position={"amount":a,"entry":p,"stop":p*(1-settings.stop_loss_pct),"take":p*(1+settings.take_profit_pct)};trade(settings.trading_mode,settings.symbol,"buy",a,p,oid,st);self.save()
 async def sell(self,p):
  z=self.position
  if not z:return
  a=z["amount"]
  if settings.live_enabled:o=await self.x.market_order("sell",a,p);oid=o.get("id");st=o.get("status","submitted")
  else:self.cash+=a*p;self.realized+=(p-z["entry"])*a;oid=f"paper-sell-{datetime.now(timezone.utc).timestamp()}";st="filled"
  trade(settings.trading_mode,settings.symbol,"sell",a,p,oid,st);self.position=None;self.save()
 async def kill(self):self.killed=True;self.save();event("kill",{"enabled":True})
 def resume(self):self.killed=False;self.save();event("kill",{"enabled":False})
 def status(self):
  p=self.last.get("price",0);return {"running":self.running,"killed":self.killed,"configured_mode":settings.trading_mode,"live_orders_enabled":settings.live_enabled,"exchange":settings.exchange_id,"symbol":settings.symbol,"timeframe":settings.timeframe,"signal":self.last,"position":self.position,"paper_cash":self.cash,"paper_equity":self.equity(p) if p else self.cash,"realized_pnl":self.realized,"daily_loss_blocked":self.risk_blocked(p) if p else False}
