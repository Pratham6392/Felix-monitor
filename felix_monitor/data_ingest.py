"""
Data ingestion for Felix Monitor.

This module defines functions responsible for retrieving data from
external services:

* Felix Protocol positions and collateral data via a subgraph or
  smart contract RPC calls.
* Hyperliquid market statistics such as open interest, funding rates,
  skew, realized volatility and orderbook depths.

These functions are implemented with placeholder logic for now.
When integrating into a live environment, replace the stub
implementations with real network calls (e.g. GraphQL queries or REST
API requests).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import requests

# Attempt to import web3 for on‑chain interactions. If unavailable,
# the on‑chain functions will fall back to stubbed data. To use
# `fetch_felix_positions` with real data you must install the
# `web3` library (e.g. `pip install web3`).
try:
    from web3 import Web3
except ImportError:  # pragma: no cover - fall back if web3 is missing
    Web3 = None  # type: ignore
    logging.getLogger(__name__).warning(
        "web3 library not installed; Felix on‑chain data ingestion will use stubbed data"
    )

logger = logging.getLogger(__name__)


@dataclass
class CdpPosition:
    """Represents a single CDP (collateralized debt position) on Felix."""

    owner: str
    collateral_type: str
    collateral_amount: float
    debt: float
    price: float
    min_collateral_ratio: float

    @property
    def collateral_value(self) -> float:
        """Return the USD value of the collateral."""
        return self.collateral_amount * self.price

    @property
    def icr(self) -> float:
        """Individual Collateral Ratio (ICR)."""
        if self.debt == 0:
            return float("inf")
        return self.collateral_value / self.debt


def fetch_felix_positions(
    network: str = "hyperliquid",
    collateral_types: List[str] | None = None,
    force_stub: bool = False,
    **kwargs,
) -> List[CdpPosition]:
    """
    Fetch open CDPs from the Felix protocol.

    Parameters
    ----------
    network : str, optional
        The blockchain network to query (default "hyperliquid").
    collateral_types : list of str, optional
        Filter results by specific collateral tokens (e.g. ["ETH", "HYPE"]).
    force_stub : bool, optional
        If True, forces the function to return stubbed data even if web3 is available.

    Returns
    -------
    positions : list of CdpPosition
        A list of CdpPosition objects representing each open trove.

    Notes
    -----
    This function currently contains stubbed data for demonstration
    purposes. To integrate with the actual Felix subgraph, you can
    use the `requests` library to perform a GraphQL query and then
    map the response to `CdpPosition` instances.
    """
    # Default RPC URL for Hyperliquid; can be overridden by rpc_url parameter.
    rpc_url: str | None = kwargs.pop("rpc_url", None)
    if rpc_url is None:
        rpc_url = os.getenv("HYPERLIQUID_RPC_URL", "https://ethereum.publicnode.com")

    # Optional mapping of collateral symbols to contract addresses and metadata.
    # Each entry should include:
    #   - trove_manager: address of the TroveManager contract for that collateral
    #   - trove_nft: address of the ERC721 Trove NFT contract
    #   - price_feed: address of the price feed (Chainlink Aggregator or similar)
    #   - decimals: collateral token decimals (e.g., 18)
    #   - debt_decimals: decimals for feUSD (default 18)
    #   - min_collateral_ratio: the minimum collateral ratio required to avoid liquidation
    collateral_configs: Dict[str, Dict[str, Any]] | None = kwargs.pop(
        "collateral_configs", None
    )
    if collateral_configs is None:
        collateral_configs = {
            "HYPE": {
                "trove_manager": "0x0000000000000000000000000000000000000000",
                "trove_nft": "0x0000000000000000000000000000000000000000",
                "price_feed": "0x0000000000000000000000000000000000000000",
                "decimals": 18,
                "debt_decimals": 18,
                "min_collateral_ratio": 1.2,
            },
            "ETH": {
                "trove_manager": "0x0000000000000000000000000000000000000000",
                "trove_nft": "0x0000000000000000000000000000000000000000",
                "price_feed": "0x0000000000000000000000000000000000000000",
                "decimals": 18,
                "debt_decimals": 18,
                "min_collateral_ratio": 1.5,
            },
        }

    # Maximum number of troves to fetch per collateral. Set this to limit
    # execution time; if None, all troves will be enumerated.
    max_troves_per_collateral: Optional[int] = kwargs.pop(
        "max_troves_per_collateral", None
    )

    # If web3 is not available or force_stub, fall back to stubbed data.
    if Web3 is None or force_stub:
        logger.info("Returning stubbed Felix CDP data with expanded token set")
        dummy_data = [
            # ETH Positions (multiple users, varied amounts)
            CdpPosition(
                owner="0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
                collateral_type="ETH",
                collateral_amount=15.5,
                debt=28000.0,
                price=3200.0,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0x2b3c4d5e6f7890abcdef1234567890abcdef1234",
                collateral_type="ETH",
                collateral_amount=8.2,
                debt=12000.0,
                price=3200.0,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0x3c4d5e6f7890abcdef1234567890abcdef123456",
                collateral_type="ETH",
                collateral_amount=25.0,
                debt=45000.0,
                price=3200.0,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0x4d5e6f7890abcdef1234567890abcdef12345678",
                collateral_type="ETH",
                collateral_amount=5.7,
                debt=8500.0,
                price=3200.0,
                min_collateral_ratio=1.5,
            ),
            # BTC Positions
            CdpPosition(
                owner="0x5e6f7890abcdef1234567890abcdef1234567890",
                collateral_type="BTC",
                collateral_amount=2.5,
                debt=95000.0,
                price=65000.0,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0x6f7890abcdef1234567890abcdef12345678901a",
                collateral_type="BTC",
                collateral_amount=1.2,
                debt=42000.0,
                price=65000.0,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0x7890abcdef1234567890abcdef12345678901a2b",
                collateral_type="BTC",
                collateral_amount=0.8,
                debt=25000.0,
                price=65000.0,
                min_collateral_ratio=1.5,
            ),
            # SOL Positions
            CdpPosition(
                owner="0x890abcdef1234567890abcdef12345678901a2b3c",
                collateral_type="SOL",
                collateral_amount=450.0,
                debt=35000.0,
                price=145.0,
                min_collateral_ratio=1.6,
            ),
            CdpPosition(
                owner="0x90abcdef1234567890abcdef12345678901a2b3c4d",
                collateral_type="SOL",
                collateral_amount=680.0,
                debt=52000.0,
                price=145.0,
                min_collateral_ratio=1.6,
            ),
            CdpPosition(
                owner="0x0abcdef1234567890abcdef12345678901a2b3c4d5e",
                collateral_type="SOL",
                collateral_amount=200.0,
                debt=14500.0,
                price=145.0,
                min_collateral_ratio=1.6,
            ),
            # HYPE Positions
            CdpPosition(
                owner="0xabcdef1234567890abcdef12345678901a2b3c4d5e6f",
                collateral_type="HYPE",
                collateral_amount=1200.0,
                debt=32000.0,
                price=28.0,
                min_collateral_ratio=1.3,
            ),
            CdpPosition(
                owner="0xbcdef1234567890abcdef12345678901a2b3c4d5e6f78",
                collateral_type="HYPE",
                collateral_amount=850.0,
                debt=18000.0,
                price=28.0,
                min_collateral_ratio=1.3,
            ),
            CdpPosition(
                owner="0xcdef1234567890abcdef12345678901a2b3c4d5e6f7890",
                collateral_type="HYPE",
                collateral_amount=3500.0,
                debt=72000.0,
                price=28.0,
                min_collateral_ratio=1.3,
            ),
            # AVAX Positions
            CdpPosition(
                owner="0xdef1234567890abcdef12345678901a2b3c4d5e6f7890ab",
                collateral_type="AVAX",
                collateral_amount=320.0,
                debt=9800.0,
                price=38.0,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0xef1234567890abcdef12345678901a2b3c4d5e6f7890abcd",
                collateral_type="AVAX",
                collateral_amount=580.0,
                debt=17500.0,
                price=38.0,
                min_collateral_ratio=1.5,
            ),
            # ARB Positions
            CdpPosition(
                owner="0xf1234567890abcdef12345678901a2b3c4d5e6f7890abcdef",
                collateral_type="ARB",
                collateral_amount=8500.0,
                debt=12000.0,
                price=0.82,
                min_collateral_ratio=1.7,
            ),
            CdpPosition(
                owner="0x1234567890abcdef12345678901a2b3c4d5e6f7890abcdef12",
                collateral_type="ARB",
                collateral_amount=15000.0,
                debt=18500.0,
                price=0.82,
                min_collateral_ratio=1.7,
            ),
            # OP Positions
            CdpPosition(
                owner="0x234567890abcdef12345678901a2b3c4d5e6f7890abcdef123",
                collateral_type="OP",
                collateral_amount=4200.0,
                debt=6500.0,
                price=1.95,
                min_collateral_ratio=1.6,
            ),
            CdpPosition(
                owner="0x34567890abcdef12345678901a2b3c4d5e6f7890abcdef1234",
                collateral_type="OP",
                collateral_amount=7800.0,
                debt=12000.0,
                price=1.95,
                min_collateral_ratio=1.6,
            ),
            # LINK Positions
            CdpPosition(
                owner="0x4567890abcdef12345678901a2b3c4d5e6f7890abcdef12345",
                collateral_type="LINK",
                collateral_amount=2500.0,
                debt=32000.0,
                price=14.5,
                min_collateral_ratio=1.5,
            ),
            CdpPosition(
                owner="0x567890abcdef12345678901a2b3c4d5e6f7890abcdef123456",
                collateral_type="LINK",
                collateral_amount=1800.0,
                debt=22000.0,
                price=14.5,
                min_collateral_ratio=1.5,
            ),
            # UNI Positions
            CdpPosition(
                owner="0x67890abcdef12345678901a2b3c4d5e6f7890abcdef1234567",
                collateral_type="UNI",
                collateral_amount=3200.0,
                debt=18000.0,
                price=7.2,
                min_collateral_ratio=1.6,
            ),
            CdpPosition(
                owner="0x7890abcdef12345678901a2b3c4d5e6f7890abcdef12345678",
                collateral_type="UNI",
                collateral_amount=5600.0,
                debt=28000.0,
                price=7.2,
                min_collateral_ratio=1.6,
            ),
            # MATIC Positions
            CdpPosition(
                owner="0x890abcdef12345678901a2b3c4d5e6f7890abcdef123456789",
                collateral_type="MATIC",
                collateral_amount=18500.0,
                debt=11500.0,
                price=0.68,
                min_collateral_ratio=1.7,
            ),
            # ATOM Positions
            CdpPosition(
                owner="0x90abcdef12345678901a2b3c4d5e6f7890abcdef1234567890a",
                collateral_type="ATOM",
                collateral_amount=2100.0,
                debt=14000.0,
                price=8.5,
                min_collateral_ratio=1.6,
            ),
            # NEAR Positions
            CdpPosition(
                owner="0x0abcdef12345678901a2b3c4d5e6f7890abcdef1234567890ab",
                collateral_type="NEAR",
                collateral_amount=8200.0,
                debt=24500.0,
                price=3.8,
                min_collateral_ratio=1.6,
            ),
            # SUI Positions (newer chain)
            CdpPosition(
                owner="0xabcdef12345678901a2b3c4d5e6f7890abcdef1234567890abc",
                collateral_type="SUI",
                collateral_amount=12000.0,
                debt=28000.0,
                price=2.45,
                min_collateral_ratio=1.7,
            ),
            # APT Positions (newer chain)
            CdpPosition(
                owner="0xbcdef12345678901a2b3c4d5e6f7890abcdef1234567890abcd",
                collateral_type="APT",
                collateral_amount=3800.0,
                debt=26000.0,
                price=7.8,
                min_collateral_ratio=1.6,
            ),
            # INJ Positions (trending DeFi)
            CdpPosition(
                owner="0xcdef12345678901a2b3c4d5e6f7890abcdef1234567890abcde",
                collateral_type="INJ",
                collateral_amount=1500.0,
                debt=32000.0,
                price=24.5,
                min_collateral_ratio=1.5,
            ),
            # TIA Positions (Celestia - newer)
            CdpPosition(
                owner="0xdef12345678901a2b3c4d5e6f7890abcdef1234567890abcdef",
                collateral_type="TIA",
                collateral_amount=4200.0,
                debt=18500.0,
                price=5.2,
                min_collateral_ratio=1.7,
            ),
        ]
        return dummy_data

    # Minimal ABIs
    TROVE_MANAGER_ABI = [
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "_troveId",
                    "type": "uint256",
                }
            ],
            "name": "getLatestTroveData",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "entireColl",
                    "type": "uint256",
                },
                {
                    "internalType": "uint256",
                    "name": "entireDebt",
                    "type": "uint256",
                },
                {
                    "internalType": "uint256",
                    "name": "redistColl",
                    "type": "uint256",
                },
                {
                    "internalType": "uint256",
                    "name": "redistDebt",
                    "type": "uint256",
                },
                {
                    "internalType": "uint256",
                    "name": "annualInterestRate",
                    "type": "uint256",
                },
                {
                    "internalType": "uint256",
                    "name": "lastInterestRateAdjTime",
                    "type": "uint256",
                },
            ],
            "stateMutability": "view",
            "type": "function",
        }
    ]
    TROVE_NFT_ABI = [
        {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [
                {"internalType": "uint256", "name": "", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "index", "type": "uint256"}
            ],
            "name": "tokenByIndex",
            "outputs": [
                {"internalType": "uint256", "name": "", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "tokenId", "type": "uint256"}
            ],
            "name": "ownerOf",
            "outputs": [
                {"internalType": "address", "name": "", "type": "address"}
            ],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    PRICE_FEED_ABI = [
        {
            "inputs": [],
            "name": "latestRoundData",
            "outputs": [
                {"internalType": "uint80", "name": "roundId", "type": "uint80"},
                {"internalType": "int256", "name": "answer", "type": "int256"},
                {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
                {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
                {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"},
            ],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [
                {"internalType": "uint8", "name": "", "type": "uint8"}
            ],
            "stateMutability": "view",
            "type": "function",
        },
    ]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    positions: List[CdpPosition] = []

    # Determine collaterals
    collaterals_to_fetch = (
        collateral_types if collateral_types else list(collateral_configs.keys())
    )

    for symbol in collaterals_to_fetch:
        cfg = collateral_configs.get(symbol)
        if not cfg:
            logger.warning("No configuration for '%s'; skipping", symbol)
            continue
        try:
            tm_addr = w3.to_checksum_address(cfg["trove_manager"])
            nft_addr = w3.to_checksum_address(cfg["trove_nft"])
            pf_addr = w3.to_checksum_address(cfg["price_feed"])
        except Exception as addr_err:
            logger.warning("Invalid address for %s: %s", symbol, addr_err)
            continue

        # Instantiate contracts
        trove_nft = w3.eth.contract(address=nft_addr, abi=TROVE_NFT_ABI)
        trove_manager = w3.eth.contract(address=tm_addr, abi=TROVE_MANAGER_ABI)
        price_feed = w3.eth.contract(address=pf_addr, abi=PRICE_FEED_ABI)

        # Fetch total number of troves
        try:
            total_troves = trove_nft.functions.totalSupply().call()
        except Exception as ex:
            logger.warning("Failed to fetch totalSupply for %s: %s", symbol, ex)
            total_troves = 0

        # Determine how many to fetch
        num_to_fetch = total_troves
        if max_troves_per_collateral is not None and total_troves > max_troves_per_collateral:
            num_to_fetch = max_troves_per_collateral

        # Fetch price once
        try:
            round_data = price_feed.functions.latestRoundData().call()
            price_decimals = price_feed.functions.decimals().call()
            answer = round_data[1]
            price = float(answer) / (10 ** price_decimals) if answer > 0 else 0.0
        except Exception as price_ex:
            logger.warning("Failed to fetch price for %s: %s", symbol, price_ex)
            price = 0.0

        # Iterate through troves
        for index in range(num_to_fetch):
            try:
                trove_id = trove_nft.functions.tokenByIndex(index).call()
                owner_addr = trove_nft.functions.ownerOf(trove_id).call()
                trove_data = trove_manager.functions.getLatestTroveData(trove_id).call()
                entire_coll = trove_data[0]
                entire_debt = trove_data[1]
                coll_decimals = cfg.get("decimals", 18)
                debt_decimals = cfg.get("debt_decimals", 18)
                collateral_amount = float(entire_coll) / (10 ** coll_decimals)
                debt_amount = float(entire_debt) / (10 ** debt_decimals)
                mcr = cfg.get("min_collateral_ratio", 1.0)
                positions.append(
                    CdpPosition(
                        owner=owner_addr,
                        collateral_type=symbol,
                        collateral_amount=collateral_amount,
                        debt=debt_amount,
                        price=price,
                        min_collateral_ratio=mcr,
                    )
                )
            except Exception as trove_err:
                logger.warning("Error retrieving trove index %s for %s: %s", index, symbol, trove_err)
                continue

    return positions


def fetch_hyperliquid_market(
    symbols: List[str],
    *,
    info_url: Optional[str] = None,
    session: Any | None = None,
) -> Dict[str, Dict[str, float | None]]:
    """
    Fetch market data for specified symbols from Hyperliquid.

    This function attempts to use Hyperliquid's public "info" endpoint to
    retrieve minimal market statistics. At the time of writing, Hyperliquid's
    API is primarily designed for order routing and user‑specific queries. The
    generic market data (open interest, funding rates, liquidity) is not
    exposed directly via a simple REST endpoint. Instead, the function
    demonstrates how to query the `activeAssetData` info call, which
    returns the current mark price for a given coin. Other metrics are
    returned as ``None`` and should be populated by calling the appropriate
    endpoints once they become available.

    Parameters
    ----------
    symbols : list of str
        Ticker symbols (e.g. ["ETH", "BTC", "HYPE"]).
    info_url : str, optional
        Base URL for the Hyperliquid info API. If not provided, the
        environment variable ``HYPERLIQUID_INFO_URL`` is used, or it
        defaults to ``https://api.hyperliquid.xyz/info``. Note that some
        node providers expose the info endpoint at different subdomains.
    session : optional
        Optional HTTP session object for connection pooling.

    Returns
    -------
    market_data : dict
        A mapping from symbol -> metrics dict containing:
        - open_interest (None by default; not available from activeAssetData)
        - funding_rate (None by default)
        - skew (None by default)
        - realized_volatility (None by default)
        - best_bid_depth (None by default)
        - best_ask_depth (None by default)
        - mark_price (float | None)

    Notes
    -----
    The Hyperliquid API uses a POST request to the `/info` endpoint with a
    JSON payload. For example, to fetch active asset data:

    .. code-block:: python

        payload = {
            "type": "activeAssetData",
            "user": "0x0000000000000000000000000000000000000000",
            "coin": "ETH"
        }
        response = session.post(info_url, json=payload)
        data = response.json()
        mark_price = float(data.get("markPx", 0))

    Other metrics (open interest, funding rates) may require different
    `type` values or external data services. See Hyperliquid's developer
    documentation for the latest endpoints.
    """
    if not info_url:
        info_url = os.getenv("HYPERLIQUID_INFO_URL", "https://api.hyperliquid.xyz/info")
    if session is None:
        session = requests.Session()
    market_data: Dict[str, Dict[str, float | None]] = {}
    for sym in symbols:
        symbol = sym.upper()
        metrics: Dict[str, float | None] = {
            "open_interest": None,
            "funding_rate": None,
            "skew": None,
            "realized_volatility": None,
            "best_bid_depth": None,
            "best_ask_depth": None,
            "mark_price": None,
        }
        try:
            payload = {
                "type": "activeAssetData",
                # Use a zero address as user; activeAssetData requires a user
                # address but only mark price is relevant for our purposes.
                "user": "0x0000000000000000000000000000000000000000",
                "coin": symbol,
            }
            resp = session.post(info_url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Mark price may come as string; convert to float if possible
            mark_px = data.get("markPx") or data.get("mark_px")
            try:
                metrics["mark_price"] = float(mark_px) if mark_px is not None else None
            except (ValueError, TypeError):
                metrics["mark_price"] = None
        except requests.RequestException as req_err:
            logger.warning(
                "HTTP error fetching Hyperliquid market data for %s: %s",
                symbol,
                req_err,
            )
        except Exception as ex:
            logger.warning(
                "Unexpected error processing Hyperliquid data for %s: %s", symbol, ex
            )
        market_data[symbol] = metrics
    return market_data