# Model Assumptions and Limitations

## Scope

This project is an exploratory behavioural simulation of cyber-bystander dynamics. It does not claim to predict the exact behaviour of an individual person or reproduce a real online conversation with causal certainty.

## Dataset grounding

CYBY23 is used to ground:

- bystander role categories;
- harmful-content context;
- example thread composition;
- scenario initialization.

Observed role labels should not be interpreted as causal behavioural mechanisms.

## Heuristic parameters

Several coefficients in the simulation are manually designed modelling assumptions, including:

- participation probabilities;
- toxicity / profanity / identity-attack pressure;
- role-specific action preferences;
- escalation and defence pressure;
- reward functions;
- learning and memory strengths.

These values are intended for controlled what-if experiments. They are not presented as empirically estimated causal coefficients.

## Randomness

Individual simulation runs contain stochastic behaviour. A single run should therefore be interpreted as one realization of the model.

For stronger analysis, scenario conclusions should be based on repeated seeded runs and summarized using quantities such as:

- mean final bullying intensity;
- standard deviation;
- escalation probability;
- de-escalation probability;
- confidence intervals.

## Theory of Mind framing

The project uses **ToM-inspired social-state inference**, not a complete cognitive Theory of Mind architecture.

Agents infer simplified social context from visible behaviour and current environmental signals.

## Learning framing

The canonical model uses lightweight reward-based adaptation and persistent memory across runs. Earlier research iterations also include tabular Q-learning.

These mechanisms demonstrate adaptive agent behaviour but should not be described as advanced deep reinforcement learning.

## Legacy role-agreement metric

The earlier dataset-conditioned model uses observed CYBY23 role labels to parameterize agents and then compares simulated actions with those labels.

For that reason, its role agreement rate is a descriptive consistency measure only. It is not out-of-sample predictive accuracy.

## Responsible interpretation

The dashboard should be described as:

- an agent-based simulation;
- an exploratory research prototype;
- a what-if analysis tool;
- a way to study behavioural dynamics under explicit assumptions.

It should not be described as:

- a production moderation system;
- a clinical or psychological assessment tool;
- a causal model of human behaviour;
- a reliable predictor of what a specific person will do.
