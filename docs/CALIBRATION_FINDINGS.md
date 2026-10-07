# Calibration Findings

The repository already contains repeated-run sensitivity experiments under `sensitivity_outputs/`.

These experiments are useful because they reveal what the current model actually does under different assumptions instead of relying on one dashboard demonstration.

## Main calibration finding

Under the standard dashboard calibration, harmful-content pressure is strong enough that most moderate- and high-harm scenarios escalate.

Across the original repeated-run experiments:

- the balanced baseline escalated in 100% of 40 runs;
- the defender-heavy baseline still escalated in 100% of 40 runs;
- the high-harm context escalated fastest, reaching the escalation threshold in about 1.9 steps on average;
- increasing defenders from 0% to 60% delayed escalation but did not reverse the standard-harm scenarios.

This indicates that the current parameterization is **escalation-dominant** under standard harm settings.

## When calming becomes possible

Targeted low-harm experiments show that defenders can change the outcome when they strongly dominate and the harmful-content pressure is low.

Examples from 50-run experiments:

| Scenario | Escalated | Calmed | Unresolved |
|---|---:|---:|---:|
| 60% defenders, low harm | 34% | 20% | 46% |
| 80% defenders, low harm | 0% | 74% | 26% |
| 90% defenders, low harm | 0% | 92% | 8% |
| 80% defenders, toxicity 0 | 0% | 100% | 0% |
| 80% defenders, toxicity 10 | 0% | 82% | 18% |
| 80% defenders, toxicity 50 | 100% | 0% | 0% |
| 80% defenders, toxicity 75 | 100% | 0% | 0% |

## Interpretation

The current model is especially sensitive to toxicity.

Defender presence influences outcomes, but at moderate-to-high toxicity the environmental pressure dominates agent adaptation.

This is not presented as evidence about real-world causal effects. It is a diagnosis of the current model calibration.

## Learning finding

Under the escalation-dominant baseline, reward-based learning can reinforce harmful-support behaviour because the learning mechanism rewards actions that appear successful inside the simulated environment.

This highlights an important modelling lesson:

**reward design determines what adaptive agents learn.**

A future safety-oriented calibration should reward reduction of victim harm directly rather than treating escalation as successful simply because it aligns with an instigator role.

## Why this is retained

These findings are kept visible because sensitivity analysis is part of model validation.

A model should not be judged only by whether its outputs look intuitive. It should be examined for:

- dominant assumptions;
- parameter sensitivity;
- failure modes;
- outcome imbalance;
- robustness across random seeds.

The existing sensitivity outputs therefore function as a documented calibration audit.

For the full historical report, see `../sensitivity_outputs/SENSITIVITY_ANALYSIS_REPORT.md`.
