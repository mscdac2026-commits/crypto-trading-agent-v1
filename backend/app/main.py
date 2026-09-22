import asyncio,secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI,Header,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .engine import Engine
from .db import init_db,recent_trades
engine=Engine(); task=None
def authorize(authorization:str|None):
    expected="Bearer "+settings.control_api_token
    if settings.control_api_token=="CHANGE_ME_BEFORE_DEPLOYMENT" or not authorization or not secrets.compare_digest(authorization,expected):
        raise HTTPException(status_code=401,detail="Unauthorized control action")
@asynccontextmanager
async def lifespan(app):
    global task
    init_db(); task=asyncio.create_task(engine.start()); yield
    engine.running=False
    if task: task.cancel()
    await engine.x.close()
app=FastAPI(title="Crypto Trading Agent V1",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.get("/api/health")
def health():return {"ok":True}
@app.get("/api/status")
def status():return engine.status()
@app.get("/api/trades")
def trades():return recent_trades()
@app.post("/api/kill")
async def kill(authorization:str|None=Header(default=None)):
    authorize(authorization);await engine.kill();return {"ok":True}
@app.post("/api/resume")
def resume(authorization:str|None=Header(default=None)):
    authorize(authorization);engine.resume();return {"ok":True}
