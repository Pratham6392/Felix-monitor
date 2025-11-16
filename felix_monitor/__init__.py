"""
felix_monitor
==============

This package provides a basic framework for monitoring risk
exposures across the Felix Protocol and Hyperliquid ecosystem.

It follows a layered architecture:

* Data ingestion functions for fetching on‑chain and market data.
* A data fusion layer to join Felix CDP positions with Hyperliquid
  trading metrics.
* A risk engine that computes liquidation scenarios and risk metrics.
* A minimal user interface layer to display results to analysts.

The code within this package is intended as a starting point and
does not make live network requests by default. To use in a real
environment you will need to supply API endpoints and potentially
API keys.
"""

from .data_ingest import fetch_felix_positions, fetch_hyperliquid_market
from .data_fusion import fuse_data
from .risk_engine import (
    compute_liquidation_stats,
    compute_perp_cdp_correlation,
    compute_liquidity_impact,
)