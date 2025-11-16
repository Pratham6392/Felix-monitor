"""
Modern Web UI for Felix Monitor.

This module provides a professional dark-themed dashboard using Streamlit
for monitoring Felix Protocol CDPs and Hyperliquid market risks.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# Use absolute imports for Streamlit compatibility
from felix_monitor.data_ingest import fetch_felix_positions, fetch_hyperliquid_market
from felix_monitor.data_fusion import fuse_data
from felix_monitor.risk_engine import (
    compute_liquidation_stats,
    compute_liquidity_impact,
    compute_perp_cdp_correlation,
)


# Page configuration
st.set_page_config(
    page_title="Felix Monitor | Risk Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom CSS for professional dark theme
def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Main background with gradient */
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
            border-right: 1px solid #2a2a3e;
        }
        
        /* Card-like containers */
        .stMetric {
            background: rgba(26, 26, 46, 0.6);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #00d4ff !important;
            font-weight: 600;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }
        
        /* Metric labels */
        [data-testid="stMetricLabel"] {
            color: #8b9dc3 !important;
            font-size: 0.9rem;
        }
        
        /* Metric values */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 600;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #00d4ff 0%, #0099cc 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stMultiSelect > div > div {
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            color: white;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: rgba(26, 26, 46, 0.6);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Tables */
        .dataframe {
            background: rgba(26, 26, 46, 0.6) !important;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: rgba(0, 212, 100, 0.1);
            border-left: 4px solid #00d464;
        }
        
        .stError {
            background: rgba(255, 50, 50, 0.1);
            border-left: 4px solid #ff3232;
        }
        
        .stWarning {
            background: rgba(255, 165, 0, 0.1);
            border-left: 4px solid #ffa500;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0f0f23;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00d4ff;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #00a3cc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_header():
    """Create the dashboard header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
            <h1 style='margin-bottom: 0;'>⚡ Felix Monitor</h1>
            <p style='color: #8b9dc3; font-size: 1.1rem; margin-top: 0;'>
                Cross-Asset Risk & Trading Monitor for Felix Protocol on Hyperliquid
            </p>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div style='text-align: right; padding-top: 20px;'>
                <span style='color: #00d464; font-size: 1.5rem;'>●</span>
                <span style='color: #8b9dc3;'> Live</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def create_liquidation_chart(stats: Dict[float, Dict[str, Any]]) -> go.Figure:
    """Create an interactive liquidation statistics chart."""
    shock_levels = list(stats.keys())
    liquidatable_counts = [stats[shock]["liquidatable_count"] for shock in shock_levels]
    at_risk_collateral = [stats[shock]["at_risk_collateral"] for shock in shock_levels]
    bad_debt = [stats[shock]["bad_debt"] for shock in shock_levels]

    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=[s * 100 for s in shock_levels],
            y=liquidatable_counts,
            mode="lines+markers",
            name="Liquidatable Positions",
            line=dict(color="#00d4ff", width=3),
            marker=dict(size=8, symbol="circle"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[s * 100 for s in shock_levels],
            y=at_risk_collateral,
            mode="lines+markers",
            name="At-Risk Collateral ($)",
            line=dict(color="#ff6b6b", width=3),
            marker=dict(size=8, symbol="diamond"),
            yaxis="y2",
        )
    )

    # Update layout
    fig.update_layout(
        title="Liquidation Risk Under Price Shocks",
        xaxis=dict(
            title="Price Shock (%)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="#8b9dc3",
        ),
        yaxis=dict(
            title="Number of Positions",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="#00d4ff",
        ),
        yaxis2=dict(
            title="Collateral Value ($)",
            overlaying="y",
            side="right",
            color="#ff6b6b",
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(26, 26, 46, 0.6)",
        font=dict(color="#ffffff"),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0, 0, 0, 0.3)",
        ),
    )

    return fig


