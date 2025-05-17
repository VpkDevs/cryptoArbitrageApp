# Crypto Arbitrage Platform – Risk Disclosure

**"Near-zero risk" means all material risks are minimized via layered controls, but risk is not eliminated.**

## Key Risks
- **Market Risk**: Sudden price moves, flash crashes, or illiquidity can cause loss.
- **Exchange Risk**: Exchange downtime, API failures, or insolvency may block or reverse trades.
- **Transfer Risk**: Blockchain congestion, stuck transactions, or high gas fees may delay or block fund transfers.
- **Operational Risk**: Bugs, network outages, or misconfiguration can cause loss or missed trades.
- **Counterparty Risk**: Custody of funds on third-party venues exposes to hacks or misappropriation.
- **Regulatory Risk**: Jurisdictional restrictions or compliance failures may result in frozen assets or legal action.

## Controls
- All trade/risk/transfer limits are enforced by code.
- Circuit breakers, kill switches, and anomaly detection are built-in.
- API keys and secrets are never stored in plaintext; Vault or KMS required.
- All operations are logged for audit and compliance.
- Only operate on KYC/AML-compliant exchanges; geo-block restricted regions.

## No Guarantee
No system can guarantee profit or absolute safety. Extreme market events or infrastructure failures can cause loss. Use at your own risk.
