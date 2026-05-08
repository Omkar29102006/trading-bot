# 🤖 Binance Futures Testnet Trading Bot

A clean, structured Python CLI application to place orders on the **Binance Futures Testnet (USDT-M)**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client (signing, HTTP)
│   ├── orders.py          # Order placement logic + response formatting
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Rotating file + console logging
├── cli.py                 # CLI entry point (argparse)
├── logs/
│   ├── market_order.log   # Sample MARKET order log
│   └── limit_order.log    # Sample LIMIT order log
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd trading_bot
```

### 2. Create & activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get Binance Futures Testnet credentials
1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Register / log in
3. Navigate to **API Management** → generate a new API key
4. Copy your **API Key** and **Secret Key**

### 5. Set environment variables
```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

On Windows (Command Prompt):
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

---

## How to Run

### Place a MARKET BUY order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a LIMIT SELL order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```

### Place a STOP_MARKET BUY order (bonus order type)
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 95000
```

### Place a STOP (Stop-Limit) SELL order
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --price 58000 --stop-price 58500
```

### View help
```bash
python cli.py --help
```

---

## Sample Output

```
──────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
──────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
──────────────────────────────────────────────────

──────────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────────
  Order ID   : 3865988542
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Status     : FILLED
  Qty Ordered: 0.01
  Qty Filled : 0.01
  Avg Price  : 62345.10
  Price      : 0
──────────────────────────────────────────────────

✅  Order placed successfully!
```

---

## Logging

Logs are written to `trading_bot.log` in the project root (rotating, max 5 MB × 3 backups).

- **File log**: DEBUG level – captures every API request/response and error detail
- **Console log**: INFO level – clean, human-readable output

Sample log files are in `logs/`:
- `logs/market_order.log` – sample MARKET order run
- `logs/limit_order.log`  – sample LIMIT order run

---

## Assumptions

- The bot targets **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`).
- Credentials are provided via environment variables (not hardcoded).
- `timeInForce` defaults to `GTC` for LIMIT and STOP orders.
- No position/balance check is performed before order placement — the exchange validates this.
- Quantities and prices are passed as strings to preserve decimal precision.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `httpx` | Async-capable HTTP client for REST API calls |

> No `python-binance` library is used — all API calls are direct REST with HMAC-SHA256 signing.
