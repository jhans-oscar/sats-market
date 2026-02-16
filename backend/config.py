import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# Finnhub APIs
FINNHUB_QUOTE = "https://finnhub.io/api/v1/quote"
FINNHUB_CANDLES = "https://finnhub.io/api/v1/stock/candle"

# Crypto APIs
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_HISTORY = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
COINBASE_API = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

# Configuración
CACHE_DURATION = 60  # segundos
CACHE_DURATION_LONG = 300  # 5 minutos para históricos
SATS_PER_BTC = 100_000_000

# Tickers populares por defecto
POPULAR_TICKERS = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
