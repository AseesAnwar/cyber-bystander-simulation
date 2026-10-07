# Repeated-Run Sensitivity Analysis

Agent-based simulations are stochastic. One run is not enough to support a robust conclusion.

The repository therefore includes `multi_seed_experiment.py`, which repeats the same canonical Mesa scenario across many random seeds.

## Example

```bash
python multi_seed_experiment.py --runs 100 --start-seed 1
```

The script records:

- seed;
- final outcome;
- final bullying intensity;
- number of simulation steps.

It also reports:

- mean final bullying intensity;
- standard deviation;
- escalation rate;
- calming rate;
- unresolved rate.

## Interpretation

Instead of saying:

> This scenario escalated.

prefer:

> Across 100 seeded runs, the scenario escalated in X% of simulations and had a mean final bullying intensity of Y.

This treats randomness as part of the model rather than hiding it.

## Important note

Repeated-run stability does not prove that the model is a causal representation of human behaviour. It only shows how stable the model's own conclusions are under its current assumptions.
