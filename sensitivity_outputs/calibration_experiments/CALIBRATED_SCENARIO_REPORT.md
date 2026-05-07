# Calibrated Scenario Report

## Purpose

The first sensitivity analysis showed that the default Mesa simulation was strongly biased toward escalation. That was useful because it revealed how the current model behaves, but it did not give enough variety for scientific explanation.

This second calibration experiment was designed to find different behavioural regimes:

- calming or very low escalation
- low escalation
- medium escalation or unresolved risk
- high escalation
- tipping-point scenarios where outcomes are mixed

The goal is to help explain how different combinations of bystander roles and harmful-content pressure affect the simulated environment over time.

## What Changed From the First Report

The first report mostly used the dashboard's standard settings:

- starting bullying level around 45
- toxicity around 50
- moderate profanity and identity attack
- balanced or moderately varied bystander mixes

Those settings created strong upward pressure, so most scenarios escalated.

In this calibration experiment, I tested lower and middle harm levels more carefully. This lets the model show a wider range of outcomes.

## Mesa Simulation Method

The same Mesa backend was used:

- `mesa_bridge.py`
- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`

Each scenario was repeated across multiple random seeds. This means the results are averages across repeated simulation runs, not one single example.

The core stopping rules stayed the same:

| Condition | Outcome |
| --- | --- |
| bullying level reaches 80 or above | Got worse |
| bullying level reaches 20 or below | Calmed down |
| maximum steps reached without either threshold | Stayed unresolved |

## Default Model Settings Kept Constant

Unless a scenario changed them, these settings were kept the same:

| Parameter | Value |
| --- | ---: |
| total bystanders | 24 |
| maximum steps | 18 |
| ToM influence strength | 0.55 |
| learning rate | 0.30 |
| reward strength | 0.90 |
| memory retention strength | 0.80 |
| adaptation speed | 0.35 |
| carry learning across independent runs | False |
| escalation threshold | 80 |
| calming threshold | 20 |

## Broad Calibration Grid

The first calibration grid tested:

```text
6 harm profiles x 5 bystander profiles x 30 repeated runs
```

This produced:

```text
900 Mesa simulation runs
```

### Harm Profiles

| Harm profile | Starting bullying | Toxicity | Profanity | Identity attack | Likes | Retweets |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Very low harm | 15 | 0 | 0 | 0 | 5 | 5 |
| Low harm | 25 | 10 | 5 | 5 | 10 | 10 |
| Mild harm | 35 | 15 | 10 | 10 | 20 | 20 |
| Medium harm | 40 | 25 | 15 | 20 | 25 | 25 |
| Upper-medium harm | 45 | 35 | 25 | 30 | 35 | 35 |
| High harm | 55 | 50 | 35 | 45 | 50 | 50 |

### Bystander Mix Profiles

| Bystander profile | Bully supporters | Victim supporters | Silent bystanders | Other |
| --- | ---: | ---: | ---: | ---: |
| Protective majority | 5% | 70% | 20% | 5% |
| Defender leaning | 15% | 55% | 25% | 5% |
| Balanced discussion | 25% | 35% | 30% | 10% |
| Silent majority | 15% | 20% | 55% | 10% |
| Bully-support leaning | 45% | 20% | 25% | 10% |

## Broad Calibration Findings

The broad grid showed clear high and very-low regimes, but the low and medium regimes needed a finer search.

### Very Low / Calming Examples

| Scenario | Mean final level | Change | Got worse | Calmed down | Unresolved | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Very low harm + Protective majority | 14.4 | -0.6 | 0% | 100% | 0% | 1.0 |
| Very low harm + Defender leaning | 14.7 | -0.3 | 0% | 100% | 0% | 1.0 |
| Very low harm + Balanced discussion | 15.6 | +0.6 | 0% | 100% | 0% | 1.0 |
| Very low harm + Silent majority | 15.8 | +0.8 | 0% | 100% | 0% | 1.0 |
| Very low harm + Bully-support leaning | 16.3 | +1.3 | 0% | 100% | 0% | 1.0 |

### Medium / Unresolved Examples

| Scenario | Mean final level | Change | Got worse | Calmed down | Unresolved | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mild harm + Protective majority | 59.9 | +24.9 | 43% | 20% | 37% | 16.0 |
| Low harm + Defender leaning | 50.0 | +25.0 | 17% | 30% | 53% | 16.2 |

### High Escalation Examples

| Scenario | Mean final level | Change | Got worse | Calmed down | Unresolved | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High harm + Protective majority | 84.3 | +29.3 | 100% | 0% | 0% | 4.2 |
| High harm + Balanced discussion | 85.0 | +30.0 | 100% | 0% | 0% | 3.5 |
| High harm + Silent majority | 85.2 | +30.2 | 100% | 0% | 0% | 3.7 |
| Medium harm + Bully-support leaning | 84.2 | +44.2 | 100% | 0% | 0% | 6.8 |

## Fine Calibration Search

The broad grid showed that low and medium escalation happen around a tipping point. To find those cases more clearly, I ran a finer search.

This search tested:

```text
588 parameter combinations x 30 repeated runs
```

This produced:

```text
17,640 Mesa simulation runs
```

The fine search varied:

- starting bullying level from 22 to 42
- toxicity from 0 to 30
- defenders from 50% to 80%
- instigators from 5% to 20%
- neutral bystanders as the remaining percentage

## Recommended Calibrated Scenarios

These are the best scenarios to use in your project presentation because they show different outcomes clearly.

## Scenario A: Low Escalation / Mostly Controlled

### Parameter Settings

| Parameter | Value |
| --- | ---: |
| starting bullying level | 38 |
| toxicity | 5 |
| profanity | 2.5 |
| identity attack | 3 |
| likes | 5 |
| retweets | 5 |
| bully supporters | 15% |
| victim supporters | 60% |
| silent bystanders | 20% |
| other | 5% |

### Results

| Metric | Value |
| --- | ---: |
| mean final bullying level | 34.6 |
| mean change | -3.4 |
| got worse | 0% |
| calmed down | 40% |
| stayed unresolved | 60% |

### Interpretation

This is a low-escalation scenario. The bullying does not usually become severe. The strong defender presence prevents the situation from getting worse, but it does not always fully calm the conversation.

In simple terms:

**People defending the victim keep the situation under control, but the conversation may still remain tense or unresolved.**

## Scenario B: Low Escalation With Balanced Pressure

### Parameter Settings

| Parameter | Value |
| --- | ---: |
| starting bullying level | 38 |
| toxicity | 0 |
| profanity | 0 |
| identity attack | 0 |
| likes | 5 |
| retweets | 5 |
| bully supporters | 20% |
| victim supporters | 50% |
| silent bystanders | 25% |
| other | 5% |

### Results

| Metric | Value |
| --- | ---: |
| mean final bullying level | 35.1 |
| mean change | -2.9 |
| got worse | 0% |
| calmed down | 50% |
| stayed unresolved | 50% |

### Interpretation

This scenario shows low escalation when the harmful-content level is very low. Even with some bully supporters, the lack of toxicity makes the situation easier to contain.

In simple terms:

**When the original situation is not very harmful, defenders can keep the conversation from becoming dangerous.**

## Scenario C: Medium Escalation / Unresolved Risk

### Parameter Settings

| Parameter | Value |
| --- | ---: |
| starting bullying level | 42 |
| toxicity | 10 |
| profanity | 5 |
| identity attack | 6 |
| likes | 10 |
| retweets | 10 |
| bully supporters | 20% |
| victim supporters | 60% |
| silent bystanders | 15% |
| other | 5% |

### Results

| Metric | Value |
| --- | ---: |
| mean final bullying level | 54.6 |
| mean change | +12.6 |
| got worse | 47% |
| calmed down | 3% |
| stayed unresolved | 50% |

### Interpretation

This is a medium-risk scenario. Even though defenders are the majority, the situation often remains unresolved and sometimes escalates.

In simple terms:

**Defenders help, but the starting bullying level and harmful content are high enough that the situation is still risky.**

## Scenario D: Medium Mixed Outcome

### Parameter Settings

| Parameter | Value |
| --- | ---: |
| starting bullying level | 38 |
| toxicity | 10 |
| profanity | 5 |
| identity attack | 6 |
| likes | 10 |
| retweets | 10 |
| bully supporters | 15% |
| victim supporters | 50% |
| silent bystanders | 30% |
| other | 5% |

### Results

| Metric | Value |
| --- | ---: |
| mean final bullying level | 53.7 |
| mean change | +15.7 |
| got worse | 33% |
| calmed down | 13% |
| stayed unresolved | 53% |

### Interpretation

This scenario is useful because it shows mixed outcomes. The situation does not always escalate, but it often remains unresolved.

In simple terms:

**The conversation is balanced on the edge. Some runs get worse, some calm down, and many stay unsettled.**

## Scenario E: Tipping-Point Scenario

### Parameter Settings

| Parameter | Value |
| --- | ---: |
| starting bullying level | 38 |
| toxicity | 15 |
| profanity | 7.5 |
| identity attack | 9 |
| likes | 15 |
| retweets | 15 |
| bully supporters | 5% |
| victim supporters | 70% |
| silent bystanders | 20% |
| other | 5% |

### Results

| Metric | Value |
| --- | ---: |
| mean final bullying level | 48.8 |
| mean change | +10.8 |
| got worse | 33% |
| calmed down | 37% |
| stayed unresolved | 30% |

### Interpretation

This is the best example of a tipping-point scenario. The same settings can lead to different outcomes because agent activation and action choices vary across runs.

In simple terms:

**This is a fragile situation. Strong defenders help, but the harmful content is strong enough that the conversation can still go either way.**

## Scenario F: High Escalation

### Parameter Settings

| Parameter | Value |
| --- | ---: |
| starting bullying level | 55 |
| toxicity | 50 |
| profanity | 35 |
| identity attack | 45 |
| likes | 50 |
| retweets | 50 |
| bully supporters | 25% |
| victim supporters | 35% |
| silent bystanders | 30% |
| other | 10% |

### Results

| Metric | Value |
| --- | ---: |
| mean final bullying level | 85.0 |
| mean change | +30.0 |
| got worse | 100% |
| calmed down | 0% |
| stayed unresolved | 0% |

### Interpretation

This is a high-escalation scenario. Harmful-content pressure is high enough that even a reasonable number of defenders cannot stop escalation.

In simple terms:

**When the original harm is severe and engagement pressure is high, the conversation gets worse very quickly.**

## What This Means Scientifically

The calibrated scenarios show that the model can represent different levels of escalation.

The earlier escalation-heavy result happened because the default settings placed the environment in a high-pressure region of the model.

The new calibration shows a more complete picture:

| Calibration type | What it shows |
| --- | --- |
| Very low harm | The situation calms quickly because there is little harmful pressure |
| Low escalation | Defenders control the situation, but it may remain unresolved |
| Medium escalation | Defenders help, but the situation is still risky |
| Tipping point | Small differences in agent behaviour can change the final outcome |
| High escalation | Toxicity and engagement overwhelm bystander defence |

## Recommended Dashboard Presets

For the dashboard, the most useful presets would be:

| Preset name | Purpose |
| --- | --- |
| Low-risk controlled conversation | Shows defenders keeping bullying low |
| Medium-risk unresolved conversation | Shows tension continuing without a clear outcome |
| Tipping-point conversation | Shows why bystander actions matter |
| High-risk escalating conversation | Shows harmful-content pressure overwhelming the environment |

## Honest Limitation

This calibration does not prove that real online conversations behave exactly this way. It shows how the current Mesa model behaves under different assumptions.

That is still valuable because agent-based modelling is about testing assumptions. The calibrated scenarios make the simulation more useful for explanation because they show more than one possible outcome.

## Output Files

The calibration experiment produced:

- `calibration_run_level_results.csv`
- `calibration_summary.csv`
- `calibration_trajectories.csv`
- `fine_calibration_search.csv`
- `recommended_calibrations.csv`
- `CALIBRATED_SCENARIO_REPORT.md`

