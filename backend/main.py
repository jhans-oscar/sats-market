from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List
from config import *

app = FastAPI(title="Sats Market API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = {}

async def get_btc_price() -> float:
    """Obtiene precio actual de BTC en USD"""
    cache_key = "btc_price"
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                COINGECKO_API,
                params={"ids": "bitcoin", "vs_currencies": "usd"},
                timeout=10.0
            )
            if response.status_code == 200:
                btc_price = response.json()["bitcoin"]["usd"]
                cache[cache_key] = (btc_price, time.time())
                return btc_price
    except:
        pass
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(COINBASE_API, timeout=10.0)
            if response.status_code == 200:
                btc_price = float(response.json()["data"]["amount"])
                cache[cache_key] = (btc_price, time.time())
                return btc_price
    except:
        raise HTTPException(status_code=503, detail="No se pudo obtener precio de BTC")

async def get_btc_historical(days: int = 30) -> List[Dict]:
    """Obtiene histórico de BTC en USD"""
    cache_key = f"btc_history_{days}"
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION_LONG:
            return data
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                COINGECKO_HISTORY,
                params={"vs_currency": "usd", "days": days},
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                # CoinGecko returns [timestamp_ms, price] pairs
                history = [
                    {"timestamp": int(point[0] / 1000), "price": point[1]}
                    for point in data["prices"]
                ]
                cache[cache_key] = (history, time.time())
                return history
    except:
        pass
    
    return []

