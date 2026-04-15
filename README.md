# Blockchain Dashboard Project

Use this repository to build your blockchain dashboard project.
Update this README every week.

## Student Information

| Field | Value |
|---|---|
| Student Name | Rubén Elices Rodríguez |
| GitHub Username | rubenelices |
| Project Title | Blockchain_dashboard |
| Chosen AI Approach | M4 option 2 — Anomaly Detector: identify blocks with statistically abnormal inter-arrival times using an exponential distribution baseline |

## Module Tracking

Use one of these values: `Not started`, `In progress`, `Done`

| Module | What it should include | Status |
|---|---|---|
| M1 | Proof of Work Monitor | In progress |
| M2 | Block Header Analyzer | Not started |
| M3 | Difficulty History | Not started |
| M4 | AI Component | Not started |

## Current Progress

- Session 1 done: repo set up, README updated, API client connected to Blockstream and returning real Bitcoin data (height, hash, nonce, bits, difficulty, tx count).

## Next Step

- Implement M1: build the Streamlit PoW Monitor panel with live difficulty, leading-zero visualisation, block time histogram, and estimated hash rate.

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
