#!/usr/bin/env python3
"""
Script de diagnóstico para Sats Market
Verifica que todo esté configurado correctamente
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("=" * 60)
print("🔍 DIAGNÓSTICO SATS MARKET")
print("=" * 60)

# 1. Verificar imports
print("\n1️⃣  Verificando imports...")
try:
    from config import *
    print("   ✅ config.py importado correctamente")
except Exception as e:
    print(f"   ❌ Error importando config: {e}")
    sys.exit(1)

# 2. Verificar API Key
print("\n2️⃣  Verificando Finnhub API Key...")
if not FINNHUB_API_KEY or FINNHUB_API_KEY == "":
    print("   ❌ FINNHUB_API_KEY está vacío")
    print("   📝 Solución:")
    print("      1. Ve a https://finnhub.io/register")
    print("      2. Regístrate gratis")
    print("      3. Copia tu API key")
    print("      4. Edita backend/.env y pega tu API key")
    print("      5. Reinicia: docker-compose restart")
    sys.exit(1)
elif FINNHUB_API_KEY == "XXXXXXXX":
    print("   ⚠️  API Key es placeholder - necesitas reemplazarla")
    print("   📝 Ve a backend/.env y pon tu API key real")
    sys.exit(1)
else:
    print(f"   ✅ API Key configurada: {FINNHUB_API_KEY[:8]}...")

# 3. Test API call
print("\n3️⃣  Probando llamada a Finnhub API...")
try:
    import httpx
    import asyncio
    
    async def test_api():
        url = FINNHUB_QUOTE
        params = {"symbol": "AAPL", "token": FINNHUB_API_KEY}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if "c" in data and data["c"] > 0:
                    print(f"   ✅ API funciona! AAPL precio: ${data['c']}")
                    return True
                else:
                    print(f"   ❌ API responde pero sin datos válidos")
                    print(f"   Respuesta: {data}")
                    return False
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limit alcanzado (demasiadas requests)")
                print(f"   Espera 1 minuto y vuelve a intentar")
                return False
            elif response.status_code == 401:
                print(f"   ❌ API Key inválida")
                print(f"   Verifica que copiaste la key correctamente")
                return False
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
    
    result = asyncio.run(test_api())
    if not result:
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 4. Verificar tickers populares
print("\n4️⃣  Verificando tickers populares configurados...")
print(f"   ✅ {len(POPULAR_TICKERS)} tickers: {', '.join(POPULAR_TICKERS)}")

# 5. Test BTC price
print("\n5️⃣  Probando obtención de precio BTC...")
try:
    async def test_btc():
        async with httpx.AsyncClient() as client:
            response = await client.get(
                COINGECKO_API,
                params={"ids": "bitcoin", "vs_currencies": "usd"},
                timeout=10.0
            )
            if response.status_code == 200:
                btc_price = response.json()["bitcoin"]["usd"]
                print(f"   ✅ BTC precio: ${btc_price:,.0f}")
                return True
            else:
                print(f"   ❌ Error obteniendo BTC: {response.status_code}")
                return False
    
    asyncio.run(test_btc())
except Exception as e:
    print(f"   ⚠️  Error con CoinGecko: {e}")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETO")
print("=" * 60)
print("\n🚀 Todo configurado correctamente!")
print("   Puedes usar: docker-compose restart")
print("   Luego abre: http://localhost:3000\n")
