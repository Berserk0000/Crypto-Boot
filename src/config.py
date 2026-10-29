import os
from dotenv import load_dotenv

load_dotenv()

# API Credentials
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_SECRET = os.getenv("BYBIT_SECRET")

# Testnet Flags
USE_BINANCE_TESTNET = os.getenv("USE_BINANCE_TESTNET", "True").lower() == "true"
USE_BYBIT_TESTNET = os.getenv("USE_BYBIT_TESTNET", "True").lower() == "true"

# Trading Strategy Parameters
DEFAULT_SYMBOL = "BTC/USDT"
TIMEFRAME = "15m"
EMA_FAST = 9
EMA_SLOW = 21
RISK_PER_TRADE = 0.01  # 1%

# CCXT Configuration
CCXT_CONFIG = {
    "binance": {
        "apiKey": BINANCE_API_KEY,
        "secret": BINANCE_SECRET,
        "enableRateLimit": True,
        "options": {"defaultType": "future", "test": USE_BINANCE_TESTNET},
    },
    "bybit": {
        "apiKey": BYBIT_API_KEY,
        "secret": BYBIT_SECRET,
        "enableRateLimit": True,
        "options": {"defaultType": "swap", "test": USE_BYBIT_TESTNET},
    },
}
