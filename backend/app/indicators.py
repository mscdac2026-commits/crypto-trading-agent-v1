import pandas as pd
def analyze(ohlcv):
    d=pd.DataFrame(ohlcv,columns=["ts","open","high","low","close","volume"]); c=d.close.astype(float)
    d["ef"]=c.ewm(span=9,adjust=False).mean(); d["es"]=c.ewm(span=21,adjust=False).mean()
    delta=c.diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=(-delta.clip(upper=0)).rolling(14).mean()
    d["rsi"]=(100-100/(1+gain/loss.replace(0,float("nan")))).fillna(50)
    m=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean(); d["m"]=m; d["ms"]=m.ewm(span=9,adjust=False).mean()
    r=d.iloc[-1]; score=0; why=[]
    if r.ef>r.es: score+=1; why.append("EMA bullish")
    else: score-=1; why.append("EMA bearish")
    if r.rsi<35: score+=1; why.append("RSI oversold")
    elif r.rsi>70: score-=1; why.append("RSI overbought")
    if r.m>r.ms: score+=1; why.append("MACD bullish")
    else: score-=1; why.append("MACD bearish")
    return {"price":float(r.close),"ema_fast":float(r.ef),"ema_slow":float(r.es),"rsi":float(r.rsi),"macd":float(r.m),"macd_signal":float(r.ms),"score":int(score),"reasons":why}
