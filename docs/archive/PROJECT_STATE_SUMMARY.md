# Cyber-Bystander Simulation Project State Summary

This file records the current state of the cyber-bystander simulation project so the team can return to it later without losing context.

## Current Project Direction

The project is a Mesa-based agent-based simulation of cyber-bystander behaviour in online bullying discussions.

The project should be explained as:

- a behavioural simulation
- an agent-based modelling prototype
- a university applied project
- an exploratory tool for understanding bystander dynamics

The project should not be explained as:

- a prediction product
- a classifier dashboard
- a machine learning accuracy tool
- a tool that predicts exact real-world human behaviour

## Main Concept

The simulation represents one online bullying conversation.

The environment includes:

- 1 abuser
- 1 victim
- multiple bystanders

Bystander roles:

- Instigator: supports the bully and can increase bullying pressure
- Defender: supports the victim and can reduce bullying pressure
- Neutral: stays silent and can indirectly allow bullying to continue
- Other: unrelated or low-impact participant

The simulation tracks how the bullying level changes over time.

Possible outcomes:

- Got worse
- Calmed down
- Stayed unresolved

## Dataset

The project uses the CYBY23 cyber-bystander dataset.

Dataset role mapping:

- `reinforce` maps to `instigator`
- `defend` maps to `defender`
- `neutral` maps to `neutral`
- `unrelated` maps to `other`

Important dataset framing:

- CYBY23 provides role structure and harmful-content context.
- CYBY23 is not used as a prediction target.
- The simulation does not claim to replay real conversations exactly.
- The dataset grounds the project in real labelled online discussion data.

## Current Dashboards

There are two useful dashboard directions for the instructor meeting.

### 1. Interactive Scenario Simulation

Current file:

- `tableau_mesa_dashboard.py`

Purpose:

- shows an interactive Tableau-style dashboard
- uses the Mesa backend
- allows manual control of bystander mix and starting situation
- supports what-if exploration

How to explain it:

“This version is inspired by CYBY23 but gives users controls so we can test what-if scenarios. It helps us explore how changing the bystander mix affects escalation or calming.”

Important current UI design:

- Bystander mix uses actual counts, not percentages.
- If total bystanders is 20, all role counts together must equal 20.
- `Unrelated bystanders` is automatically calculated from the remaining total.
- Advanced behaviour settings are simple on/off toggles.

Advanced behaviour toggles:

- Social influence on
- Learning from outcomes on
- Memory across runs on
- Carry learning into next run

The dashboard maps these toggles to internal numeric values for the Mesa model.

### 2. Dataset-Dependent Simulation

Purpose:

- uses CYBY23-derived values as the scenario source
- is more dataset-grounded
- avoids manually inventing the starting environment

How to explain it:

“This version is more dataset-grounded. The bystander mix and harmful-content context come from CYBY23. The user does not manually create the scenario.”

Recommended meeting flow:

1. Show dataset-dependent simulation first.
2. Explain that this proves the project is connected to CYBY23.
3. Then show the interactive scenario simulation.
4. Explain that this supports what-if sensitivity testing.

## Mesa Backend

Mesa is the real simulation framework.

Important files:

- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`
- `mesa_bridge.py`

How to explain Mesa:

“The web page is built in Streamlit, but the simulation itself runs through a Mesa backend. The dashboard passes settings to `CyberBystanderMesaModel`, which creates bystander agents and activates them step by step.”

Important code evidence:

- `dashboard.py` / `tableau_mesa_dashboard.py` imports from `mesa_bridge.py`
- `mesa_bridge.py` creates `CyberBystanderMesaModel`
- `mesa_model.py` defines `CyberBystanderMesaModel`
- Mesa agent activation uses `self.agents.shuffle_do("step")`

## Codex Role

Codex was used as a development assistant.

Codex helped with:

- code generation
- debugging
- restructuring
- dashboard wording
- documentation
- project explanation

Codex is not the simulation framework.

Meeting explanation:

“Mesa is the simulation engine. Codex was used as a coding and documentation assistant to help develop and explain the project.”

## Important Files

Key current files:

- `tableau_mesa_dashboard.py`
- `dashboard.py`
- `mesa_bridge.py`
- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`
- `abm_explanations.py`
- `abm_ui_helpers.py`
- `preprocess_cyby23.py`
- `MESA_BUILD_GUIDE.md`
- `CODEX_AND_MESA_GUIDE.md`
- `current_live_mesa_dashboard_code.zip`

## Current Live Dashboard Link

The most recent temporary Cloudflare link was:

```text
https://dental-renewal-teenage-guardian.trycloudflare.com
```

Important:

- This link is temporary.
- It only works while the local Streamlit app and Cloudflare tunnel are running.
- If it stops working, restart Streamlit and create a fresh tunnel.

## Local Run Command

To run the Tableau-style dashboard locally:

```bash
cd /Users/aseesanwar/Documents/Playground
streamlit run tableau_mesa_dashboard.py
```

To install dependencies:

```bash
pip install -r requirements.txt
```

## Required Python Libraries

Current `requirements.txt`:

```text
pandas>=2.2
numpy>=1.26
mesa>=3.5
matplotlib>=3.8
openpyxl>=3.1
networkx>=3.3
streamlit>=1.55
```

## Instructor Explanation

Short meeting script:

“I built two Mesa-based simulation views. The first one is a dataset-dependent simulation, where the starting scenario comes from CYBY23. The second is an interactive scenario dashboard where we can adjust bystander roles to test what-if behaviour. Neither version is a prediction tool. The aim is to explore how cyber-bystanders, such as defenders, bully supporters, silent bystanders, and unrelated participants, may influence whether online bullying becomes worse, calms down, or stays unresolved.”

## Key Takeaway

The project shows that online bullying is not only shaped by the bully. Bystanders also matter. The simulation helps users explore how different bystander roles can change the direction of a harmful online conversation.
