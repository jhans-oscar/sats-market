# 🚀 Guía de Deploy - Sats Market

## Opción 1: Railway (Recomendada - Más fácil)

### Paso 1: Preparar el repositorio

1. **Crea un repositorio en GitHub:**
   ```bash
   cd sats-market
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/sats-market.git
   git push -u origin main
   ```

### Paso 2: Deploy en Railway

1. Ve a https://railway.app
2. Click en "Start a New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu cuenta de GitHub
5. Selecciona el repo `sats-market`
6. Railway detectará automáticamente tu proyecto

### Paso 3: Configurar Variables de Entorno

En Railway, ve a "Variables" y añade:
```
FINNHUB_API_KEY=tu_api_key_aqui
PORT=8000
```

### Paso 4: Ajustar comando de inicio

En Railway, ve a "Settings" → "Deploy" y configura:
- **Build Command:** (vacío, Railway lo detecta automático)
- **Start Command:** `cd backend && uvicorn main_production:app --host 0.0.0.0 --port $PORT`

### Paso 5: Deploy!

Railway automáticamente desplegará tu app. Obtendrás una URL como:
`https://sats-market-production.up.railway.app`

---

## Opción 2: Render (También gratis)

### Paso 1: Preparar el repositorio (igual que Railway)

### Paso 2: Deploy en Render

1. Ve a https://render.com
2. Click en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Name:** sats-market
   - **Runtime:** Python 3
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main_production:app --host 0.0.0.0 --port $PORT`

### Paso 3: Variables de Entorno

Añade en la sección "Environment":
```
FINNHUB_API_KEY=tu_api_key_aqui
```

### Paso 4: Deploy!

Click en "Create Web Service". En 5-10 minutos tendrás tu URL.

---

## Opción 3: Fly.io (Más control)

### Paso 1: Instalar flyctl

```bash
# macOS
brew install flyctl

# Linux/WSL
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login
```

### Paso 2: Crear archivo fly.toml

Ya está creado en el proyecto. Solo necesitas:

```bash
cd sats-market
flyctl launch
```

Sigue las instrucciones y configura:
- App name: `sats-market`
- Region: Elige la más cercana
- PostgreSQL: No
- Redis: No

### Paso 3: Configurar secrets

```bash
flyctl secrets set FINNHUB_API_KEY=tu_api_key_aqui
```

### Paso 4: Deploy

```bash
flyctl deploy
```

Tu app estará en: `https://sats-market.fly.dev`

---

## Post-Deploy: Configuración Final

### 1. Verificar que funciona

Abre tu URL y prueba:
- Buscar un ticker (AAPL, TSLA)
- Ver precio en sats
- Añadir a watchlist

### 2. Actualizar el tweet

Publica un follow-up con:
```
✅ Live now!

Sats Market - See stocks in Bitcoin

🔗 [tu-url-aqui]

Features:
• Real-time conversion to sats
• Watchlist that persists
• Clean, minimal design

Built in 48hrs. Feedback welcome 🧡⚡

#Bitcoin #BuildInPublic
```

### 3. Dominio personalizado (Opcional)

#### Railway:
- Ve a Settings → Domains
- Añade tu dominio custom

#### Render:
- Ve a Settings → Custom Domain
- Añade tu dominio y configura DNS

---

## Troubleshooting

### Error: "Ticker not found"
- Verifica que FINNHUB_API_KEY esté configurado correctamente
- Prueba con otro ticker (AAPL, MSFT, GOOGL)

### Error: "Cannot fetch BTC price"
- Espera 1 minuto y vuelve a intentar (rate limits)
- Verifica conectividad del servidor

### Frontend no carga
- Verifica que el path `../frontend` existe en producción
- Asegúrate de que el comando start usa `main_production.py`

---

## Costos

- **Railway:** Free tier (500 horas/mes) - Suficiente para MVP
- **Render:** Free tier (750 horas/mes) - Duerme después de inactividad
- **Fly.io:** Free tier (3 VMs pequeñas) - Más control

**Recomendación:** Empieza con Railway. Es la más simple y funciona perfectamente para este proyecto.

---

## Siguiente: PWA

Una vez deployado, podemos convertirlo en PWA para que sea instalable en iPhone.
