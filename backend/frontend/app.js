// Configuration
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : '/api';
const WATCHLIST_KEY = 'satsmarket_watchlist';

// State
let currentUnit = 'sats';
let currentData = null;
let watchlist = loadWatchlist();
let priceChart = null;

// Elements
const tickerInput = document.getElementById('tickerInput');
const btcTicker = document.getElementById('btcTicker');
const popularGrid = document.getElementById('popularGrid');
const detailSection = document.getElementById('detailSection');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const watchlistGrid = document.getElementById('watchlistGrid');
const clearWatchlistBtn = document.getElementById('clearWatchlist');
const chartLoading = document.getElementById('chartLoading');

// Initialize
init();

function init() {
    loadBTCPrice();
    loadPopularStocks();
    renderWatchlist();
    setupEventListeners();
    
    // Refresh intervals
    setInterval(loadBTCPrice, 60000); // 1 min
    setInterval(refreshWatchlist, 30000); // 30 sec
    setInterval(loadPopularStocks, 60000); // 1 min
}

function setupEventListeners() {
    // Search on Enter
    tickerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const ticker = tickerInput.value.trim().toUpperCase();
            if (ticker) searchTicker(ticker);
        }
    });

    // Unit toggle
    document.querySelectorAll('.unit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentUnit = btn.dataset.unit;
            document.querySelectorAll('.unit-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updatePriceDisplay();
            if (currentData) {
                updateChart();
            }
        });
    });

    // Watchlist toggle
    const watchlistBtn = document.getElementById('watchlistBtn');
    watchlistBtn.addEventListener('click', toggleWatchlist);

    // Clear watchlist
    clearWatchlistBtn.addEventListener('click', () => {
        if (confirm('Remove all stocks from watchlist?')) {
            watchlist = [];
            saveWatchlist();
            renderWatchlist();
        }
    });
}

// API Calls
async function loadBTCPrice() {
    try {
        const response = await fetch(`${API_URL}/btc`);
        const data = await response.json();
        const price = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(data.btc_price_usd);
        
        btcTicker.querySelector('.btc-price').textContent = price;
    } catch (err) {
        console.error('Error loading BTC price:', err);
    }
}

async function loadPopularStocks() {
    try {
        const response = await fetch(`${API_URL}/popular`);
        const data = await response.json();
        
        popularGrid.innerHTML = data.popular.map(stock => `
            <div class="popular-card" onclick="searchTicker('${stock.symbol}')">
                <div class="popular-card-header">
                    <div class="popular-ticker">${stock.symbol}</div>
                    <div class="popular-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}">
                        ${stock.change_percent >= 0 ? '↑' : '↓'} ${Math.abs(stock.change_percent).toFixed(2)}%
                    </div>
                </div>
                <div class="popular-price">${formatNumber(stock.price_sats)}</div>
                <div class="popular-unit">sats</div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading popular stocks:', err);
    }
}

async function searchTicker(ticker) {
    showLoading();
    hideError();
    
    try {
        const response = await fetch(`${API_URL}/price/${ticker}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch data');
        }
        
        currentData = await response.json();
        displayDetail();
        loadHistoricalData(ticker);
        tickerInput.value = '';
        
    } catch (err) {
        showError(err.message);
    } finally {
        hideLoading();
    }
}

