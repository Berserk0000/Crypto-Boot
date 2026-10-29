import asyncio
import ccxt.async_support as ccxt  # Use standard async CCXT instead of pro
import pandas as pd
import pandas_ta as ta

class DataEngine:
    def __init__(self, exchange_id='binance', symbol='BTC/USDT', timeframe='15m'):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'enableRateLimit': True,
        })
        # Enable sandbox/testnet if needed
        if self.exchange.urls.get('test'):
            self.exchange.set_sandbox_mode(True)
            
        self.symbol = symbol
        self.timeframe = timeframe

    async def fetch_latest_candles(self, limit=100):
        ohlcv = await self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calculate indicators safely on closed candles
        df['fast_ema'] = ta.ema(df['close'], length=9)
        df['slow_ema'] = ta.ema(df['close'], length=21)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        return df

    async def close(self):
        await self.exchange.close()
