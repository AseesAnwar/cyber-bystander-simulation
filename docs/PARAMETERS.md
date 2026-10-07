# Simulation Parameters

The canonical Mesa model is intentionally transparent. Its parameters are modelling assumptions used for controlled what-if analysis, not empirically estimated causal coefficients.

## Population parameters

| Parameter | Meaning |
|---|---|
| total_bystanders | Number of bystander agents in the scenario |
| instigator_pct | Share predisposed toward supporting the bully |
| defender_pct | Share predisposed toward supporting the victim |
| neutral_pct | Share predisposed toward silence / non-intervention |
| other_pct | Share predisposed toward stepping aside |

Percentages are normalized and converted into integer agent counts while preserving the requested population size.

## Environment parameters

| Parameter | Meaning | Scale |
|---|---|---|
| initial_aggression | Starting bullying intensity | 0–100 |
| toxicity_level | Hostility of the source context | 0–100 |
| profanity_level | Offensive-language intensity | 0–100 |
| identity_attack_level | Identity-targeted harm | 0–100 |
| like_influence | Visible approval pressure | 0–100 |
| retweet_influence | Amplification / spread pressure | 0–100 |

## Behaviour parameters

| Parameter | Meaning |
|---|---|
| tom_influence_strength | Strength of ToM-inspired social-context adjustments |
| learning_rate | Speed of within-run reward adaptation |
| reward_strength | Magnitude of reward effects |
| memory_retention_strength | How much prior learned state is retained |
| adaptation_speed | How strongly new experience changes stored state |
| carry_learning | Whether learning persists across separate dashboard runs |

## Core heuristic dynamics

The current model combines:

- harmful-content pressure;
- support-for-bully pressure;
- defender pressure;
- silence pressure;
- low-impact unrelated behaviour;
- bounded random variation.

These terms are intentionally readable and adjustable so they can support sensitivity analysis.

## Why heuristics are used

The project is an exploratory agent-based model, not a causal estimator.

Using explicit heuristics makes it possible to:

- explain exactly why a simulated outcome changed;
- vary one assumption at a time;
- compare scenarios consistently;
- run sensitivity experiments;
- identify which assumptions have the greatest effect.

A future research extension could estimate some coefficients from empirical data or calibrate them against held-out aggregate statistics.
