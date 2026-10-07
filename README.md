# Cyber-Bystander Agent-Based Simulation

[![Python tests](https://github.com/AseesAnwar/cyber-bystander-simulation/actions/workflows/tests.yml/badge.svg)](https://github.com/AseesAnwar/cyber-bystander-simulation/actions/workflows/tests.yml)

An explainable agent-based modelling project that explores how different bystander roles can influence the escalation or de-escalation of harmful online conversations.

The project uses Python, Mesa, Streamlit, and the CYBERBYSTANDER (CYBY23) dataset to build configurable social simulations around four bystander roles:

- **Instigator** — supports or amplifies harmful behaviour
- **Defender** — pushes back and supports the victim
- **Neutral** — observes or stays silent
- **Other** — participates without materially affecting the conflict

This is an **exploratory simulation**, not a prediction product or causal model of human behaviour.

## What This Project Demonstrates

- Agent-based modelling with Mesa
- Python simulation design
- Dataset preprocessing and role normalization
- Streamlit interactive dashboards
- ToM-inspired social-context reasoning
- Reward-based agent adaptation
- Persistent learning across repeated runs
- Reproducible random-seed experiments
- Sensitivity analysis
- Automated unit tests and GitHub Actions CI
- Transparent documentation of modelling assumptions and limitations

## Core Research Question

> How can the composition and behaviour of online bystanders influence whether a harmful conversation escalates, de-escalates, or remains unresolved?

The model supports what-if questions such as:

- What happens when defender participation increases?
- How does a neutral-heavy environment affect escalation?
- How does higher toxicity change the simulated outcome?
- How stable is a scenario across many random seeds?
- How does lightweight learning change behaviour across repeated runs?

## Canonical Architecture

The portfolio-facing implementation is the Mesa stack below.

```text
CYBY23 data / scenario inputs
        ↓
preprocess_cyby23.py
        ↓
mesa_bridge.py
        ↓
mesa_model.py
        ↓
mesa_agents.py + mesa_learning.py
        ↓
Streamlit dashboard
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the detailed architecture.

### Main files

- `preprocess_cyby23.py` — loads, cleans, normalizes, and structures CYBY23 data
- `mesa_agents.py` — defines bystander agent roles and action behaviour
- `mesa_learning.py` — reward-based adaptation and persistent learning state
- `mesa_model.py` — canonical Mesa simulation environment
- `mesa_bridge.py` — interface between the Mesa backend and UI
- `dashboard.py` — interactive Streamlit simulation
- `tableau_mesa_dashboard.py` — presentation-oriented dashboard variation
- `multi_seed_experiment.py` — repeated-run sensitivity analysis
- `tests/` — automated model and preprocessing tests

## How the Simulation Works

Each scenario contains an online bullying environment with one harmful situation and a population of bystander agents.

At each step:

1. agents observe the current environment;
2. agents respond to role preferences and visible social context;
3. active agents choose actions;
4. the overall bullying intensity changes;
5. reward-based learning updates behavioural tendencies;
6. the simulation stops when it escalates, calms down, or reaches the maximum number of steps.

Possible agent actions include:

- support the bully
- support the victim
- stay silent
- step aside

## Dataset Grounding

The project uses CYBY23 to ground role structure and harmful-content context.

The preprocessing workflow:

- cleans dataset rows;
- normalizes identifiers;
- maps raw bystander labels into four interpretable roles;
- identifies source posts and labelled replies;
- builds conversation-level records;
- derives scenario context such as toxicity and engagement.

The dataset is **not** treated as proof that the simulation reproduces real human behaviour causally.

### Data file

By default the project expects:

```text
data/CYBERBYSTANDER (CYBY23) dataset.xlsx
```

You can also provide an explicit path when running preprocessing or other command-line tools.

The source dataset is not included in this public repository unless redistribution permission is confirmed.

## Model Interpretation

The canonical Mesa implementation is designed as a transparent **what-if model**.

Several coefficients are deliberately heuristic, including:

- role participation probabilities
- content-pressure weights
- defender and instigator pressure
- silence effects
- reward functions
- learning and memory strengths

These are modelling assumptions, not estimated causal coefficients.

See:

- [docs/PARAMETERS.md](docs/PARAMETERS.md)
- [docs/MODEL_LIMITATIONS.md](docs/MODEL_LIMITATIONS.md)

## Important Evaluation Clarification

An earlier research implementation in this repository used observed CYBY23 role labels to help parameterize agents and then compared simulated actions against those same role labels.

That metric is now called **role agreement rate**, not accuracy.

It should be interpreted only as a descriptive reproduction measure because the observed role label contributes to the simulated behaviour. It is **not out-of-sample predictive accuracy**.

The canonical Mesa simulation is therefore evaluated primarily through:

- behaviour under controlled scenarios;
- reproducibility with fixed seeds;
- repeated-run sensitivity;
- outcome distributions;
- parameter sensitivity;
- transparent inspection of agent rules.

## Multi-Seed Sensitivity Analysis

One stochastic run is not treated as sufficient evidence.

The project includes:

```bash
python multi_seed_experiment.py --runs 100 --start-seed 1
```

This repeats one scenario across many random seeds and reports:

- mean final bullying intensity
- standard deviation
- escalation rate
- calming rate
- unresolved rate

This allows conclusions to be phrased as distributions rather than one-off outcomes.

See [docs/SENSITIVITY_ANALYSIS.md](docs/SENSITIVITY_ANALYSIS.md).

## Automated Testing

The repository includes unit tests for important invariants, including:

- role percentages convert to the requested population size
- base behavioural preferences remain valid probability distributions
- positive rewards increase learned action values
- identical seeds reproduce the same simulation path
- bullying intensity remains bounded between 0 and 100
- CYBY23 role labels normalize correctly
- missing dataset paths raise clear errors

GitHub Actions runs these tests automatically on pushes and pull requests.

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

The dependency file constrains major versions to reduce accidental breakage from future package releases.

## Run the Dashboard

```bash
streamlit run dashboard.py
```

For the presentation-oriented interface:

```bash
streamlit run tableau_mesa_dashboard.py
```

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## Run a Multi-Seed Experiment

```bash
python multi_seed_experiment.py --runs 100
```

Run-level results are exported to:

```text
outputs/multi_seed_results.csv
```

## Repository Documentation

```text
docs/
├── ARCHITECTURE.md
├── MODEL_LIMITATIONS.md
├── PARAMETERS.md
├── SENSITIVITY_ANALYSIS.md
└── archive/
    └── historical project notes, proposals, prompt logs, and handoff material
```

Historical university-development material is retained for transparency but moved out of the repository root so the canonical implementation is easy to identify.

## Research and Legacy Code

The project evolved through several modelling approaches.

Files such as `model.py`, `agents.py`, `rl_module.py`, `tom_module.py`, `memory_module.py`, `behavioral_simulation.py`, and `dataset_behavioral_simulation.py` represent earlier research iterations or supporting experiments.

They are retained to show development history but are **not the canonical runtime architecture**.

## Current Limitations

- behavioural coefficients are heuristic rather than causally estimated;
- CYBY23 grounds scenarios but does not validate exact simulated trajectories;
- social networks are simplified;
- ToM is an interpretable approximation rather than a complete cognitive architecture;
- learning is lightweight reward adaptation rather than deep reinforcement learning;
- stronger empirical calibration and held-out validation would be needed before making predictive claims.

These limitations are deliberate and documented rather than hidden.

## Future Improvements

- expand multi-seed sensitivity experiments across scenario grids;
- add confidence intervals and parameter-sensitivity visualizations;
- calibrate selected parameters against aggregate held-out statistics;
- add network topology to represent repeated social relationships;
- add portfolio screenshots of the dashboard and simulation outputs;
- package the canonical model into a cleaner `src/` module structure.

## Project Background

This project began as a university applied research project and has been progressively refactored into a more reproducible and recruiter-readable portfolio project.

The focus is not on claiming that a simulation can predict human behaviour. The value of the project is in building a transparent computational environment where assumptions can be changed, repeated, tested, and explained.

## License

MIT License.
