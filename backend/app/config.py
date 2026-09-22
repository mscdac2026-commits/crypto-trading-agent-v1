from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    trading_mode:str="paper"; live_trading_confirmation:str="NO"
    exchange_id:str="binance"; exchange_api_key:str=""; exchange_api_secret:str=""; exchange_password:str=""
    symbol:str="BTC/USDT"; timeframe:str="5m"; poll_seconds:int=20
    risk_per_trade:float=.005; max_position_pct:float=.10; max_daily_loss_pct:float=.02
    stop_loss_pct:float=.015; take_profit_pct:float=.03; min_signal_score:int=2
    paper_starting_cash:float=10000; cors_origins:str="http://localhost:5173"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    @property
    def live_enabled(self):
        return self.trading_mode.lower()=="live" and self.live_trading_confirmation=="I_UNDERSTAND_REAL_MONEY_IS_AT_RISK"
settings=Settings()
