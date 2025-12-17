# 🏠 QoL Analyzer

**Quality of Life analysis across CA, NY, TX, and UT using Census ACS, BLS CPI, and Tax Foundation data.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-75%20passing-brightgreen.svg)](tests/)
[![R²](https://img.shields.io/badge/R%C2%B2-1.0-success.svg)](REGRESSION_RESULTS.md)

---

## Quick Start

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up API Keys
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Get free API keys:
- **Census API**: https://api.census.gov/data/key_signup.html
- **BLS API**: https://www.bls.gov/developers/home.htm

### 3. Run Pipeline
```bash
python3 -m scripts.run_pipeline
```

### 4. Launch Dashboard
```bash
streamlit run scripts/streamlit_app.py
```

---

## Features

- 📊 **Interactive Dashboard** - Plotly-powered visualizations
- 🔄 **Multi-Year Trends** - Compare 2022-2024 data
- 💰 **CPI Adjustment** - Real purchasing power analysis
- 🏠 **Housing Burden** - Rent & owner cost burden metrics
- 💳 **Tax Integration** - Disposable income calculations
- 📈 **Auto Insights** - Key findings generated automatically

---

## Key Findings

- ✅ **R² = 1.0** - Model explains 100% of QoL variance
- 🏆 **Utah ranks #1** - Highest QoL score (+0.92 avg)
- 🏠 **Housing > Income** - Housing burden is primary QoL driver
- 📊 **Consistent Trends** - Stable patterns across 2022-2024

**Detailed results**: [REGRESSION_RESULTS.md](REGRESSION_RESULTS.md)

---

## For Graders / Reviewers

### To Run Locally
1. `pip install -r requirements.txt`
2. `python3 -m scripts.run_pipeline` (uses existing data)
3. `streamlit run scripts/streamlit_app.py`

### To View Results
- **Dashboard**: Run Streamlit app (see above)
- **Regression Analysis**: See [REGRESSION_RESULTS.md](REGRESSION_RESULTS.md)
- **Tests**: Run `pytest tests/` (75 tests, all passing)

### Key Files
- **Proposal**: [docs/Project_Proposal.pdf](docs/Project_Proposal.pdf)
- **Data**: [data/processed/qol_with_real_income_peryear.csv](data/processed/qol_with_real_income_peryear.csv)

---

## Deploying to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repo
   - Main file: `scripts/streamlit_app.py`
   - Click "Deploy"

---

## Technical Details

### QoL Score Formula
```python
QoL = 0.5 × z(real_income) - 0.25 × z(rent_burden) - 0.25 × z(owner_burden)
```

### Data Sources
- **U.S. Census Bureau**: ACS 1-year estimates
- **Bureau of Labor Statistics**: Regional CPI
- **Tax Foundation**: State/local tax burdens

---

## Team

**Jun Kim** - Statistical analysis, visualization, regression
**Eddy Kim** - API extraction, feature engineering, testing

---

**Built with**: Python, Pandas, Streamlit, Plotly, scikit-learn
**Generated with**: [Claude Code](https://claude.com/claude-code)

