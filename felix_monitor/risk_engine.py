"""
Risk engine for the Felix Monitor.

This module defines functions to perform risk analytics on the fused
CDP and market data. The goal of the risk engine is to provide a
set of metrics and scenario analyses that help stakeholders
understand potential liquidation events, correlation between
trading activity and CDP health, and liquidity impacts.

The functions here do not perform any I/O; they operate purely on
in-memory data structures.
"""
from __future__ import annotations

import math
from typing import Dict, List, Any, Tuple


def compute_liquidation_stats(
    fused_data: List[Dict[str, Any]],
    shock_levels: List[float] | None = None,
) -> Dict[float, Dict[str, Any]]:
    """
    Compute liquidation statistics under varying price shocks.

    Parameters
    ----------
    fused_data : list of dict
        Combined trove and market records from the data fusion layer.
    shock_levels : list of float, optional
        Percentage price shocks to apply. Negative values represent
        price drops (e.g. -0.2 means a -20% price shock).
        Defaults to [-0.05, -0.1, -0.2, -0.3, -0.4].

    Returns
    -------
    results : dict
        Mapping of shock level -> summary statistics:
        {
            "liquidatable_count": int,
            "at_risk_collateral": float,
            "bad_debt": float,
        }

    Notes
    -----
    The function assumes that collateral and debt are denominated in the
    same stable unit (e.g. USD). For simplicity, we do not model
    liquidation penalties or partial liquidations; if a trove becomes
    under-collateralized, its entire debt is considered bad debt.
    """
    if shock_levels is None:
        shock_levels = [-0.05, -0.1, -0.2, -0.3, -0.4]

    results: Dict[float, Dict[str, Any]] = {}
    for shock in shock_levels:
        liquidatable_count = 0
        at_risk_collateral = 0.0
        bad_debt = 0.0
        for record in fused_data:
            # apply price shock on collateral value
            collateral_value_new = record["collateral_value"] * (1 + shock)
            debt = record["debt"]
            icr_new = float("inf") if debt == 0 else collateral_value_new / debt
            min_ratio = record["min_collateral_ratio"]
            # check if new ICR falls below the minimum collateral ratio
            if icr_new < min_ratio:
                liquidatable_count += 1
                at_risk_collateral += record["collateral_value"]
                bad_debt += max(0.0, debt - collateral_value_new)
        results[shock] = {
            "liquidatable_count": liquidatable_count,
            "at_risk_collateral": at_risk_collateral,
            "bad_debt": bad_debt,
        }
    return results


def compute_perp_cdp_correlation(
    fused_data: List[Dict[str, Any]],
    history: List[Tuple[float, float]] | None = None,
) -> float:
    """
    Compute the correlation between changes in open interest and changes
    in average collateral ratios.

    Parameters
    ----------
    fused_data : list of dict
        The latest fused data; expected to include market_metrics.
    history : list of (oi_change, icr_change), optional
        Historical pairs of changes in open interest and average ICR.

    Returns
    -------
    corr : float
        Pearson correlation coefficient between OI changes and ICR changes.

    Notes
    -----
    This is a placeholder implementation. In a full system you would
    track time series of both open interest and average ICR and then
    compute correlation across these samples. Here we simply return
    0.0 when insufficient history is provided.
    """
    if not history or len(history) < 2:
        return 0.0
    oi_changes, icr_changes = zip(*history)
    # compute Pearson correlation
    mean_oi = sum(oi_changes) / len(oi_changes)
    mean_icr = sum(icr_changes) / len(icr_changes)
    numerator = sum(
        (oi - mean_oi) * (icr - mean_icr) for oi, icr in zip(oi_changes, icr_changes)
    )
    denominator = math.sqrt(
        sum((oi - mean_oi) ** 2 for oi in oi_changes)
        * sum((icr - mean_icr) ** 2 for icr in icr_changes)
    )
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def compute_liquidity_impact(
    fused_data: List[Dict[str, Any]],
    shock: float,
    orderbook_depth_levels: Dict[str, float] | None = None,
) -> Dict[str, float]:
    """
    Estimate the price impact of liquidating collateral under a given shock.

    Parameters
    ----------
    fused_data : list of dict
        Combined trove and market records from the data fusion layer.
    shock : float
        The price shock applied (e.g., -0.2 for a 20% price drop).
    orderbook_depth_levels : dict, optional
        Additional depth levels to override each symbol's best bid depth.
        By default, uses the 'best_bid_depth' from the fused market metrics.

    Returns
    -------
    impact : dict
        Mapping from collateral symbol -> estimated impact ratio:
        (collateral_to_sell / orderbook_depth)

    Notes
    -----
    This simplified model assumes that liquidation amounts are sold
    immediately into the top orderbook level. In reality, liquidations
    would likely interact with deeper levels and other sources of
    liquidity, which should be considered for more precise modelling.
    """
    impact: Dict[str, float] = {}
    # group at-risk collateral by symbol
    collateral_to_sell: Dict[str, float] = {}
    for record in fused_data:
        collateral_value_new = record["collateral_value"] * (1 + shock)
        debt = record["debt"]
        icr_new = float("inf") if debt == 0 else collateral_value_new / debt
        if icr_new < record["min_collateral_ratio"]:
            symbol = record["collateral_type"].upper()
            collateral_to_sell[symbol] = collateral_to_sell.get(symbol, 0.0) + record[
                "collateral_value"
            ]
    # compute impact relative to orderbook depth
    for symbol, amount in collateral_to_sell.items():
        # Determine depth: use override if provided, else use first record's metrics.
        depth = None
        if orderbook_depth_levels and symbol in orderbook_depth_levels:
            depth = orderbook_depth_levels.get(symbol)
        else:
            # Find a record with this symbol and get its market_metrics
            for record in fused_data:
                if record["collateral_type"].upper() == symbol:
                    depth = record["market_metrics"].get("best_bid_depth")
                    break
        
        # If depth is still None, use a default value
        if depth is None:
            depth = 1.0
        
        impact[symbol] = amount / max(depth, 1e-8)
    return impact