# Web Trading Bot

Aplikasi web trading otomatis dengan fitur backtest, live scanner, optimizer, dan auto trading untuk cryptocurrency futures.

## Fitur Utama

### 🔍 Backtest
- Atur tanggal, saldo, leverage, margin, dan timeframe
- Analisis performa strategi dengan data historis
- Visualisasi equity curve dan statistik trading

### 📡 Live Scanner 24/7
- Monitor pair USDT-Futures secara real-time
- Deteksi sinyal otomatis berdasarkan strategi
- Notifikasi langsung ke Telegram
- Monitor TP hit otomatis

### 🎯 Parameter Optimizer
- Optimasi setting TP, SL, dan parameter strategi
- Penyesuaian otomatis berdasarkan karakter masing-masing coin
- Analisis performa terbaik untuk setiap pair

### 🤖 Auto Trading
- Filter ketat: winrate minimal, drawdown maksimal, jumlah trade
- Integrasi langsung dengan Binance API
- Entry otomatis hanya untuk sinyal yang lolos semua kriteria

## Instalasi

1. Clone atau download project ini
2. Jalankan `run.bat` atau:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
3. Buka browser ke `http://localhost:5000`

## Konfigurasi

### Binance API
1. Login ke Binance
2. Buat API Key di Account > API Management
3. Enable Futures Trading
4. Masukkan API Key dan Secret di aplikasi

### Telegram Bot
1. Chat dengan @BotFather di Telegram
2. Buat bot baru dengan `/newbot`
3. Dapatkan Bot Token
4. Dapatkan Chat ID dengan chat ke bot dan buka:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`

## Strategi Trading

Aplikasi menggunakan kombinasi indikator:
- RSI (Relative Strength Index)
- EMA Crossover (12/26)
- Simple Moving Average
- Support/Resistance levels

### Sinyal Long
- RSI < 30 (oversold)
- EMA fast cross above EMA slow
- Price above MA

### Sinyal Short  
- RSI > 70 (overbought)
- EMA fast cross below EMA slow
- Price below MA

## Keamanan

- Gunakan API Key dengan permission terbatas
- Set IP whitelist di Binance
- Mulai dengan balance kecil untuk testing
- Monitor performance secara berkala

## Disclaimer

Trading cryptocurrency memiliki risiko tinggi. Gunakan aplikasi ini dengan bijak dan hanya trade dengan dana yang siap hilang. Developer tidak bertanggung jawab atas kerugian trading.

## Support

Untuk pertanyaan dan support, hubungi developer melalui Telegram atau email.