async function loadHistoricalData(ticker) {
    chartLoading.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_URL}/historical/${ticker}?days=30`);
        
        if (!response.ok) {
            throw new Error('Historical data not available');
        }
        
        const data = await response.json();
        currentData.historical = data.data;
        updateChart();
        
    } catch (err) {
        console.error('Error loading historical data:', err);
    } finally {
        chartLoading.style.display = 'none';
    }
}

function displayDetail() {
    document.getElementById('detailSymbol').textContent = currentData.symbol;
    
    // Change indicator
    const changeEl = document.getElementById('detailChange');
    const changeValue = changeEl.querySelector('.change-value');
    const isPositive = currentData.change_percent >= 0;
    
    changeEl.className = `detail-change ${isPositive ? 'positive' : 'negative'}`;
    changeValue.textContent = `${isPositive ? '↑' : '↓'} ${Math.abs(currentData.change_percent).toFixed(2)}%`;
    
    updatePriceDisplay();
    updateWatchlistButton();
    
    detailSection.style.display = 'block';
    detailSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function updatePriceDisplay() {
    if (!currentData) return;
    
    const mainPrice = document.getElementById('mainPrice');
    const priceUnit = document.getElementById('priceUnit');
    
    switch (currentUnit) {
        case 'sats':
            mainPrice.textContent = formatNumber(currentData.price_sats);
            priceUnit.textContent = 'sats';
            break;
        case 'btc':
            mainPrice.textContent = currentData.price_btc.toFixed(8);
            priceUnit.textContent = '₿';
            break;
        case 'usd':
            mainPrice.textContent = formatCurrency(currentData.price_usd);
            priceUnit.textContent = '';
            break;
    }
    
    // Update conversions
    document.getElementById('conversionUSD').textContent = formatCurrency(currentData.price_usd);
    document.getElementById('conversionBTC').textContent = `₿${currentData.price_btc.toFixed(8)}`;
    document.getElementById('conversionSats').textContent = formatNumber(currentData.price_sats);
}

function updateChart() {
    if (!currentData || !currentData.historical) return;
    
    const ctx = document.getElementById('priceChart').getContext('2d');
    const historical = currentData.historical;
    
    // Prepare data based on current unit
    let chartData = [];
    let yAxisLabel = '';
    
    switch (currentUnit) {
        case 'sats':
            chartData = historical.map(h => h.price_sats);
            yAxisLabel = 'Price (sats)';
            break;
        case 'btc':
            chartData = historical.map(h => h.price_btc);
            yAxisLabel = 'Price (₿)';
            break;
        case 'usd':
            chartData = historical.map(h => h.price_usd);
            yAxisLabel = 'Price (USD)';
            break;
    }
    
    const labels = historical.map(h => {
        const date = new Date(h.timestamp * 1000);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    // Destroy existing chart
    if (priceChart) {
        priceChart.destroy();
    }
    
    // Create new chart
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: currentData.symbol,
                data: chartData,
                borderColor: '#f7931a',
                backgroundColor: 'rgba(247, 147, 26, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointHoverBackgroundColor: '#f7931a',
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1a1a1a',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#f7931a',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        title: (items) => labels[items[0].dataIndex],
                        label: (context) => {
                            let value = context.parsed.y;
                            if (currentUnit === 'sats') {
                                return formatNumber(Math.round(value)) + ' sats';
                            } else if (currentUnit === 'btc') {
                                return '₿' + value.toFixed(8);
                            } else {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 0,
                        autoSkipPadding: 20,
                        color: '#5f6368',
                        font: {
                            family: 'Archivo',
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: '#e8eaed'
                    },
                    ticks: {
                        color: '#5f6368',
                        font: {
                            family: 'JetBrains Mono',
                            size: 11
                        },
                        callback: function(value) {
                            if (currentUnit === 'sats') {
                                return formatNumber(Math.round(value));
                            } else if (currentUnit === 'btc') {
                                return value.toFixed(8);
                            } else {
                                return '$' + value.toFixed(0);
                            }
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Watchlist Functions
function toggleWatchlist() {
    if (!currentData) return;
    
    const btn = document.getElementById('watchlistBtn');
    const ticker = currentData.symbol;
    
    if (isInWatchlist(ticker)) {
        removeFromWatchlist(ticker);
        btn.classList.remove('active');
    } else {
        addToWatchlist(currentData);
        btn.classList.add('active');
    }
}

function addToWatchlist(data) {
    if (!isInWatchlist(data.symbol)) {
        watchlist.push({
            symbol: data.symbol,
            price_sats: data.price_sats,
            price_btc: data.price_btc,
            price_usd: data.price_usd,
            timestamp: Date.now()
        });
        saveWatchlist();
        renderWatchlist();
    }
}

function removeFromWatchlist(ticker) {
    watchlist = watchlist.filter(item => item.symbol !== ticker);
    saveWatchlist();
    renderWatchlist();
    updateWatchlistButton();
}

function isInWatchlist(ticker) {
    return watchlist.some(item => item.symbol === ticker);
}

function updateWatchlistButton() {
    if (!currentData) return;
    const btn = document.getElementById('watchlistBtn');
    if (isInWatchlist(currentData.symbol)) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
}

function renderWatchlist() {
    if (watchlist.length === 0) {
        watchlistGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⭐</div>
                <p>Add stocks to your watchlist</p>
                <span class="empty-hint">Search for any ticker above</span>
            </div>
        `;
        clearWatchlistBtn.style.display = 'none';
        return;
    }
    
    clearWatchlistBtn.style.display = 'block';
    
    watchlistGrid.innerHTML = watchlist.map(item => `
        <div class="watchlist-card" onclick="searchTicker('${item.symbol}')">
            <div class="watchlist-card-header">
                <div class="watchlist-ticker">${item.symbol}</div>
                <button class="watchlist-remove" onclick="event.stopPropagation(); removeFromWatchlist('${item.symbol}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="watchlist-price">${formatNumber(item.price_sats)}</div>
            <div class="watchlist-unit">sats</div>
        </div>
    `).join('');
}

async function refreshWatchlist() {
    if (watchlist.length === 0) return;
    
    for (const item of watchlist) {
        try {
            const response = await fetch(`${API_URL}/price/${item.symbol}`);
            if (response.ok) {
                const data = await response.json();
                const index = watchlist.findIndex(w => w.symbol === item.symbol);
                if (index !== -1) {
                    watchlist[index] = {
                        symbol: data.symbol,
                        price_sats: data.price_sats,
                        price_btc: data.price_btc,
                        price_usd: data.price_usd,
                        timestamp: Date.now()
                    };
                }
            }
        } catch (err) {
            console.error(`Error refreshing ${item.symbol}:`, err);
        }
    }
    
    saveWatchlist();
    renderWatchlist();
}

// LocalStorage
function saveWatchlist() {
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(watchlist));
}

function loadWatchlist() {
    try {
        const data = localStorage.getItem(WATCHLIST_KEY);
        return data ? JSON.parse(data) : [];
    } catch {
        return [];
    }
}

// UI State
function showLoading() {
    loadingState.style.display = 'flex';
}

function hideLoading() {
    loadingState.style.display = 'none';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorState.style.display = 'block';
    setTimeout(() => {
        errorState.style.display = 'none';
    }, 5000);
}

function hideError() {
    errorState.style.display = 'none';
}

// Formatters
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function formatCurrency(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}