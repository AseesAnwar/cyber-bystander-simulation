# CYBY23 Agent-Based Simulation Project Report

Date generated: 2026-05-04
Workspace: `/Users/aseesanwar/Documents/Playground`

## Overview

This report summarizes the work completed in this chat from the first Mesa prototype through the current CYBY23 dataset-led interactive simulation. The project evolved from a generic cyberbystander simulation into a separate dataset-grounded dashboard designed to be clearer for instructors and teammates.

## Phase 1: Initial Mesa Prototype

On March 12, 2026, the first working Mesa simulation was created to model bystander choices among:

- `ignore`
- `defend`
- `report`
- `reinforce`

Files created:

- `simulation.py`
- `requirements.txt`
- `README.md`

Core behaviour in this phase:

- Agents were given empathy, anonymity sensitivity, and peer susceptibility.
- Action probabilities were shaped by empathy, anonymity, and peer norms.
- A `DataCollector` tracked action counts over time.
- Results were exported to CSV for later inspection.

## Phase 2: Dependencies and Initial Experiments

Dependencies were installed into a local virtual environment, and the first scenario runs were executed.

Outputs created:

- `run_high_anonymity.csv`
- `run_prosocial.csv`

Purpose of these runs:

- Compare higher-anonymity behaviour against a more prosocial starting environment.
- Inspect final counts and average action behaviour across time.

Issue fixed:

- The initial simulation row incorrectly showed all agents as `ignore` before any action had happened.
- That was corrected in `simulation.py`.

## Phase 3: First Interactive Dashboard

A Streamlit dashboard was added so the model could be explored through a web browser.

Key file:

- `dashboard.py`

Capabilities added:

- Parameter controls in the sidebar
- Line charts for bystander actions over time
- Norm visualizations
- Agent-level scatter plots
- CSV downloads

This dashboard was first exposed locally at:

- `http://127.0.0.1:8501`

## Phase 4: Public Temporary Sharing

The local-only dashboard was then made shareable using a Cloudflare quick tunnel.

Key tool used:

- `cloudflared`

Important outcome:

- The dashboard could be accessed by teammates and instructors through a temporary public URL.

Important limitation:

- These links are temporary and stay live only while the laptop stays awake, online, and the Streamlit plus tunnel processes remain running.

## Phase 5: Explanation and Academic Framing

The dashboard was updated to explain:

- what the simulation is about
- what each action means
- what the charts represent
- what is modelled behaviour versus real-world observation

We also discussed validity and bias.

Main conclusions from that discussion:

- The early prototype was technically working but not yet empirically validated.
- The initial behavioural rules were hand-crafted.
- Authenticity requires calibration against observed data.
- Bias can arise from modelling assumptions and parameter choices.

## Phase 6: Transition to CYBY23 Dataset-Led Modelling

The project then moved from a generic agent-based model toward a CYBY23-grounded simulation.

Important local dataset found:

- `/Users/aseesanwar/Downloads/archive/CYBERBYSTANDER (CYBY23) dataset.xlsx`

Important preprocessing file:

- `preprocess_cyby23.py`

Local preprocessing results found during testing:

- 90 usable source posts / threads
- 512 labelled bystander replies

Observed local role mix:

- about 44% reinforce / bully-supporting
- about 17% defend / victim-supporting
- about 36% neutral / silent
- about 2% unrelated / aside

## Phase 7: CYBY23 Learning Calibration

A new calibration layer was added:

- `cyby23_learning.py`

Purpose:

- Estimate starting behavioural tendencies from CYBY23 role labels
- Use the dataset to bias simulated behaviour in a transparent way

Observed role-to-action mapping:

- `reinforce` -> bully-supporting tendency
- `defend` -> victim-supporting tendency
- `neutral` -> silence tendency
- `unrelated` -> step-aside tendency

This made the simulation more dataset-aware than the original hand-set version.

## Phase 8: Separate CYBY23 Interactive Model

To avoid disturbing the older dashboard, a separate CYBY23 dataset-led model was created.

New files:

- `cyby23_interactive_model.py`
- `cyby23_interactive_dashboard.py`

Design goal:

- Leave older running dashboards untouched
- Build a separate browser app specifically for CYBY23-based behaviour learning

Main features of the new model:

- Loads CYBY23 threads
- Selects threads by risk group or thread id
- Converts labelled bystander replies into agents
- Infers traits such as empathy, anonymity sensitivity, and peer susceptibility
- Simulates actions over time:
  - `ignore`
  - `defend`
  - `report`
  - `reinforce`
