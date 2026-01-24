# 📈 Kazakhstan Banking Statistics Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Plotly Dash](https://img.shields.io/badge/Plotly-Dash-3F4F75.svg)](https://dash.plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green.svg)](https://pandas.pydata.org/)
[![Bootstrap](https://img.shields.io/badge/Dash-Bootstrap-purple.svg)](https://dash-bootstrap-components.opensource.faculty.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive web dashboard for visualizing **Kazakhstan banking sector statistics** using data from the National Bank of Kazakhstan (NBK). Built with Plotly Dash featuring 7 interactive charts and deployed on Render.

---

## 🎯 Features

- **7 Interactive Charts** — Comprehensive banking sector analysis
- **Real-time Filtering** — Select banks, date ranges, and metrics
- **Multiple Data Views** — Line charts, bar charts, pie charts, stacked bars
- **Prudential Monitoring** — Track regulatory compliance with threshold indicators
- **Responsive Design** — Bootstrap-powered layout for all devices
- **Live Data** — Loads directly from GitHub-hosted Excel files

---

## 📊 Dashboard Charts

| # | Chart | Description |
|---|-------|-------------|
| 1 | **Bank Indicators Dynamics** | Assets, loans, provisions, capital over time |
| 2 | **Asset Quality - NPL** | Non-performing loans (90+ days overdue) |
| 3 | **Asset Quality - Provisions** | Loan portfolio vs IFRS provisions |
| 4 | **Loan Portfolio by Type** | Interbank, corporate, SME, retail breakdown |
| 5 | **Provisions by Aging** | Overdue buckets (1-30, 31-60, 61-90, 90+ days) |
| 6 | **Interest Margin** | Net interest income and margin trends |
| 7 | **Prudential Ratios** | Capital adequacy (k1, k2), liquidity with regulatory thresholds |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Plotly Dash |
| **UI Components** | Dash Bootstrap Components |
| **Visualization** | Plotly.js (go.Scatter, go.Bar, go.Pie) |
| **Data Processing** | Pandas |
| **Data Source** | Excel files (NBK statistics) |
| **Deployment** | Render / Gunicorn |

---

## 📁 Project Structure

```
├── main.py                   # Dash application (7 charts + callbacks)
├── New_Banking_Dash.ipynb    # Jupyter notebook for development
├── Data/                     # Banking statistics data
│   ├── FI2.xlsx              # Financial indicators by bank
│   ├── LP.xlsx               # Loan portfolio breakdown
│   ├── IM.xlsx               # Interest margin data
│   ├── PN.xlsx               # Prudential ratios
│   └── PN_threshold.xlsx     # Regulatory thresholds
├── Procfile                  # Deployment: web: gunicorn main:server
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+

### Installation

```bash
# Clone the repository
git clone https://github.com/daureny/Dashboard_PyCh_final.git
cd Dashboard_PyCh_final

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python main.py
```

Open your browser at `http://127.0.0.1:8050`

---

## 🌐 Deployment

The app is configured for Render/Heroku deployment:

```
# Procfile
web: gunicorn main:server
```

Data is loaded directly from GitHub raw URLs, so no local data files needed on the server.

---

## 📈 Data Source

Data sourced from **National Bank of Kazakhstan (NBK)**:
- [NBK Statistical Bulletin](https://nationalbank.kz/en/news/statisticheskiy-byulleten)
- Financial indicators for all licensed banks
- Monthly/quarterly reporting data

### Metrics Covered:
- Total Assets & Liabilities
- Loan Portfolios (by type and aging)
- IFRS Provisions
- Capital Adequacy Ratios (k1, k2)
- Liquidity Ratios
- Interest Income/Expense & Margins

---

## 🖼️ Screenshots

*Dashboard displays banking statistics in Russian, matching NBK official reporting format.*

---

## 🔮 Future Improvements

- [ ] Automated data fetching from NBK website
- [ ] English language toggle
- [ ] Additional charts (ROA, ROE, efficiency ratios)
- [ ] Bank comparison mode
- [ ] Export to PDF/Excel

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Dauren Yeleukenov**  
Risk Management & FinTech Professional  
- 20+ years in banking and financial services
- Former National Bank of Kazakhstan (2000-2011, 2016-2020)
- [LinkedIn](https://linkedin.com/in/yourprofile)

---

*Transforming NBK banking data into actionable insights with Python and Dash.*
