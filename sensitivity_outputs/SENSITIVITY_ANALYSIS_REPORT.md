# Sensitivity Analysis Report

## Purpose

This sensitivity analysis tests how the current Mesa cyber-bystander simulation behaves when key environment settings are changed.

The aim is not to prove real-world causality. The aim is to understand how the simulated environment responds over time when we change:

- the mix of bystander roles
- the harmfulness of the starting situation
- engagement pressure from likes and retweets
- social influence, learning, and memory settings

## Experimental Setup

The experiment used the current Mesa backend through `mesa_bridge.py`.

Each scenario was repeated across multiple random seeds so the result was not based on a single run.

Main outcome measures:

- **Mean final bullying level:** average bullying level at the end of the run.
- **Mean change:** final bullying level minus starting bullying level.
- **Got worse rate:** percentage of runs that reached the escalation threshold.
- **Calmed down rate:** percentage of runs that reached the calming threshold.
- **Unresolved rate:** percentage of runs that ended without either threshold.
- **Mean steps:** average number of simulation steps before the run stopped.

The default escalation threshold is 80. The default calming threshold is 20.

## Main Finding

The current simulation is strongly biased toward escalation under the standard dashboard settings.

In plain English:

**When the harmful-content pressure is moderate or high, the bullying level usually rises over time even when there are more defenders. Defenders slow escalation, but they do not always reverse it unless they strongly dominate and the starting harm level is low.**

This is useful scientifically because it shows what the current model assumes. It tells us that harmful content features such as toxicity, profanity, identity attack, and engagement have a very strong effect in the current environment.

## Scenario Comparison

| Scenario | Mean final bullying level | Mean change | Got worse | Calmed down | Unresolved | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Balanced baseline | 85.3 | +40.3 | 100% | 0% | 0% | 5.0 |
| Defender-heavy | 84.0 | +39.0 | 100% | 0% | 0% | 5.2 |
| High engagement | 84.7 | +39.7 | 100% | 0% | 0% | 4.4 |
| High-harm context | 89.6 | +24.6 | 100% | 0% | 0% | 1.9 |
| Instigator-heavy | 85.0 | +40.0 | 100% | 0% | 0% | 4.2 |
| Low-harm context | 82.4 | +57.4 | 100% | 0% | 0% | 13.3 |
| Neutral-heavy | 84.9 | +39.9 | 100% | 0% | 0% | 5.2 |

### Interpretation

The high-harm context escalated fastest, reaching the escalation threshold in about 2 steps on average.

The low-harm context escalated more slowly, taking about 13 steps on average, but still eventually crossed the escalation threshold under the tested role mix.

This suggests that the current model treats harmful content pressure as a constant upward force. Bystander behaviour matters, but under standard settings it mostly changes the speed of escalation rather than fully changing the final outcome.

## Role Mix Sweep

This test gradually replaced instigators with defenders while keeping the rest of the scenario mostly stable.

| Role mix | Mean final bullying level | Mean change | Mean steps |
| --- | ---: | ---: | ---: |
| Defenders 0% / Instigators 60% | 86.0 | +41.0 | 3.9 |
| Defenders 10% / Instigators 50% | 84.8 | +39.8 | 4.2 |
| Defenders 20% / Instigators 40% | 85.0 | +40.0 | 4.4 |
| Defenders 30% / Instigators 30% | 85.4 | +40.4 | 4.8 |
| Defenders 40% / Instigators 20% | 84.9 | +39.9 | 5.1 |
| Defenders 50% / Instigators 10% | 84.0 | +39.0 | 5.3 |
| Defenders 60% / Instigators 0% | 83.9 | +38.9 | 6.0 |

### Interpretation

More defenders delayed escalation, but did not stop it under the standard harm settings.

This is an important model diagnosis. It means the dashboard currently shows the direction of bystander influence, but the harmful-content pressure is calibrated so strongly that role mix alone is not enough to calm the situation unless the scenario is already low risk.

## Behaviour Module Comparison

This test compared four behaviour settings:

- rules only
- social influence only
- learning only
- social influence plus learning

| Behaviour setting | Mean final bullying level | Mean change | Got worse | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| Learning only | 84.5 | +39.5 | 100% | 5.0 |
| Rules only | 83.7 | +38.7 | 100% | 5.5 |
| Social + learning | 84.5 | +39.5 | 100% | 4.9 |
| Social influence only | 83.0 | +38.0 | 100% | 5.4 |

### Interpretation

Under the standard settings, ToM and learning did not substantially change the final outcome.

This does not mean ToM and learning are useless. It means their effect is currently smaller than the harmful-content pressure in the model. For the scientific write-up, this can be described as a calibration finding:

**The adaptive behaviour modules are present, but the current environmental pressure dominates agent adaptation in moderate-to-high harm scenarios.**

