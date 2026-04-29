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
| M4 | AI Component | In progress |

## Current Progress

- M1, M2, M3 complete with Streamlit dashboard. Tested with real Bitcoin data from Blockstream API.
- Dashboard features: dark theme, crypto color palette, live data refresh (60s), interactive Plotly charts.
- M1: difficulty visualization, hash rate, inter-block time histogram.
- M2: block header parsing, manual PoW verification with hashlib, leading zero bits count.
- M3: difficulty adjustment history, period ratios, aggregate statistics.
- API client expanded: get_block_header_hex, get_block_txids, get_block_by_height.

## Next Step

- Implement M4 AI component (Anomaly Detector on inter-arrival times).
- Add optional modules M5, M6, M7.

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
    `-- m4_ai_component.py
```

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-29 20:44 CEST
Status: Amber

Strength:
- M2 already includes concrete block-header analysis work.

Improve now:
- I do not yet see a clear dashboard integration for M1, M2, M3, and M4 in app.py.

Next step:
- Make sure app.py visibly integrates M1, M2, M3, and M4 in the dashboard navigation.
<!-- student-repo-auditor:teacher-feedback:end -->
