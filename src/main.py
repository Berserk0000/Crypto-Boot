import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live

console = Console()

# Define the crypto pairs you want to scan
SYMBOLS = [
    'BTC/USDT', 
    'ETH/USDT', 
    'SOL/USDT', 
    'BNB/USDT', 
    'XRP/USDT', 
    'ADA/USDT', 
    'AVAX/USDT', 
    'LINK/USDT'
]

async def fetch_pair_data(exchange, symbol, timeframe='15m'):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calculate indicators
        df['fast_ema'] = ta.ema(df['close'], length=9)
        df['slow_ema'] = ta.ema(df['close'], length=21)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Determine trend state
        trend = "BULLISH 🟢" if latest['fast_ema'] > latest['slow_ema'] else "BEARISH 🔴"
        
        # Check for fresh crossover signal
        crossover = "NONE"
        if prev['fast_ema'] <= prev['slow_ema'] and latest['fast_ema'] > latest['slow_ema']:
            crossover = "CROSS UP 🚀"
        elif prev['fast_ema'] >= prev['slow_ema'] and latest['fast_ema'] < latest['slow_ema']:
            crossover = "CROSS DOWN ⚠️"

        return {
            "symbol": symbol,
            "price": latest['close'],
            "fast_ema": latest['fast_ema'],
            "slow_ema": latest['slow_ema'],
            "trend": trend,
            "signal": crossover,
            "atr": latest['atr']
        }
    except Exception as e:
        return None

def generate_table(results):
    table = Table(title="⚡ Crypto Trend Scanner (Testnet)", header_style="bold magenta", border_style="cyan")
    
    table.add_column("Symbol", justify="left", style="bold white", no_wrap=True)
    table.add_column("Price (USDT)", justify="right", style="green")
    table.add_column("Fast EMA (9)", justify="right", style="cyan")
    table.add_column("Slow EMA (21)", justify="right", style="blue")
    table.add_column("Trend State", justify="center")
    table.add_column("Signal", justify="center", style="bold")
    table.add_column("ATR", justify="right", style="yellow")

    for r in results:
        if r:
            table.add_row(
                r["symbol"],
                f"{r['price']:,.2f}",
                f"{r['fast_ema']:,.2f}",
                f"{r['slow_ema']:,.2f}",
                r["trend"],
                r["signal"],
                f"{r['atr']:,.2f}"
            )
            
    return table

async def main():
    exchange = ccxt.binance({'enableRateLimit': True})
    if exchange.urls.get('test'):
        exchange.set_sandbox_mode(True)
        
    console.print("[bold yellow]🚀 Multi-Pair Crypto Scanner Initialized... Press Ctrl+C to exit.[/bold yellow]\n")
    
    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                tasks = [fetch_pair_data(exchange, symbol) for symbol in SYMBOLS]
                results = await asyncio.gather(*tasks)
                
                table = generate_table(results)
                live.update(table)
                
                # Wait 10 seconds before next scan cycle
                await asyncio.sleep(10)
                
    except asyncio.CancelledError:
        pass
    finally:
        await exchange.close()
        console.print("[bold red]Scanner shutdown complete.[/bold red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold green]Exited cleanly.[/bold green]")
