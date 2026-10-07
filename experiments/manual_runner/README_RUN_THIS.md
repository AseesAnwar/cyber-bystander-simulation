# Manual Mesa Test Runner

This folder contains everything needed to run the manual Mesa test script.

## Why The Import Error Happened

The script imports:

```python
from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState
```

That means `manual_test_runner.py` must be in the same folder as:

- `mesa_bridge.py`
- `mesa_learning.py`
- `mesa_model.py`
- `mesa_agents.py`
- `abm_explanations.py`

Those files are included in this folder.

## Files In This Folder

| File | Purpose |
| --- | --- |
| `manual_test_runner.py` | Main script to run |
| `mesa_bridge.py` | Connects the script to the Mesa model |
| `mesa_model.py` | Mesa simulation model |
| `mesa_agents.py` | Mesa bystander agents |
| `mesa_learning.py` | Learning and reward helpers |
| `abm_explanations.py` | Explanation helper used by the bridge |
| `requirements.txt` | Python libraries to install |

## How To Run

Open Terminal in this folder.

Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manual_test_runner.py
```

If you already have the libraries installed, you can run:

```bash
python3 manual_test_runner.py
```

## Output

The script creates:

```text
manual_test_outputs/manual_test_results.xlsx
manual_test_outputs/manual_test_detailed_runs.csv
manual_test_outputs/manual_test_summary_results.csv
```

## If You Still Get Import Errors

Run:

```bash
PYTHONPATH=. python3 manual_test_runner.py
```

But this package should already avoid that problem because the script adds its own folder to the Python path.