- Uses reward updates so agents adapt during the run
- Tracks bullying level and final outcome

Important modelling caveat:

- CYBY23 does not directly label `report`
- In the simulation, `report` is a latent simulated intervention option, not a directly observed CYBY23 label

## Phase 9: Separate Dashboard on Port 8502

The new CYBY23 app was launched independently of the old dashboard.

Port layout:

- older dashboard: `8501`
- new CYBY23 dashboard: `8502`

This separation was important because the user explicitly asked that the older running environment should not be touched.

## Phase 10: UX Redesign for Clarity

The first CYBY23 dashboard version still felt too technical and confusing for presentation use.

The user raised two strong criticisms:

1. the user would not know what to do
2. if the model is dataset-led, exposed controls like anonymity and simulation steps are confusing

In response, the separate CYBY23 dashboard was redesigned around a guided user journey.

New main flow:

1. choose CYBY23 data and a real conversation
2. choose a scenario
3. run the simulation
4. read the result and takeaway

The dashboard also started prioritizing larger threads by default so the demo behaviour is easier to interpret.

## Phase 11: Dataset-Derived Values vs Modelling Assumptions

One of the most important improvements was separating:

- what comes directly from CYBY23
- what is a modelling assumption used for scenario testing

Dataset-derived values now include:

- selected thread
- observed bystander role counts
- thread risk level
- toxicity and identity-attack features
- number of labelled replies

Modelling assumptions now include:

- future interaction rounds
- assumed platform anonymity
- assumed peer pressure strength
- agent adaptation speed
- CYBY23 starting-pattern strength

This improved the academic defensibility of the dashboard.

## Phase 12: Scenario-Based Interaction

To reduce confusion further, raw control-first interaction was replaced by scenario presets.

Current scenario choices:

- `Dataset baseline`
- `More anonymous platform`
- `Stronger intervention/moderation`

This lets the user compare plausible situations without needing to understand every low-level model parameter.

## Phase 13: Process and Port Isolation

The user then asked to make sure the new environment was not being used by any other running app.

A process check found:

- the older dashboard correctly on `8501`
- the new CYBY23 dashboard on `8502`
- one conflicting old process also bound to `8502`

That conflicting old process was stopped carefully, leaving:

- `dashboard.py` on `8501`
- `cyby23_interactive_dashboard.py` on `8502`

This ensured the new CYBY23 environment was isolated.

## Phase 14: Public URL for the Separate CYBY23 Dashboard

A separate Cloudflare quick tunnel was created for the new CYBY23 dashboard on port `8502`.

Public URL created:

- `https://everybody-aware-winds-luck.trycloudflare.com`

That URL was verified with HTTP 200 at the time it was created.

Again, it remains temporary and depends on the host machine and processes continuing to run.

## Current Project State

Most relevant files now:

- `simulation.py`
- `dashboard.py`
- `preprocess_cyby23.py`
- `cyby23_learning.py`
- `cyby23_interactive_model.py`
- `cyby23_interactive_dashboard.py`

Key distinction:

- `dashboard.py` belongs to the older simulation/dashboard path
- `cyby23_interactive_dashboard.py` is the newer dataset-led CYBY23 dashboard

Current local access points:

- old dashboard: `http://127.0.0.1:8501`
- new CYBY23 dashboard: `http://127.0.0.1:8502`

Current public share link for the new CYBY23 dashboard:

- `https://everybody-aware-winds-luck.trycloudflare.com`

## Overall Summary

The project moved through four major stages:

1. a generic Mesa cyberbystander prototype
2. a local interactive dashboard
3. a public temporary shareable version
4. a separate CYBY23 dataset-led interactive simulation with clearer academic framing

The most important improvement was not only technical complexity, but clarity.

The current CYBY23 dashboard is designed to:

- start from real observed dataset evidence
- show what is actually taken from the dataset
- make assumptions explicit rather than hidden
- let users compare scenarios in a way that is easier to present and defend

## Note on the "Stronger Intervention/Moderation" Scenario

In `cyby23_interactive_dashboard.py`, the `Stronger intervention/moderation` scenario currently uses:

- `anonymity_level = 0.35`
- `peer_influence_strength = 0.45`
- `learning_rate = 0.45`
- `learning_strength = 0.65`
- `steps = 25`

This is the preset that currently represents a more protective environment where corrective behaviour and reporting-type responses are easier to learn and sustain in the simulation.
