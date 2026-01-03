# Monthly Stock Drops Analyzer — Streamlit + Plotly

Dashboard to analyze monthly returns, frequency of drops below a threshold, drawdowns, streaks, and seasonality.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd stock-drops-dashboard
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Option 1: Using Streamlit command (Recommended)

```bash
streamlit run app/main.py
```

This will:
- Start the Streamlit server (usually on `http://localhost:8501`)
- Automatically open your browser
- Show the dashboard interface

### Option 2: Windows - Double-click `run.bat`

Simply double-click the `run.bat` file in the project root. This will:
- Activate the virtual environment (if `.venv` exists)
- Start Streamlit on port 8501
- Open your browser automatically

### Option 3: Using Python module

```bash
python -m streamlit run app/main.py
```

## Accessing the Dashboard

Once running, the dashboard will be available at:
- **Local URL:** `http://localhost:8501`
- **Network URL:** (shown in terminal, allows access from other devices on your network)

## Stopping the Application

Press `Ctrl+C` in the terminal/command prompt where Streamlit is running.

## Troubleshooting

**Issue: "streamlit: command not found"**
- Make sure you've activated your virtual environment
- Verify Streamlit is installed: `pip list | grep streamlit`
- Try: `python -m streamlit run app/main.py`

**Issue: Port 8501 already in use**
- Use a different port: `streamlit run app/main.py --server.port 8502`
- Or stop the other process using port 8501

**Issue: Import errors**
- Ensure you're in the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that Python can find the `app` module (the bootstrap code in `main.py` should handle this)

## Features

- **Multiple data sources**: Load data from yfinance or upload CSV files
- **Monthly returns analysis**: Calculate and visualize period returns
- **Threshold analysis**: Count periods below a drop threshold
- **Drawdown tracking**: Visualize accumulated drawdowns from peaks
- **Seasonality heatmap**: Year × Month return patterns
- **Event tracking**: List and export periods that breach the threshold

## Project Structure

```
app/
├── core/          # Core calculations (returns, drawdown, stats)
├── data/          # Data loading (yfinance, CSV)
├── ui/            # UI components (sidebar, tabs, components)
├── viz/           # Visualization functions (Plotly charts)
└── main.py        # Main application entry point
```