async def get_stock_quote(ticker: str) -> Dict:
    """Obtiene cotización completa con cambio % desde Finnhub"""
    cache_key = f"stock_quote_{ticker.upper()}"
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    
    url = FINNHUB_QUOTE
    params = {
        "symbol": ticker.upper(),
        "token": FINNHUB_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Error obteniendo {ticker}")
            
            data = response.json()
            
            # Finnhub quote response:
            # c: current price, d: change, dp: percent change, h: high, l: low, o: open, pc: previous close
            if "c" not in data or data["c"] == 0:
                raise HTTPException(status_code=404, detail=f"Ticker {ticker} no encontrado")
            
            quote_data = {
                "symbol": ticker.upper(),
                "current_price": float(data["c"]),
                "change": float(data.get("d", 0)),
                "change_percent": float(data.get("dp", 0)),
                "high": float(data.get("h", 0)),
                "low": float(data.get("l", 0)),
                "open": float(data.get("o", 0)),
                "previous_close": float(data.get("pc", 0)),
                "timestamp": int(time.time())
            }
            
            cache[cache_key] = (quote_data, time.time())
            return quote_data
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def get_stock_historical(ticker: str, days: int = 30) -> List[Dict]:
    """Obtiene datos históricos de una acción - primero intenta Finnhub, luego Yahoo Finance"""
    cache_key = f"stock_history_{ticker.upper()}_{days}"
    
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION_LONG:
            return data
    
    to_date = int(datetime.now().timestamp())
    from_date = int((datetime.now() - timedelta(days=days)).timestamp())
    
    # Try Finnhub first
    url = FINNHUB_CANDLES
    params = {
        "symbol": ticker.upper(),
        "resolution": "D",
        "from": from_date,
        "to": to_date,
        "token": FINNHUB_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("s") == "ok" and data.get("c"):
                    history = [
                        {
                            "timestamp": data["t"][i],
                            "close": data["c"][i],
                            "high": data["h"][i],
                            "low": data["l"][i],
                            "open": data["o"][i],
                            "volume": data["v"][i]
                        }
                        for i in range(len(data["c"]))
                    ]
                    
                    cache[cache_key] = (history, time.time())
                    return history
    except Exception as e:
        print(f"Finnhub historical error: {e}")
    
    # Fallback to Yahoo Finance
    print(f"Trying Yahoo Finance for {ticker} historical data...")
    try:
        # Yahoo Finance chart API
        period1 = from_date
        period2 = to_date
        yahoo_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}"
        params = {
            "period1": period1,
            "period2": period2,
            "interval": "1d"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(yahoo_url, params=params, headers=headers, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("chart") and data["chart"].get("result"):
                    result = data["chart"]["result"][0]
                    timestamps = result.get("timestamp", [])
                    quotes = result.get("indicators", {}).get("quote", [{}])[0]
                    
                    if timestamps and quotes.get("close"):
                        history = []
                        for i in range(len(timestamps)):
                            if quotes["close"][i] is not None:
                                history.append({
                                    "timestamp": timestamps[i],
                                    "close": quotes["close"][i],
                                    "high": quotes.get("high", [None] * len(timestamps))[i] or quotes["close"][i],
                                    "low": quotes.get("low", [None] * len(timestamps))[i] or quotes["close"][i],
                                    "open": quotes.get("open", [None] * len(timestamps))[i] or quotes["close"][i],
                                    "volume": quotes.get("volume", [0] * len(timestamps))[i]
                                })
                        
                        if history:
                            cache[cache_key] = (history, time.time())
                            return history
                            
    except Exception as e:
        print(f"Yahoo Finance historical error: {e}")
    
    return []

# API Endpoints

@app.get("/api")
async def api_root():
    return {
        "message": "Sats Market API 🧡⚡",
        "version": "2.0.0",
        "endpoints": {
            "btc": "/api/btc",
            "price": "/api/price/{ticker}",
            "historical": "/api/historical/{ticker}",
            "popular": "/api/popular",
            "compare": "/api/compare?tickers=AAPL,TSLA"
        }
    }

@app.get("/api/btc")
async def get_btc():
    """Obtiene precio actual de BTC"""
    btc_price = await get_btc_price()
    return {
        "btc_price_usd": btc_price,
        "timestamp": time.time()
    }

@app.get("/api/price/{ticker}")
async def get_price(ticker: str):
    """
    Obtiene precio completo de una acción en USD, BTC y Sats con cambio %
    """
    # Obtener cotización con cambio %
    quote_data = await get_stock_quote(ticker)
    
    # Obtener precio de BTC
    btc_price = await get_btc_price()
    
    # Calcular conversiones
    price_usd = quote_data["current_price"]
    price_btc = price_usd / btc_price
    price_sats = price_btc * SATS_PER_BTC
    
    return {
        "symbol": quote_data["symbol"],
        "price_usd": round(price_usd, 2),
        "price_btc": round(price_btc, 8),
        "price_sats": int(price_sats),
        "change": round(quote_data["change"], 2),
        "change_percent": round(quote_data["change_percent"], 2),
        "high": round(quote_data["high"], 2),
        "low": round(quote_data["low"], 2),
        "btc_rate": round(btc_price, 2),
        "timestamp": quote_data["timestamp"],
        "formatted_sats": f"{int(price_sats):,}"
    }

@app.get("/api/historical/{ticker}")
async def get_historical(ticker: str, days: int = 30):
    """
    Obtiene histórico de precios en sats
    """
    # Obtener históricos de stock y BTC en paralelo
    stock_history = await get_stock_historical(ticker, days)
    btc_history = await get_btc_historical(days)
    
    if not stock_history or not btc_history:
        raise HTTPException(status_code=404, detail="Datos históricos no disponibles")
    
    # Crear un mapa de precios BTC por timestamp (aproximado al día)
    btc_price_map = {}
    for btc_point in btc_history:
        # Redondear a día
        day_timestamp = btc_point["timestamp"] - (btc_point["timestamp"] % 86400)
        btc_price_map[day_timestamp] = btc_point["price"]
    
    # Convertir histórico a sats
    sats_history = []
    for point in stock_history:
        day_timestamp = point["timestamp"] - (point["timestamp"] % 86400)
        
        # Encontrar el precio BTC más cercano
        btc_price = btc_price_map.get(day_timestamp)
        if not btc_price:
            # Buscar el más cercano
            closest_ts = min(btc_price_map.keys(), key=lambda x: abs(x - day_timestamp))
            btc_price = btc_price_map[closest_ts]
        
        price_btc = point["close"] / btc_price
        price_sats = price_btc * SATS_PER_BTC
        
        sats_history.append({
            "timestamp": point["timestamp"],
            "price_usd": round(point["close"], 2),
            "price_sats": int(price_sats),
            "price_btc": round(price_btc, 8)
        })
    
    return {
        "symbol": ticker.upper(),
        "days": days,
        "data": sats_history
    }

@app.get("/api/popular")
async def get_popular():
    """
    Obtiene precios de los tickers más populares
    """
    results = []
    btc_price = await get_btc_price()
    
    for ticker in POPULAR_TICKERS:
        try:
            quote_data = await get_stock_quote(ticker)
            price_usd = quote_data["current_price"]
            price_btc = price_usd / btc_price
            price_sats = price_btc * SATS_PER_BTC
            
            results.append({
                "symbol": ticker,
                "price_usd": round(price_usd, 2),
                "price_sats": int(price_sats),
                "change_percent": round(quote_data["change_percent"], 2)
            })
        except:
            # Skip if ticker fails
            continue
    
    return {"popular": results, "btc_price": btc_price}

@app.get("/api/compare")
async def compare_stocks(tickers: str):
    """
    Compara múltiples tickers (máximo 4)
    Query: ?tickers=AAPL,TSLA,MSFT
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")][:4]
    
    if not ticker_list:
        raise HTTPException(status_code=400, detail="Provide at least one ticker")
    
    btc_price = await get_btc_price()
    results = []
    
    for ticker in ticker_list:
        try:
            quote_data = await get_stock_quote(ticker)
            price_usd = quote_data["current_price"]
            price_btc = price_usd / btc_price
            price_sats = price_btc * SATS_PER_BTC
            
            results.append({
                "symbol": ticker,
                "price_usd": round(price_usd, 2),
                "price_btc": round(price_btc, 8),
                "price_sats": int(price_sats),
                "change_percent": round(quote_data["change_percent"], 2)
            })
        except Exception as e:
            results.append({
                "symbol": ticker,
                "error": str(e)
            })
    
    return {"comparison": results, "btc_rate": btc_price}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "timestamp": time.time()}

# Serve static files (frontend) in production
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/{filename:path}")
    async def serve_frontend(filename: str):
        if filename.startswith("api"):
            return {"error": "Not found"}
        
        if filename in ["", "/"]:
            return FileResponse(os.path.join(frontend_path, "index.html"))
        
        file_path = os.path.join(frontend_path, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(frontend_path, "index.html"))
