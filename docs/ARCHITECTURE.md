# Canonical Architecture

This repository contains several research iterations. The **portfolio-facing implementation** is the Mesa + Streamlit stack below.

## Canonical runtime path

```text
CYBY23 dataset / manual scenario inputs
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

## Canonical files

- `preprocess_cyby23.py` — dataset loading, cleaning, role normalization, and thread construction.
- `mesa_agents.py` — Mesa agent definitions and role-specific behaviour.
- `mesa_learning.py` — lightweight reward-based adaptation and persistent learning state.
- `mesa_model.py` — core Mesa environment and simulation dynamics.
- `mesa_bridge.py` — stable interface between the simulation backend and UI.
- `dashboard.py` / `tableau_mesa_dashboard.py` — interactive Streamlit presentation layers.

## Research / legacy implementations

Earlier implementations are now separated from the canonical runtime:

- `legacy/label_conditioned/` contains the earlier role-label-conditioned simulation stack.
- `experiments/prototypes/` contains exploratory models, dashboards, manual tests, and reward experiments.

These files document the evolution of the project, but they should not be treated as the primary portfolio runtime path.

One important distinction is that the legacy dataset-conditioned simulator uses observed CYBY23 role labels as part of agent initialization. Its role-agreement metric is therefore a **descriptive reproduction measure**, not an independent predictive accuracy estimate.

## Modelling intent

This project is an exploratory agent-based model, not a classifier or forecasting service.

The canonical Mesa implementation is intended to answer questions such as:

- How does the bystander mix change simulated escalation?
- How sensitive are outcomes to defender, instigator, neutral, and unrelated roles?
- How do toxicity and engagement settings affect simulated bullying intensity?
- How does lightweight reward-based adaptation change behaviour over repeated runs?
- How stable are outcomes across different random seeds?

The model is deliberately interpretable and parameterized rather than designed as a black-box prediction model.
