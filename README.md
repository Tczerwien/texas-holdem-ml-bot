# Texas Hold’em ML Bot

This project aims to build a **modular, reproducible Texas Hold’em poker bot** using modern machine‑learning techniques.  It is designed for research and educational purposes, not for real‑money games.  The roadmap is broken into clear phases that take the project from an empty repository all the way to a demo bot that can play full hands against simulated opponents.

## Project Goals

The long‑term ambition is to create a bot that can ingest permitted hand histories, engineer meaningful features, estimate hand strength and opponent tendencies, and make reasoned betting decisions under uncertainty.  To get there the project focuses on:

- **Compliance & ethics:** use only play‑money or properly licensed data and document all sources in a `COMPLIANCE.md` file.  Never deploy the bot on real‑money platforms that prohibit automation.
- **Reproducibility:** deterministic data splits and simulations, locked dependencies, and continuous integration (CI) that enforces linting, typing, and test coverage.  All experiments should be easy to reproduce with a fixed random seed.
- **Modularity:** the codebase is organized into independent modules for the game engine, data parsing, feature engineering, models, policy/decision logic, evaluation, and utilities.  Each module comes with unit tests and contract tests for public interfaces.

## Roadmap (High Level)

The roadmap is an execution plan covering roughly two months of work.  Each phase has objectives, acceptance criteria, and deliverables; only a summary is given here.  See the JSON roadmap file for full details.

1. **Development Environment & Foundations (days 1‑2)** – bootstrap the repository with a license, code of conduct, compliance guide, CI pipeline and a reproducible Python setup (e.g. `pyproject.toml`, pre‑commit hooks, `pytest` with coverage).  A quickstart in this README should let a new contributor get up and running in under five minutes.
2. **Engine & State (days 3‑5)** – implement the core card representations, hand evaluator and game‑state logic.  The engine should deterministically score hands and support unit tests for straights, flushes, kickers and special cases like the wheel (A‑5 straight).
3. **Data Collection (days 6‑10)** – parse permitted hand histories and generate synthetic hands with a stable schema.  Define a `DATA_SCHEMA.md` for actions, stacks, positions and timestamps, and ensure processed datasets validate against it.  Store processed data in `data/processed` for repeatable experiments.
4. **Feature Engineering (days 11‑15)** – compute leakage‑free features from hands, positions, betting sequences and opponent history.  A `FeatureRegistry` will manage feature names, data types and dependencies while guarding against accidentally using future information in current decisions.
5. **Hand Strength Estimation (days 16‑22)** – estimate win probabilities with Monte Carlo simulations and fit machine‑learning surrogates (e.g. random forest or gradient boosting) for speed.  Calibrate predicted probabilities and include unit tests on canonical scenarios.
6. **Opponent Modeling (days 23‑28)** – derive statistics such as VPIP (Voluntarily Put Money In Pot), PFR (Pre‑Flop Raise) and aggression factor, then cluster opponents into personas (tight‑passive, TAG, LAG, etc.) with recency weighting.  Provide a baseline classifier and document the resulting profiles.
7. **Decision Engine (days 29‑35)** – choose whether to fold, call or raise (with size) using calibrated hand strength, opponent models and game theory.  Enforce never folding the nuts and adhere to minimum defense frequency bounds.  Start with simple rule‑based policies and progress to ML models.
8. **Bluffing & Balancing (days 36‑40)** – balance value and bluff ranges based on bet size, board texture and blockers.  Introduce an “exploit” engine that adapts bluff frequency against different opponent types while remaining within reasonable bounds.
9. **Integration & Simulation (days 41‑45)** – glue together the engine, features, models and policy to play full games in a simulator against different persona opponents.  Run 10 k‑hand simulations per persona, log metrics like win‑rate and action distribution, and build simple dashboards.
10. **Optimization & Learning (days 46‑50)** – tune hyper‑parameters, prune features, and potentially ensemble multiple policies.  Measure uplift over the Phase 8 baseline while enforcing safety limits (loss caps, session length).
11. **Final Testing & Demo (days 51‑56)** – validate on large historical datasets, implement preset “personalities” (conservative, aggressive, adaptive), and provide a demo via CLI (and optionally a Streamlit app) for human‑vs‑bot play.  Produce a project report summarizing methods, results, weaknesses and ablation studies.

Throughout all phases there are **cross‑cutting rules** (e.g. hand evaluator correctness, legal betting actions, recency in opponent modeling) and a **risk log** (e.g. ToS compliance, evaluator speed, feature leakage) to track potential issues and mitigations.  The **definition of done** requires that all phases meet their acceptance criteria, the end‑to‑end pipeline can be executed with a single command, and an ethical/compliance statement is finalized.

## Quickstart

> **Note:** The project is in its early stages; these instructions assume Phase 0 deliverables are available.  As the codebase evolves the commands may change.

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Tczerwien/texas-holdem-ml-bot
   cd texas-holdem-ml-bot
   ```

2. **Create a virtual environment** (Python 3.10 or 3.11) and install dependencies.  The project uses a lockfile to ensure reproducible installs.  For example, with `uv`:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   pip install -r requirements.txt  # or `uv pip install` / `poetry install` once configured
   ```

3. **Run the tests and lints** to verify your setup:

   ```bash
   make test   # runs pytest, linting and type checks (see Phase 0 tasks)
   ```

4. **Play a quick simulation** (later phases).  Once the engine, features, models and policy are implemented you will be able to run a CLI or notebook to simulate games and inspect metrics.  The exact commands will be documented in `src/demo/cli.py` and `docs/` when available.

## Contributing

Contributions are welcome!  Please adhere to the code of conduct, respect the compliance guidelines, and follow the project’s style and testing conventions.  Issues and pull requests should target a clear phase or task from the roadmap and include acceptance criteria for review.

---

*This README is a high‑level overview.  For detailed tasks, acceptance criteria, and deliverables see the `texas_holdem_ml_bot_roadmap_llm.json` file in this repository.*
