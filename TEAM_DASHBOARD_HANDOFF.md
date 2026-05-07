# Team Dashboard Handoff Guide

## Purpose

This folder contains the current Python code for the cyber-bystander Mesa dashboard.

The live Cloudflare links are temporary, so teammates should run the dashboard locally on their own computers.

## Main Dashboard File

Run this file:

```bash
streamlit run tableau_mesa_dashboard.py
```

This opens the interactive dashboard in a browser.

## What The Dashboard Is

This is a behavioural simulation dashboard, not a prediction product.

It simulates an online bullying situation with:

- one harmful situation / abuser context
- one victim context
- multiple bystanders

Bystander roles:

- Instigator: supports the bully
- Defender: supports the victim
- Neutral: stays silent
- Other: unrelated or low-impact

The Mesa backend updates the bullying level over time and shows whether the situation:

- got worse
- calmed down
- stayed unresolved

## Important Files

| File | Purpose |
| --- | --- |
| `tableau_mesa_dashboard.py` | Main Streamlit dashboard |
| `mesa_model.py` | Mesa model/environment |
| `mesa_agents.py` | Mesa bystander agents |
| `mesa_learning.py` | Action preferences, learning state, reward helpers |
| `mesa_bridge.py` | Connects Mesa outputs to the dashboard |
| `abm_explanations.py` | Plain-English explanations |
| `abm_ui_helpers.py` | Chart and visual helper functions |
| `preprocess_cyby23.py` | CYBY23 dataset loading and cleaning |
| `reward_design_experiments.py` | Separate experiment for reward-design testing |
| `requirements.txt` | Python libraries needed |

## Setup Steps

### 1. Open Terminal

Go to the project folder.

```bash
cd path/to/the/dashboard/folder
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

On Mac:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install libraries

```bash
pip install -r requirements.txt
```

### 5. Run the dashboard

```bash
streamlit run tableau_mesa_dashboard.py
```

Streamlit will print a local browser URL, usually:

```text
http://localhost:8501
```

Open that URL in a browser.

## Dataset Note

The dashboard is connected to the CYBY23 cyber-bystander project.

The dataset itself is not included in this code zip unless it is shared separately.

If a teammate needs full dataset functionality, give them the CYBY23 Excel file and make sure the path in the app points to the dataset location on their computer.

Common dataset filename:

```text
CYBERBYSTANDER (CYBY23) dataset.xlsx
```

## How To Work On The Code

Start with these files:

1. Edit dashboard wording or layout in `tableau_mesa_dashboard.py`.
2. Edit agent behaviour in `mesa_agents.py`.
3. Edit environment logic in `mesa_model.py`.
4. Edit learning and reward logic in `mesa_learning.py`.
5. Edit plain-English explanations in `abm_explanations.py`.

## Important Project Framing

Use this wording when explaining the project:

```text
This is an agent-based behavioural simulation for exploring cyber-bystander dynamics. It is not a tool for predicting exact real-world behaviour.
```

## Current Scientific Findings

The testing so far found:

- harmful-content pressure can push the simulation toward escalation
- defenders can reduce or delay harm
- silence can indirectly allow harm to continue
- calibration is needed to show low, medium, tipping-point, and high-risk scenarios
- reward design strongly affects what agents learn

## Reward Design Experiment

To run the separate reward-design experiment:

```bash
python3 reward_design_experiments.py
```

This creates CSV outputs in:

```text
sensitivity_outputs/reward_design_experiments/
```

This experiment compares:

- role-based reward
- victim-safety reward
- mixed ethical reward

## Troubleshooting

If Streamlit says a port is already in use:

```bash
streamlit run tableau_mesa_dashboard.py --server.port 8502
```

If imports fail, make sure:

```bash
pip install -r requirements.txt
```

was run inside the activated virtual environment.

