import logging
from src.config import RISK_PER_TRADE

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExecutionEngine:
    def __init__(self, initial_balance=10000):
        self.balance = initial_balance
        self.open_position = None

    def check_signals(self, df):
        """Checks for EMA crossover signals."""
        if len(df) < 2: 
            return None
            
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        # Bullish Crossover (Fast crosses above Slow)
        if prev['ema_fast'] <= prev['ema_slow'] and curr['ema_fast'] > curr['ema_slow']:
            return 'BUY'
        # Bearish Crossover (Fast crosses below Slow)
        elif prev['ema_fast'] >= prev['ema_slow'] and curr['ema_fast'] < curr['ema_slow']:
            return 'SELL'
        return None

    def calculate_position(self, price, atr):
        """Calculates position size based on 1% risk rule."""
        risk_amount = self.balance * RISK_PER_TRADE
        sl_distance = 1.5 * atr  # 1.5x ATR stop-loss
        position_size = risk_amount / sl_distance
        return position_size

    def execute_trade(self, signal, df):
        """Executes or manages paper-traded positions."""
        row = df.iloc[-1]
        price = row['close']
        atr = row['atr']
        
        # Manage existing position
        if self.open_position:
            if self.open_position['type'] == 'LONG':
                if price <= self.open_position['sl'] or price >= self.open_position['tp']:
                    self.close_position(price)
            elif self.open_position['type'] == 'SHORT':
                if price >= self.open_position['sl'] or price <= self.open_position['tp']:
                    self.close_position(price)
            return

        # Open new position
        if not signal:
            return

        size = self.calculate_position(price, atr)
        
        if signal == 'BUY':
            self.open_position = {
                'type': 'LONG',
                'entry': price,
                'sl': price - (1.5 * atr),
                'tp': price + (3.0 * atr),
                'size': size
            }
            logger.info(f"OPEN LONG: Price={price:.2f}, SL={self.open_position['sl']:.2f}, TP={self.open_position['tp']:.2f}, Size={size:.4f}")
            
        elif signal == 'SELL':
            self.open_position = {
                'type': 'SHORT',
                'entry': price,
                'sl': price + (1.5 * atr),
                'tp': price - (3.0 * atr),
                'size': size
            }
            logger.info(f"OPEN SHORT: Price={price:.2f}, SL={self.open_position['sl']:.2f}, TP={self.open_position['tp']:.2f}, Size={size:.4f}")

    def close_position(self, price):
        """Logs the closure of a paper-traded position."""
        if self.open_position['type'] == 'LONG':
            pnl = (price - self.open_position['entry']) * self.open_position['size']
        else:
            pnl = (self.open_position['entry'] - price) * self.open_position['size']
        
        self.balance += pnl
        logger.info(f"CLOSE {self.open_position['type']}: Price={price:.2f}, PnL={pnl:.2f}, New Balance={self.balance:.2f}")
        self.open_position = None
