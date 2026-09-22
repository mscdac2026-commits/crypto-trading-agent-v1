# Crypto Trading Agent V1

FastAPI + CCXT + React/TypeScript automated crypto trading agent.

## Safety defaults
Real exchange orders are locked by default. Start in paper mode. Use exchange API keys with withdrawal permission disabled.

## Run
```bash
cp .env.example .env
docker compose up --build
```
UI: http://localhost:5173
API: http://localhost:8000/docs

## Real-money activation
After testing, configure exchange credentials and explicitly set:
```env
TRADING_MODE=live
LIVE_TRADING_CONFIRMATION=I_UNDERSTAND_REAL_MONEY_IS_AT_RISK
```

V1 is long-only spot trading with one strategy position. Automated trading can lose money; no strategy guarantees profit.