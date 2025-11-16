"""
Minimal dashboard for Felix Monitor.

This script demonstrates how to orchestrate the data ingestion,
fusion, and risk computation functions to produce a human-readable
summary. It can be run as a standalone CLI application.

In a production environment, you might wish to build a richer
interactive UI (for example using Streamlit, Dash, or a web
framework). Here we simply print results to the console.
"""
from __future__ import annotations

import argparse
from typing import List

from .data_ingest import fetch_felix_positions, fetch_hyperliquid_market
from .data_fusion import fuse_data
from .risk_engine import compute_liquidation_stats, compute_liquidity_impact


def main(symbols: List[str], shock: float) -> None:
    """Entry point for the CLI dashboard."""
    # Step 1: Data ingestion
    positions = fetch_felix_positions(collateral_types=symbols)
    market_data = fetch_hyperliquid_market(symbols)
    # Step 2: Data fusion
    fused = fuse_data(positions, market_data)
    # Step 3: Risk calculations
    stats = compute_liquidation_stats(fused)
    liquidity_impact = compute_liquidity_impact(fused, shock=shock)
    # Print results
    print("=== Felix Monitor Summary ===")
    print("\nShock Scenarios (negative values = price drops):")
    for shock_level, result in stats.items():
        print(
            f"Shock {shock_level*100:+.0f}% -> "
            f"Liquidatable: {result['liquidatable_count']}, "
            f"At-risk collateral: ${result['at_risk_collateral']:,.2f}, "
            f"Bad debt: ${result['bad_debt']:,.2f}"
        )
    print("\nLiquidity Impact for shock {:.0%}:".format(shock))
    for sym, impact in liquidity_impact.items():
        print(f"{sym}: {impact:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Felix Monitor summary.")
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["ETH", "HYPE"],
        help="Collateral symbols to analyse",
    )
    parser.add_argument(
        "--shock",
        type=float,
        default=-0.2,
        help="Single shock level for liquidity impact (-0.2 = -20%)",
    )
    args = parser.parse_args()
    main(args.symbols, args.shock)