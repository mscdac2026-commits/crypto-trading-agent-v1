import sqlite3,json
from pathlib import Path
from datetime import datetime,timezone
DB=Path("/app/data/trading.db")
if not DB.parent.exists(): DB=Path("data/trading.db")
DB.parent.mkdir(parents=True,exist_ok=True)
def conn():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init_db():
 with conn() as c:
  c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT,kind TEXT,payload TEXT)")
  c.execute("CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT,mode TEXT,symbol TEXT,side TEXT,amount REAL,price REAL,order_id TEXT UNIQUE,status TEXT)")
  c.execute("CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT)")
def event(kind,payload):
 with conn() as c:c.execute("INSERT INTO events(ts,kind,payload) VALUES(?,?,?)",(datetime.now(timezone.utc).isoformat(),kind,json.dumps(payload,default=str)))
def trade(mode,symbol,side,amount,price,order_id,status):
 with conn() as c:c.execute("INSERT OR IGNORE INTO trades(ts,mode,symbol,side,amount,price,order_id,status) VALUES(?,?,?,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),mode,symbol,side,amount,price,str(order_id or ""),status))
def recent_trades(n=100):
 with conn() as c:return [dict(x) for x in c.execute("SELECT * FROM trades ORDER BY id DESC LIMIT ?",(n,))]
def set_state(k,v):
 with conn() as c:c.execute("INSERT INTO state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(k,json.dumps(v)))
def get_state(k,default=None):
 with conn() as c:
  r=c.execute("SELECT value FROM state WHERE key=?",(k,)).fetchone()
  return json.loads(r["value"]) if r else default
