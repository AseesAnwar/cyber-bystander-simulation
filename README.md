# Cyber-Bystander Simulation Prototype

## Project Summary

This repository contains an early-stage research prototype for simulating cyber-bystander behaviour in harmful online conversations. The project uses the CYBERBYSTANDER (CYBY23) dataset and the Mesa agent-based modelling framework to compare real labelled reply behaviour with simulated reply behaviour.

The prototype is designed for a university audience: it is simple enough to explain in a presentation, but structured clearly enough to support future research extensions.

## What The Simulation Does

The simulator treats each online conversation as a sequence:

1. a harmful or hostile original post appears
2. people reply to that conversation
3. each replying agent chooses one of four actions:
   - support the harmful post (`reinforce`)
   - push back against it (`defend`)
   - stay neutral (`neutral`)
   - say something unrelated (`unrelated`)

The model can run in two modes:

- baseline rule-based mode
- simplified learning mode with Theory of Mind (ToM), Reinforcement Learning (RL), and Continual Learning (CL)

## Why This Matters For Cyber-Bystander Behaviour

Cyber-bystander behaviour is important because harmful online discussions are shaped not only by the person who starts them, but also by how others react. Replies can amplify harm, resist harm, remain passive, or ignore the conflict entirely.

This project models those bystander reactions in a way that lets us:

- compare model behaviour with real labelled data
- test whether simple social assumptions produce realistic reply patterns
- build a transparent baseline before moving to more advanced AI approaches

## Connection To The ToM / RL / CL Research Direction

This prototype is inspired by research directions that combine:

- Theory of Mind: agents infer what is happening socially
- Reinforcement Learning: agents learn which actions pay off
- Continual Learning: agents adapt over time instead of resetting completely

This implementation keeps those ideas intentionally simple and interpretable:

- no deep learning
- no neural networks
- no external ML libraries

Instead, the project uses:

- simple mental-state inference from toxicity, sentiment, and visible reply trends
- tabular Q-learning with dictionary-based Q-tables
- rolling memory with decay-based forgetting

This makes the project easier to defend in an academic meeting while still showing a credible extension path toward richer learning models.

## Project Structure

- `preprocess_cyby23.py`
  Loads and cleans the CYBY23 dataset, normalizes labels, and builds conversation records.
- `agents.py`
  Defines the source post, moderator, victim, and bystander agents.
- `tom_module.py`
  Implements simplified Theory of Mind inference.
- `rl_module.py`
  Implements tabular Q-learning and reusable learner profiles.
- `memory_module.py`
  Implements rolling memory for continual learning.
- `model.py`
  Defines the Mesa conversation model and simulation outputs.
- `run_simulation.py`
  Runs batch simulations from the command line and exports results.
- `dashboard.py`
  Streamlit dashboard for interactive exploration.
- `demo.py`
  Small runnable example script.

## Early-Stage Prototype Note

This repository should be treated as an early-stage research prototype rather than a finished production tool. The aim is to support discussion, experimentation, and academic presentation.

Current simplifications include:

- one reply decision per agent per conversation
- no deep language modelling
- no full social network graph
- simplified rewards and memory rules
- simplified Theory of Mind rather than a full cognitive architecture

## Setup Instructions

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Provide the dataset

The expected default dataset path is:

```text
/mnt/data/CYBERBYSTANDER (CYBY23) dataset.xlsx
```

If that path does not exist, the scripts will use the local fallback path configured in the preprocessing module when available.

## How To Run The Project Locally

### Run preprocessing only

```bash
python3 preprocess_cyby23.py --dataset-path "/mnt/data/CYBERBYSTANDER (CYBY23) dataset.xlsx"
```

### Run the baseline simulation

```bash
python3 run_simulation.py --dataset-path "/mnt/data/CYBERBYSTANDER (CYBY23) dataset.xlsx"
```

### Run the learning-enabled simulation

```bash
python3 run_simulation.py --dataset-path "/mnt/data/CYBERBYSTANDER (CYBY23) dataset.xlsx" --learning-mode
```

### Launch the Streamlit dashboard

```bash
streamlit run dashboard.py
```

### Run the demo script

```bash
python3 demo.py
```

## Dashboard Overview

The Streamlit dashboard is intended for presentations and academic walkthroughs. It includes:

- plain-English explanation of the model
- comparison of real reply behaviour and predicted reply behaviour
- example conversation walkthrough
- optional learning mode visualizations
- advanced tables for technical inspection

## Screenshots

Add screenshots here after publishing the project.

- `[Screenshot placeholder: dashboard home view]`
- `[Screenshot placeholder: learning mode view]`
- `[Screenshot placeholder: example conversation walkthrough]`

## Requirements

The project currently depends on:

- Python 3.12+
- pandas
- numpy
- mesa
- matplotlib
- openpyxl
- networkx
- streamlit

Install all requirements with:

```bash
pip install -r requirements.txt
```

## How To Share This Project

Once this repository is pushed to a public GitHub repository, anyone with the GitHub link can view the code, README, and project files in their browser.

If the repository is public:

- instructors can open the link directly
- teammates can clone the repository locally
- anyone with the link can inspect the code without needing local access to your machine

Note that the dataset itself may need to be shared separately if you do not include it in the repository.

## License

This project is released under the MIT License. See the `LICENSE` file for details.
