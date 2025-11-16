# Felix Monitor - Quick Start Guide

## 🚀 Getting Started

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Pratham6392/Felix-monitor.git
cd Felix-monitor
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Or with user-level installation:
```bash
pip install --user -r requirements.txt
```

### Running the Dashboard

#### Option 1: Using the convenience script (Recommended)
```bash
python run_dashboard.py
```

#### Option 2: Direct Streamlit command
```bash
streamlit run felix_monitor/app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`.

## 🎨 Features

### Modern Dark UI
- Professional gradient background
- Smooth animations and transitions
- Interactive charts with Plotly
- Real-time data updates

### Risk Analysis
- **Liquidation Scenarios**: Visualize positions at risk under different price shocks
- **Bad Debt Projections**: Estimate potential bad debt by shock level
- **Liquidity Impact**: Analyze market depth vs. liquidation amounts
- **Position Monitoring**: Track all CDP positions with health indicators

### Interactive Controls

**Sidebar Configuration:**
- Select multiple collateral assets (ETH, HYPE, BTC, SOL)
- Adjust price shock level (-50% to 0%)
- Set maximum troves to fetch
- Toggle stub data for testing

## 📊 Dashboard Overview

### Key Metrics Section
- Total Positions
- Total Collateral Value
- Total Debt
- Average Individual Collateral Ratio (ICR)

### Risk Analysis
- Liquidatable positions at current shock level
- At-risk collateral value
- Potential bad debt estimation

### Visualization Tabs
1. **Liquidation Analysis**: Interactive line charts showing liquidation risk
2. **Bad Debt Projections**: Bar charts for bad debt estimates
3. **Liquidity Impact**: Asset-by-asset liquidity analysis

### Positions Table
Detailed view of all CDP positions with:
- Owner address
- Collateral type and amount
- Current value and debt
- Individual Collateral Ratio (ICR)
- Health status indicators (🟢 Healthy, 🟡 Warning, 🔴 At Risk)

## 🔧 Configuration

### Using Real Data

To connect to live blockchain data:

1. Set environment variables:
```bash
# For Hyperliquid RPC
export HYPERLIQUID_RPC_URL="https://rpc.hyperliquid.xyz/evm"

# For Hyperliquid market data API
export HYPERLIQUID_INFO_URL="https://api.hyperliquid.xyz/info"
```

2. Update contract addresses in `felix_monitor/data_ingest.py`:
```python
collateral_configs = {
    "HYPE": {
        "trove_manager": "0xYOUR_TROVE_MANAGER_ADDRESS",
        "trove_nft": "0xYOUR_NFT_ADDRESS",
        "price_feed": "0xYOUR_PRICE_FEED_ADDRESS",
        ...
    }
}
```

3. Disable "Use Stub Data" in the dashboard sidebar

### Custom Styling

Edit `.streamlit/config.toml` to customize colors:
```toml
[theme]
primaryColor="#00d4ff"      # Accent color
backgroundColor="#0f0f23"    # Main background
secondaryBackgroundColor="#1a1a2e"  # Cards/containers
textColor="#ffffff"          # Text color
```

## 🎯 CLI Version

For command-line usage without the web UI:

```bash
python -m felix_monitor.dashboard --symbols ETH HYPE --shock -0.2
```

Options:
- `--symbols`: Space-separated list of collateral types
- `--shock`: Price shock level as decimal (e.g., -0.2 for -20%)

## 🐛 Troubleshooting

### Streamlit not found
If you see "No module named streamlit", ensure the Scripts directory is in your PATH:
```bash
# Windows (add to system PATH)
C:\Users\YOUR_USERNAME\AppData\Roaming\Python\Python312\Scripts

# Or use python -m
python -m streamlit run felix_monitor/app.py
```

### Port already in use
If port 8501 is busy, specify a different port:
```bash
streamlit run felix_monitor/app.py --server.port=8502
```

### No data showing
1. Make sure "Use Stub Data" is checked for testing
2. Check console for error messages
3. Verify environment variables are set correctly

## 📚 Next Steps

- **Integrate Real APIs**: Replace stub data with live Felix Protocol and Hyperliquid APIs
- **Add Alerts**: Set up notifications for high-risk scenarios
- **Historical Data**: Track trends over time
- **Export Reports**: Generate PDF/CSV reports

## 💡 Tips

- Use the refresh button to update data
- Hover over charts for detailed values
- Expand "Market Data Details" for additional metrics
- Adjust shock level to see different risk scenarios

## 🤝 Contributing

Feel free to open issues or submit pull requests to improve the dashboard!

---

**Built with ❤️ for the Felix Protocol community**