## Targeted Calming Test

Because the main scenarios mostly escalated, a second experiment tested whether defenders can calm the environment under lower-harm conditions.

| Case | Mean final bullying level | Mean change | Got worse | Calmed down | Unresolved | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 40% defenders low harm | 81.6 | +56.6 | 98% | 0% | 2% | 13.6 |
| 60% defenders low harm | 60.1 | +35.1 | 34% | 20% | 46% | 15.7 |
| 80% defenders low harm | 29.5 | +4.5 | 0% | 74% | 26% | 9.0 |
| 90% defenders low harm | 21.2 | -3.8 | 0% | 92% | 8% | 5.5 |
| 80% defenders toxicity 0 | 18.4 | -6.6 | 0% | 100% | 0% | 3.8 |
| 80% defenders toxicity 10 | 25.3 | +0.3 | 0% | 82% | 18% | 8.2 |
| 80% defenders toxicity 25 | 64.7 | +39.7 | 54% | 22% | 24% | 15.5 |
| 80% defenders toxicity 50 | 83.3 | +58.3 | 100% | 0% | 0% | 10.5 |
| 80% defenders toxicity 75 | 84.4 | +59.4 | 100% | 0% | 0% | 7.6 |
| 80% defenders initial 15 | 14.8 | -0.2 | 0% | 100% | 0% | 1.0 |
| 80% defenders initial 25 | 23.9 | -1.1 | 0% | 86% | 14% | 7.8 |
| 80% defenders initial 35 | 24.3 | -10.7 | 0% | 84% | 16% | 11.4 |
| 80% defenders initial 45 | 28.5 | -16.5 | 6% | 76% | 18% | 14.7 |
| 80% defenders initial 60 | 34.5 | -25.5 | 22% | 44% | 34% | 15.8 |

### Interpretation

This test shows that the model can produce calming outcomes, but only under certain conditions.

Defenders are most effective when:

- defender presence is very high
- toxicity is low
- profanity is low
- identity attack is low
- starting aggression is not already too close to the escalation threshold

The most useful result is the toxicity sensitivity:

- At toxicity 0, 80% defenders calmed the situation in 100% of runs.
- At toxicity 10, 80% defenders calmed the situation in 82% of runs.
- At toxicity 25, outcomes became mixed.
- At toxicity 50 or higher, the situation escalated in 100% of runs.

This suggests that toxicity is one of the strongest drivers in the current model.

## Continual Learning Result

The continual learning run carried memory across 40 repeated simulations.

The model learned strongly from repeated escalation outcomes. Because instigator actions were repeatedly associated with escalation, bully-support tendency increased across runs. Defender and silent tendencies became more negative because those actions were not consistently associated with reducing harm under the tested baseline scenario.

In simple terms:

**The model currently learns the behaviour that appears successful inside the simulated environment. Since the baseline environment escalates often, the learning system reinforces harmful support unless the reward design is adjusted to prioritise victim safety more strongly.**

This is a valuable scientific finding because it shows that reward design matters. If the goal is bullying intervention, the reward system should not simply learn from whether escalation happened. It should be explicitly designed around reducing harm and supporting the victim.

## Scientific Conclusion

The sensitivity analysis shows that the current Mesa simulation behaves consistently, but it is calibrated toward escalation under standard settings.

The environment is most affected by:

1. **Toxicity and harmful-content pressure:** higher toxicity causes faster escalation.
2. **Defender dominance:** defenders can calm the situation, but mainly when they strongly outnumber instigators and the content is not too harmful.
3. **Neutral or silent behaviour:** silence does not directly attack the victim, but it does not provide enough counter-pressure to stop escalation.
4. **Engagement pressure:** likes and retweets increase the speed of escalation.
5. **Learning design:** agents learn from outcomes, so reward design strongly shapes future behaviour.

## Recommended Model Improvements

For the next version, the model should be recalibrated so the dashboard shows a wider range of realistic outcomes.

Recommended changes:

- Reduce the constant harmful-content pressure slightly.
- Increase the effect of defenders when they act together.
- Add a collective defence effect when defenders are the clear majority.
- Penalise instigator learning more strongly when the final outcome is harmful.
- Reward defender behaviour based on victim safety, not only immediate bullying-level decrease.
- Add a moderation or reporting effect when toxicity is very high.

These changes would make the simulation better for scientific demonstration because it would show not only escalation, but also realistic pathways to calming and unresolved outcomes.

## Output Files

The numerical results were saved in:

- `sensitivity_outputs/sensitivity_runs.csv`
- `sensitivity_outputs/sensitivity_summary.csv`
- `sensitivity_outputs/targeted_calming_summary.csv`
- `sensitivity_outputs/trajectory_summary.csv`
- `sensitivity_outputs/continual_learning_runs.csv`

