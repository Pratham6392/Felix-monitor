# Felix Monitor

This repository contains a minimal proof‑of‑concept implementation of a
cross‑asset risk and trading monitor for the Felix Protocol on
Hyperliquid. The project follows a layered architecture inspired by the
design discussed with the user:

```
+------------------------+
|   Hyperliquid API     |
|  - OI, skew, funding  |
|  - orderbook depth    |
+-----------+------------+
            |
            v
 +------------+       +--------------+       +-----------------+
 | Felix Sub- | ----> | Data Fusion | ----> | Risk Engine     |
 | graph/API  |       | Layer       |       |                 |
 | CDPs, ICR  |       |             |       | - ICR shifts    |
 | Collateral |       |             |       | - Bad debt calc |
 +------------+       +--------------+       +-----------------+
            |
            v
     +--------------+
     | Front-end UI |
     |   Dashboard  |
     +--------------+
```

## Components

1. **Data Ingestion (`felix_monitor/data_ingest.py`)**

   Functions for fetching Felix CDP positions and Hyperliquid market
   statistics. The current implementation uses stubbed data and is
   intended to be replaced with real network calls (e.g. GraphQL and
   REST API requests).

2. **Data Fusion (`felix_monitor/data_fusion.py`)**

   Combines the on‑chain positions with market metrics so that they can
   be consumed by the risk engine.

3. **Risk Engine (`felix_monitor/risk_engine.py`)**

   Computes:

   * Liquidation statistics under varying price shocks.
   * An illustrative correlation between open interest changes and
     collateral ratio changes.
   * Simplified estimates of liquidity impacts of forced liquidations.

4. **Dashboard (`felix_monitor/dashboard.py`)**

   A simple CLI entry point that glues together the ingestion, fusion
   and risk calculations and prints a summary to the console.

## How to Run

The monitor is intended to be run as a Python module. A Python 3.10+
environment with `requests` (optional) and standard libraries is
sufficient. To execute the CLI:

```bash
python -m felix_monitor.dashboard --symbols ETH HYPE --shock -0.2
```

This will fetch stub data, compute liquidation scenarios and print
impact metrics for a 20% price drop.

## Extending the Monitor

To integrate with live systems, you should:

* Replace the stubbed implementations in `data_ingest.py` with
  actual calls to the Felix subgraph or RPC endpoints.
* Use Hyperliquid’s official API to retrieve real market statistics.
* Persist historical data to enable true time‑series correlation
  analysis in `risk_engine.compute_perp_cdp_correlation`.
* Build a graphical dashboard using Streamlit, Dash or a web framework.

## License

This project is provided for demonstration purposes only and comes
without any warranty. Please verify results independently before
using it for any production or financial decisions.