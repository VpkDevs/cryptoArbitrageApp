# Crypto Arbitrage Dashboard

A modern React/TypeScript dashboard for real-time monitoring, control, and transparency over the arbitrage platform.

## Features
- Live streaming of detected opportunities (WebSocket)
- Portfolio balances and P&L
- Health and status of all microservices
- Manual override: kill switch, circuit breaker
- Audit log viewer
- Responsive, production-grade UI (Chakra UI)

## Quick Start
```
cd dashboard
npm install
npm start
# Open http://localhost:3000
```

## Configuration
- API base URL: set in `.env` (defaults to http://localhost:8000)
