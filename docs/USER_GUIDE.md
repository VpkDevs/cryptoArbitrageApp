# Crypto Arbitrage Platform – User Guide

## Dashboard Overview

- **Opportunities Tab**: Live stream of all detected arbitrage opportunities. Hover over any value for a tooltip explaining its meaning (e.g., "Profit (%)" shows estimated net gain after fees; "Legs" lists the sequence of trades).
- **Portfolio Tab**: Shows your current balances and positions across all connected exchanges. Tooltips explain each column (e.g., "Available" is the amount you can trade immediately).
- **Health Tab**: Displays system and API status. Green = healthy, red = action needed.
- **Controls Tab**: Manual override controls, including the kill switch. Tooltips explain risks and best practices for each control.
- **Audit Log Tab**: Immutable log of all key actions and events. Hover for details.

## Key Concepts (with built-in tooltips/explainers)
- **Arbitrage Opportunity**: A chance to profit from price differences across exchanges or products. The dashboard explains each type (spatial, triangular, statistical) via tooltips.
- **Legs**: The sequence of trades needed to capture an arbitrage. Hover on any leg to see a breakdown (exchange, symbol, side, price).
- **Risk Score**: An estimate of the riskiness of the opportunity, factoring in volatility, liquidity, and system health.
- **Kill Switch**: Instantly halts all trading. Use only in emergencies; see tooltip for details.

## Getting Help
- All dashboard elements have hover-tooltips. If you are unsure about a term, hover or click the info icon.
- For advanced help, see the full documentation in the `docs/` folder.
