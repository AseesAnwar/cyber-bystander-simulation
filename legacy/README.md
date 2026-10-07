# Legacy Implementations

This folder preserves earlier research implementations that are no longer the canonical portfolio runtime.

## label_conditioned/

This model used observed CYBY23 role labels as part of agent initialization and then compared simulated actions with those labels.

Because the target label contributes to behaviour generation, its **role agreement rate is not predictive accuracy**.

The implementation is preserved for research history and transparency, but the portfolio-facing model is the root-level Mesa stack:

- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`
- `mesa_bridge.py`
