import sqlite3,json
from pathlib import Path
from datetime import datetime,timezone
DB=Path("/app/data/trading.db")
if not DB.parent.exists(): DB=Path("data/trading.db")
DB.parent.mkdir(parents=True,exist_ok=True)
def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT,kind TEXT,payload TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT,mode TEXT,symbol TEXT,side TEXT,amount REAL,price REAL,order_id TEXT,status TEXT)")
def event(kind,payload):
    with sqlite3.connect(DB) as c:c.execute("INSERT INTO events(ts,kind,payload) VALUES(?,?,?)",(datetime.now(timezone.utc).isoformat(),kind,json.dumps(payload,default=str)))
def trade(mode,symbol,side,amount,price,order_id,status):
    with sqlite3.connect(DB) as c:c.execute("INSERT INTO trades(ts,mode,symbol,side,amount,price,order_id,status) VALUES(?,?,?,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),mode,symbol,side,amount,price,str(order_id or ""),status))
def recent_trades(n=100):
    with sqlite3.connect(DB) as c:
        c.row_factory=sqlite3.Row
        return [dict(x) for x in c.execute("SELECT * FROM trades ORDER BY id DESC LIMIT ?",(n,)).fetchall()]
