<div align="center">
  <img src="Header.png" alt="CryptoChain Analyzer Dashboard" width="100%"/>
</div>

---

# CryptoChain Analyzer Dashboard

A full-stack Bitcoin blockchain analytics dashboard built with Python and Streamlit, developed as a university project for the Cryptography course at UAX (2025–26). It connects to public blockchain APIs — no API key required — and presents live on-chain data through seven analytical modules covering Proof of Work, difficulty analysis, AI anomaly detection, Merkle proofs, and security modeling.

## What Was Built

| Module | Description |
|---|---|
| **M1 — PoW Monitor** | Visualizes mining difficulty, estimated hash rate, and inter-block time distribution using live Bitcoin data from the Blockstream API. |
| **M2 — Block Header Analyzer** | Parses raw 80-byte block headers, manually verifies Proof of Work with `hashlib`, and counts leading zero bits to explain the target relationship. |
| **M3 — Difficulty History** | Charts the full difficulty adjustment history across 2016-block epochs, showing period ratios and adjustment statistics. |
| **M4 — Anomaly Detector (AI)** | Unsupervised anomaly detection on block inter-arrival times using an exponential baseline model and `IsolationForest`. Evaluated with KS goodness-of-fit and synthetic precision / recall / F1. |
| **M5 — Merkle Proof Verifier** | Rebuilds a transaction's Merkle path from raw block data and verifies it against the block header Merkle root. |
| **M6 — Security Score** | Estimates 51% attack cost (energy-only) and plots Nakamoto double-spend probability curves for configurable confirmation depths. |
| **M7 — Difficulty Predictor (AI)** | Supervised `RandomForestRegressor` that predicts the next difficulty adjustment using chronological holdout evaluation — contrasts supervised vs. unsupervised AI approaches. |

## Tech Stack

- **Python 3.11+** · **Streamlit** · **Plotly** · **Pandas** · **scikit-learn**
- **Blockstream API** (primary) · **Blockchain.info** (fallback for aggregated difficulty history)
- Dark theme · Share Tech Mono / Rajdhani fonts · Crypto color palette · 60 s auto-refresh

## How to Run

```bash
# 1. Clone the repository
git clone https://github.com/rubenelices/BLOCKCHAIN_DASHBOARD_RER.git
cd BLOCKCHAIN_DASHBOARD_RER

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`. No API keys or `.env` file needed — all data is fetched from public endpoints.

## Project Structure

```text
template-blockchain-dashboard/
|-- app.py                        # Streamlit entry point & sidebar navigation
|-- requirements.txt
|-- api/
|   `-- blockchain_client.py      # All API calls (Blockstream + Blockchain.info)
|-- modules/
|   |-- m1_pow_monitor.py
|   |-- m2_block_header.py
|   |-- m3_difficulty_history.py
|   |-- m4_ai_component.py        # IsolationForest anomaly detector
|   |-- m5_merkle_proof.py
|   |-- m6_security_score.py
|   `-- m7_difficulty_predictor.py
|-- config/
|-- prompts/
`-- report/
    `-- report.pdf
```

---

# Blockchain Dashboard Project

Use this repository to build your blockchain dashboard project.
Update this README every week.

## Student Information

| Field | Value |
|---|---|
| Student Name | Ruben Elices Rodriguez |
| GitHub Username | rubenelices |
| Project Title | Blockchain_dashboard |
| Chosen AI Approach | M4 option 2, Anomaly Detector |

## Module Tracking

Use one of these values: `Not started`, `In progress`, `Done`

| Module | What it should include | Status |
|---|---|---|
| M1 | Proof of Work Monitor | Done |
| M2 | Block Header Analyzer | Done |
| M3 | Difficulty History | Done |
| M4 | AI Component | Done |
| M5 | Merkle Proof Verifier | Done |
| M6 | Security Score | Done |
| M7 | Second AI Approach | Done |

## Current Progress

- M1, M2, M3 complete with Streamlit dashboard. Tested with real Bitcoin data from Blockstream API.
- Dashboard features: dark theme, crypto color palette, live data refresh (60s), interactive Plotly charts.
- M1: difficulty visualization, hash rate, inter-block time histogram.
- M2: block header parsing, manual PoW verification with hashlib, leading zero bits count.
- M3: difficulty adjustment history, period ratios, aggregate statistics.
- M4: anomaly detector on Bitcoin block inter-arrival times using an exponential baseline and IsolationForest.
- M4 evaluation: KS goodness-of-fit test plus synthetic anomaly precision, recall, and F1-score.
- M5: Merkle proof verifier that rebuilds a transaction path to the block header Merkle root.
- M6: security score with energy-only 51% attack cost and Nakamoto double-spend probability curves.
- M7: supervised difficulty adjustment predictor with chronological holdout metrics.
- API client expanded: get_block_header_hex, get_block_txids, get_block_by_height.

## Next Step

- Add final report in report/report.pdf before the deadline.
- Run a clean final test of installation and dashboard startup.

## Main Problem or Blocker

- None currently.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```text
template-blockchain-dashboard/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- app.py
|-- api/
|   `-- blockchain_client.py
`-- modules/
    |-- m1_pow_monitor.py
    |-- m2_block_header.py
    |-- m3_difficulty_history.py
    |-- m4_ai_component.py
    |-- m5_merkle_proof.py
    |-- m6_security_score.py
    `-- m7_difficulty_predictor.py
```

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-29 20:44 CEST
Status: Amber

Strength:
- The dashboard already integrates M1, M2, and M3 clearly in app.py.

Improve now:
- M4 is not yet visibly integrated into the dashboard navigation.

Next step:
- Add a visible M4 entry in app.py so the AI module skeleton is also accessible from the dashboard.
<!-- student-repo-auditor:teacher-feedback:end -->
