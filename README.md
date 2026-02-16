# ⚡ Sats Market

Ver el mercado de valores a través de ojos Bitcoin. Convierte cualquier ticker (AAPL, TSLA, MSFT) a sats en tiempo real.

## 🚀 Inicio Rápido con Docker

### Prerequisitos
- Docker instalado ([Descargar aquí](https://www.docker.com/get-started))
- Docker Compose (incluido con Docker Desktop)

### Instalación

1. **Clona o descarga este proyecto**
```bash
cd sats-market
```

2. **Levanta los contenedores**
```bash
docker-compose up -d
```

3. **Abre en el navegador**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

¡Eso es todo! 🎉

### Comandos útiles

```bash
# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reconstruir después de cambios
docker-compose up -d --build

# Ver estado de contenedores
docker-compose ps
```

## 📡 API Endpoints

### Obtener precio de BTC
```bash
GET http://localhost:8000/api/btc
```

**Respuesta:**
```json
{
  "btc_price_usd": 95234.50,
  "timestamp": 1708123456.789
}
```

### Obtener precio de acción
```bash
GET http://localhost:8000/api/price/{ticker}
```

**Ejemplo:**
```bash
curl http://localhost:8000/api/price/AAPL
```

**Respuesta:**
```json
{
  "symbol": "AAPL",
  "exchange": "NMS",
  "price_usd": 185.50,
  "price_btc": 0.00194821,
  "price_sats": 194821,
  "btc_rate": 95234.50,
  "timestamp": 1708123456,
  "formatted_sats": "194,821"
}
```

## 🛠️ Desarrollo

### Sin Docker (desarrollo local)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
Abre `frontend/index.html` en el navegador o usa un servidor local:
```bash
cd frontend
python -m http.server 3000
```

## 🎨 Features

- ✅ Conversión en tiempo real USD → BTC → Sats
- ✅ Búsqueda de cualquier ticker
- ✅ Toggle entre USD/BTC/Sats
- ✅ Tickers populares de acceso rápido
- ✅ Diseño responsive (móvil y desktop)
- ✅ Tema Bitcoin (naranja y negro)
- ✅ Cache para optimizar requests
- ✅ Dockerizado y listo para producción

## 🔧 Próximas Features (Roadmap)

- [ ] Watchlist persistente
- [ ] Gráficos históricos en sats
- [ ] PWA (Progressive Web App)
- [ ] Alertas de precio
- [ ] Portfolio tracker
- [ ] Comparación entre múltiples tickers

## 📊 APIs Utilizadas

- **Yahoo Finance** - Precios de acciones (gratis, sin API key)
- **CoinGecko** - Precio de Bitcoin (gratis, sin API key)
- **Coinbase** - Fallback para precio BTC (gratis)

## 🤝 Contribuir

¿Ideas? ¿Bugs? ¡PRs bienvenidos!

## 📄 Licencia

MIT

---

Hecho con 🧡 para la comunidad Bitcoin
