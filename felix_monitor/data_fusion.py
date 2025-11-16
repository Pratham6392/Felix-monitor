"""
Data fusion layer for the Felix Monitor.

This module contains functionality for combining data from Felix CDPs
with Hyperliquid trading metrics. The fused data structure produced by
these functions simplifies downstream analysis performed by the risk
engine.
"""
from __future__ import annotations

from typing import Dict, List, Any
from .data_ingest import CdpPosition


def fuse_data(
    positions: List[CdpPosition],
    market_data: Dict[str, Dict[str, float]],
) -> List[Dict[str, Any]]:
    """
    Combine Felix CDP positions with relevant Hyperliquid market data.

    Parameters
    ----------
    positions : list of CdpPosition
        The troves fetched from Felix.
    market_data : dict
        The trading metrics from Hyperliquid keyed by collateral symbol.

    Returns
    -------
    fused : list of dict
        A list of dictionaries where each dictionary contains both
        trove details and market metrics.
    """
    fused: List[Dict[str, Any]] = []
    for pos in positions:
        symbol = pos.collateral_type.upper()
        metrics = market_data.get(symbol, {})
        fused.append(
            {
                "owner": pos.owner,
                "collateral_type": pos.collateral_type,
                "collateral_amount": pos.collateral_amount,
                "collateral_value": pos.collateral_value,
                "debt": pos.debt,
                "icr": pos.icr,
                "min_collateral_ratio": pos.min_collateral_ratio,
                "market_metrics": metrics,
            }
        )
    return fused