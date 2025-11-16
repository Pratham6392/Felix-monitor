# Felix Monitor - Deployment Guide

## 🚀 Streamlit Cloud Deployment

### Quick Deploy

1. **Visit:** https://share.streamlit.io/deploy
2. **Sign in** with your GitHub account
3. **Fill in the deployment form:**
   - **Repository:** `Pratham6392/Felix-monitor`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py` ⚠️ **IMPORTANT: Use this file!**
4. **Click "Deploy"**

### Why `streamlit_app.py`?

The `streamlit_app.py` file is the entry point for Streamlit Cloud. It properly sets up the Python path and imports the main application from the `felix_monitor` package.

**DO NOT use:** `felix_monitor/app.py` directly - this will cause import errors!

### Deployment Configuration

The repository includes:
- ✅ `streamlit_app.py` - Entry point for Streamlit Cloud
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System-level dependencies (if needed)
- ✅ `.streamlit/config.toml` - Dark theme configuration

### Expected Deployment Time

- **Build time:** 2-3 minutes
- **First load:** 10-20 seconds

### After Deployment

Your app will be available at:
```
https://pratham6392-felix-monitor-xxxxx.streamlit.app
```

### Troubleshooting

#### ModuleNotFoundError
- **Solution:** Make sure you're using `streamlit_app.py` as the main file path, NOT `felix_monitor/app.py`

#### Import Errors
- **Solution:** The `streamlit_app.py` file handles path setup automatically

#### Missing Dependencies
- **Solution:** All dependencies are in `requirements.txt` and will be installed automatically

### Auto-Redeployment

Streamlit Cloud automatically redeploys when you push to the `main` branch on GitHub. No manual intervention needed!

### Local Testing

Before deploying, test locally:
```bash
streamlit run streamlit_app.py
```

Or use the convenience script:
```bash
python run_dashboard.py
```

## 🔧 Alternative Deployment Options

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t felix-monitor .
docker run -p 8501:8501 felix-monitor
```

### Heroku Deployment

1. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

2. Create `Procfile`:
```
web: sh setup.sh && streamlit run streamlit_app.py
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### AWS EC2 / VPS Deployment

1. SSH into your server
2. Clone the repository
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run with PM2 or systemd:
```bash
streamlit run streamlit_app.py --server.port=8501
```

## 📊 Monitoring

After deployment, monitor your app:
- **Streamlit Cloud Dashboard:** View logs, metrics, and usage
- **GitHub Actions:** Set up CI/CD for automated testing
- **Error Tracking:** Check Streamlit Cloud logs for any issues

## 🔐 Environment Variables

For production deployment with real APIs:

1. Go to Streamlit Cloud dashboard
2. Click "Manage app" → "Settings" → "Secrets"
3. Add your secrets:
```toml
HYPERLIQUID_RPC_URL = "your_rpc_url"
HYPERLIQUID_INFO_URL = "your_info_url"
FELIX_SUBGRAPH_URL = "your_subgraph_url"
```

4. Access in code:
```python
import streamlit as st
rpc_url = st.secrets.get("HYPERLIQUID_RPC_URL", "default_value")
```

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `streamlit_app.py` exists at root
- [ ] `requirements.txt` is up to date
- [ ] Signed in to Streamlit Cloud
- [ ] Correct repository and branch selected
- [ ] Main file path set to `streamlit_app.py`
- [ ] App deployed successfully
- [ ] Public URL works
- [ ] All features tested

## 🎉 Success!

Your Felix Monitor dashboard should now be live and accessible to anyone with the URL!