def create_bad_debt_chart(stats: Dict[float, Dict[str, Any]]) -> go.Figure:
    """Create a bad debt visualization chart."""
    shock_levels = list(stats.keys())
    bad_debt = [stats[shock]["bad_debt"] for shock in shock_levels]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[f"{s*100:+.0f}%" for s in shock_levels],
            y=bad_debt,
            marker=dict(
                color=bad_debt,
                colorscale="Reds",
                showscale=True,
                colorbar=dict(title="Bad Debt ($)"),
            ),
            text=[f"${bd:,.0f}" for bd in bad_debt],
            textposition="outside",
        )
    )

    fig.update_layout(
        title="Potential Bad Debt by Shock Level",
        xaxis=dict(
            title="Price Shock",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="#8b9dc3",
        ),
        yaxis=dict(
            title="Bad Debt ($)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="#8b9dc3",
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(26, 26, 46, 0.6)",
        font=dict(color="#ffffff"),
        showlegend=False,
    )

    return fig


def create_liquidity_impact_chart(impact: Dict[str, float]) -> go.Figure:
    """Create liquidity impact visualization."""
    if not impact:
        return None

    symbols = list(impact.keys())
    values = list(impact.values())

    fig = go.Figure()

    colors = ["#00d4ff" if v < 0.1 else "#ffa500" if v < 0.3 else "#ff3232" for v in values]

    fig.add_trace(
        go.Bar(
            x=symbols,
            y=values,
            marker=dict(color=colors),
            text=[f"{v:.2%}" for v in values],
            textposition="outside",
        )
    )

    fig.update_layout(
        title="Liquidity Impact by Asset",
        xaxis=dict(
            title="Asset",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="#8b9dc3",
        ),
        yaxis=dict(
            title="Impact Ratio (Liquidation / Orderbook Depth)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="#8b9dc3",
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(26, 26, 46, 0.6)",
        font=dict(color="#ffffff"),
        showlegend=False,
    )

    return fig


def create_positions_table(positions: List[Any]) -> pd.DataFrame:
    """Create a DataFrame from CDP positions."""
    if not positions:
        return pd.DataFrame()

    data = []
    for pos in positions:
        data.append(
            {
                "Owner": pos.owner[:10] + "...",
                "Collateral": pos.collateral_type,
                "Amount": f"{pos.collateral_amount:,.2f}",
                "Value ($)": f"${pos.collateral_value:,.2f}",
                "Debt ($)": f"${pos.debt:,.2f}",
                "ICR": f"{pos.icr:.2f}x",
                "Min ICR": f"{pos.min_collateral_ratio:.2f}x",
                "Health": "🟢 Healthy" if pos.icr > pos.min_collateral_ratio * 1.5 else "🟡 Warning" if pos.icr > pos.min_collateral_ratio else "🔴 At Risk",
            }
        )

    return pd.DataFrame(data)


def main():
    """Main application entry point."""
    apply_custom_css()
    create_header()

    # Sidebar controls
    st.sidebar.markdown("## ⚙️ Configuration")
    st.sidebar.markdown("---")

    # Symbol selection
    available_symbols = [
        "ETH", "BTC", "SOL", "HYPE",  # Major tokens
        "AVAX", "ARB", "OP", "LINK",  # L1s and L2s
        "UNI", "MATIC", "ATOM", "NEAR",  # DeFi & Ecosystems
        "SUI", "APT", "INJ", "TIA"  # Newer chains
    ]
    selected_symbols = st.sidebar.multiselect(
        "Select Collateral Assets",
        available_symbols,
        default=["ETH", "BTC", "SOL", "HYPE"],
        help="Choose which collateral types to monitor",
    )

    # Shock level slider
    shock_level = st.sidebar.slider(
        "Price Shock Level (%)",
        min_value=-50,
        max_value=0,
        value=-20,
        step=5,
        help="Simulate a price drop scenario",
    ) / 100

    # Advanced settings
    with st.sidebar.expander("🔧 Advanced Settings"):
        max_troves = st.number_input(
            "Max Troves per Asset",
            min_value=1,
            max_value=1000,
            value=100,
            help="Limit number of positions to fetch",
        )
        use_stub_data = st.checkbox(
            "Use Stub Data",
            value=True,
            help="Use demo data instead of live blockchain data",
        )

    # Refresh button
    refresh = st.sidebar.button("🔄 Refresh Data", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: #8b9dc3; font-size: 0.9rem;'>
            <p>Felix Monitor v1.0</p>
            <p>Built for Hyperliquid</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main content
    if not selected_symbols:
        st.warning("⚠️ Please select at least one collateral asset from the sidebar.")
        return

    # Fetch data
    with st.spinner("🔍 Fetching data..."):
        try:
            # Fetch positions
            positions = fetch_felix_positions(
                collateral_types=selected_symbols,
                max_troves_per_collateral=max_troves,
                force_stub=use_stub_data,
            )

            # Fetch market data
            market_data = fetch_hyperliquid_market(selected_symbols)

            # Fuse data
            fused = fuse_data(positions, market_data)

            # Compute risk metrics
            stats = compute_liquidation_stats(fused)
            liquidity_impact = compute_liquidity_impact(fused, shock=shock_level)

        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.info("💡 Try enabling 'Use Stub Data' in Advanced Settings.")
            return

    # Display key metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_positions = len(positions)
        st.metric("Total Positions", total_positions, help="Number of active CDPs")

    with col2:
        total_collateral = sum(p.collateral_value for p in positions)
        st.metric(
            "Total Collateral",
            f"${total_collateral:,.0f}",
            help="Total USD value of all collateral",
        )

    with col3:
        total_debt = sum(p.debt for p in positions)
        st.metric("Total Debt", f"${total_debt:,.0f}", help="Total debt across all CDPs")

    with col4:
        avg_icr = sum(p.icr for p in positions) / len(positions) if positions else 0
        st.metric("Avg ICR", f"{avg_icr:.2f}x", help="Average Individual Collateral Ratio")

    st.markdown("---")

    # Risk Analysis Section
    st.markdown("### ⚠️ Risk Analysis")

    # Get current shock stats
    current_shock_stats = stats.get(shock_level, stats[min(stats.keys())])

    col1, col2, col3 = st.columns(3)

    with col1:
        liquidatable = current_shock_stats["liquidatable_count"]
        delta_color = "inverse" if liquidatable > 0 else "normal"
        st.metric(
            f"Liquidatable @ {shock_level*100:.0f}%",
            liquidatable,
            delta=f"{liquidatable} positions at risk",
            delta_color=delta_color,
        )

    with col2:
        at_risk = current_shock_stats["at_risk_collateral"]
        st.metric(
            "At-Risk Collateral",
            f"${at_risk:,.0f}",
            help="Total collateral value in at-risk positions",
        )

    with col3:
        bad_debt = current_shock_stats["bad_debt"]
        st.metric(
            "Potential Bad Debt",
            f"${bad_debt:,.0f}",
            delta=f"{(bad_debt/total_debt*100):.1f}% of total debt" if total_debt > 0 else "0%",
            delta_color="inverse",
        )

    st.markdown("---")

    # Charts
    tab1, tab2, tab3 = st.tabs(["📈 Liquidation Analysis", "💰 Bad Debt Projections", "💧 Liquidity Impact"])

    with tab1:
        st.plotly_chart(create_liquidation_chart(stats), use_container_width=True)

    with tab2:
        st.plotly_chart(create_bad_debt_chart(stats), use_container_width=True)

    with tab3:
        if liquidity_impact:
            st.plotly_chart(
                create_liquidity_impact_chart(liquidity_impact), use_container_width=True
            )
            st.info(
                "💡 **Interpretation:** Values < 10% indicate low impact, "
                "10-30% moderate impact, >30% high market impact."
            )
        else:
            st.info("No liquidations expected at current shock level.")

    st.markdown("---")

    # Positions Table
    st.markdown("### 📋 CDP Positions")
    positions_df = create_positions_table(positions)

    if not positions_df.empty:
        st.dataframe(positions_df, use_container_width=True, hide_index=True)
    else:
        st.info("No positions found for selected assets.")

    # Market Data Section
    with st.expander("📊 Market Data Details"):
        for symbol, metrics in market_data.items():
            st.markdown(f"**{symbol}**")
            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.write(f"Mark Price: ${metrics.get('mark_price', 'N/A')}")
            with metric_cols[1]:
                st.write(f"OI: ${metrics.get('open_interest', 'N/A'):,}" if metrics.get('open_interest') else "OI: N/A")
            with metric_cols[2]:
                st.write(f"Funding: {metrics.get('funding_rate', 'N/A')}" if metrics.get('funding_rate') else "Funding: N/A")
            with metric_cols[3]:
                st.write(f"Volatility: {metrics.get('realized_volatility', 'N/A')}" if metrics.get('realized_volatility') else "Volatility: N/A")


if __name__ == "__main__":
    main()

