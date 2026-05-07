# Sensitivity Analysis Methods and Parameter Settings

## 1. What Was Tested

The sensitivity analysis tested how the current Mesa-based cyber-bystander simulation responds when the environment parameters are changed.

The main question was:

**How does the simulated bullying level change over time when we change bystander roles, harmful-content levels, engagement, and learning behaviour?**

The simulation was not used as a prediction model. It was used as an agent-based behavioural experiment.

## 2. Mesa Backend Used

The experiment used the current Mesa backend in the project.

Main files used:

- `mesa_bridge.py`
- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`

The experiment called:

```python
from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState
```

Each run created a `SimulationConfig`, passed it into `simulate_scenario`, and collected the resulting bullying-level history, final outcome, role composition, and learning state.

## 3. Core Mesa Simulation Process

Each simulation run followed this process:

1. Create a Mesa model using `CyberBystanderMesaModel`.
2. Convert bystander role percentages into actual agent counts.
3. Create bystander agents:
   - Instigator agents
   - Defender agents
   - Neutral agents
   - Other agents
4. Set the starting bullying level.
5. Set harmful-content context:
   - toxicity
   - profanity
   - identity attack
   - likes
   - retweets
6. Run the model step by step.
7. At each step, Mesa activates agents using:

```python
self.agents.shuffle_do("step")
```

8. Each active agent chooses an action:
   - `support_bully`
   - `support_victim`
   - `stay_silent`
   - `step_aside`
9. The model calculates how much the bullying level changes.
10. The model checks whether the conversation:
   - got worse
   - calmed down
   - stayed unresolved
11. Results are collected with Mesa `DataCollector`.

## 4. Default Parameter Values

These were the base settings used unless a scenario changed them.

| Parameter | Value | Plain-English meaning |
| --- | ---: | --- |
| `total_bystanders` | 24 | Total people replying/watching in the simulated conversation |
| `instigator_pct` | 25.0 | Percentage of bystanders likely to support the bully |
| `defender_pct` | 25.0 | Percentage of bystanders likely to support the victim |
| `neutral_pct` | 35.0 | Percentage of bystanders likely to stay silent |
| `other_pct` | 15.0 | Percentage of unrelated/low-impact bystanders |
| `initial_aggression` | 45.0 | Starting bullying level |
| `toxicity_level` | 50.0 | Harmfulness/toxicity of the original situation |
| `profanity_level` | 35.0 | Strength of profanity in the situation |
| `identity_attack_level` | 35.0 | Strength of identity-based attack |
| `like_influence` | 35.0 | Extra pressure from likes/favourites |
| `retweet_influence` | 35.0 | Extra pressure from retweets/shares |
| `simulation_speed` | 0.5 | Dashboard display speed; not used in scientific calculation |
| `tom_influence_strength` | 0.55 | Strength of social influence / Theory of Mind effect |
| `learning_rate` | 0.30 | How quickly agents update from rewards |
| `reward_strength` | 0.90 | How strongly rewards affect learned tendencies |
| `memory_retention_strength` | 0.80 | How much past learning is retained |
| `adaptation_speed` | 0.35 | How quickly new experience changes memory |
| `carry_learning` | False | Whether learning carries into the next independent run |
| `max_steps` | 18 | Maximum simulation steps before stopping |
| `escalation_threshold` | 80.0 | If bullying reaches this level, outcome is “Got worse” |
| `calming_threshold` | 20.0 | If bullying drops to this level, outcome is “Calmed down” |

## 5. How Percentages Became Mesa Agents

The model converted role percentages into actual agent counts using `percentages_to_counts` in `mesa_model.py`.

For the default setting:

| Role | Percentage | Approximate count out of 24 |
| --- | ---: | ---: |
| Instigator | 25% | 6 |
| Defender | 25% | 6 |
| Neutral | 35% | 8 |
| Other | 15% | 4 |

The total always equals 24 agents after rounding.

## 6. Agent Participation Probabilities

Not every agent acts at every step. Each role has a probability of participating based on the current bullying level and harmful-content context.

The model uses this logic:

```python
bullying_ratio = bullying_intensity / 100
toxicity_ratio = toxicity_level / 100
identity_ratio = identity_attack_level / 100
```

Participation probability by role:

```python
instigator = min(0.92, 0.30 + 0.24 * bullying_ratio + 0.20 * toxicity_ratio)
defender   = min(0.88, 0.20 + 0.25 * bullying_ratio + 0.12 * identity_ratio)
neutral    = min(0.80, 0.18 + 0.16 * bullying_ratio)
other      = 0.12
```

Using the default starting settings:

- bullying level = 45, so bullying ratio = 0.45
- toxicity level = 50, so toxicity ratio = 0.50
- identity attack level = 35, so identity ratio = 0.35

Approximate starting participation probabilities:

| Role | Calculation | Starting probability |
| --- | --- | ---: |
| Instigator | `0.30 + 0.24*0.45 + 0.20*0.50` | 0.508 |
| Defender | `0.20 + 0.25*0.45 + 0.12*0.35` | 0.3545 |
| Neutral | `0.18 + 0.16*0.45` | 0.252 |
| Other | fixed | 0.12 |

This means instigators are more likely to act early in the default setting.

## 7. Agent Action Choices

Agents choose from four actions:

| Action | Plain-English meaning |
| --- | --- |
| `support_bully` | Supports or reinforces the harmful post |
| `support_victim` | Defends or supports the victim |
| `stay_silent` | Does not intervene |
| `step_aside` | Acts unrelated or has little impact |

Each role starts with built-in action preferences.

| Role | support bully | support victim | stay silent | step aside |
| --- | ---: | ---: | ---: | ---: |
| Instigator | 0.62 | 0.08 | 0.22 | 0.08 |
| Defender | 0.08 | 0.62 | 0.22 | 0.08 |
| Neutral | 0.12 | 0.15 | 0.60 | 0.13 |
| Other | 0.08 | 0.10 | 0.20 | 0.62 |

The final action choice combines:

1. role-based starting preference
2. learned values from reward updates
3. social influence / Theory of Mind adjustment

## 8. Theory of Mind / Social Influence Settings

Theory of Mind was implemented as simple social-context reasoning.

Agents looked at what happened in the previous step:

- how many supported the bully
- how many defended the victim
- how many stayed silent

The model converted this into:

```python
bully_support_pressure = previous_support_bully_count / total_agents
defence_pressure = previous_support_victim_count / total_agents
silence_pressure = previous_stay_silent_count / total_agents
```

Then each agent adjusted its action weights:

```python
support_bully  += 0.35 * bully_support_pressure * tom_influence_strength * role_sensitivity
support_victim += 0.35 * defence_pressure * tom_influence_strength * role_sensitivity
stay_silent    += 0.35 * silence_pressure * tom_influence_strength * role_sensitivity
step_aside     += 0.08
```

Role sensitivities:

| Role | Social sensitivity |
| --- | ---: |
| Instigator | 0.90 |
| Defender | 0.95 |
| Neutral | 1.15 |
| Other | 0.80 |

Default ToM influence strength:

```python
tom_influence_strength = 0.55
```

In plain English:

**Agents became slightly more likely to copy what seemed common in the conversation.**

## 9. Bullying-Level Change Formula

At every step, the model calculated the change in bullying level.

The formula was:

```python
content_pressure =
    5.2 * toxicity_ratio
  + 3.0 * profanity_ratio
  + 4.1 * identity_ratio
  + 2.2 * engagement_ratio

support_pressure =
    support_bully_count / total_bystanders * (16 + 6 * toxicity_ratio)

defence_pressure =
    support_victim_count / total_bystanders * (16 + 5 * identity_ratio)

silence_pressure =
    stay_silent_count / total_bystanders * (5 + 4 * bullying_ratio)

unrelated_pressure =
    step_aside_count / total_bystanders * 1.2

randomness =
    random number between -1.0 and +1.0

bullying_change =
    content_pressure
  + support_pressure
  + silence_pressure
  + 0.4 * unrelated_pressure
  - defence_pressure
  + randomness
```

The new bullying level was:

```python
new_bullying_level = old_bullying_level + bullying_change
```

The value was kept between 0 and 100.

## 10. Default Starting Pressure Calculation

Using default settings:

| Input | Value |
| --- | ---: |
| Bullying ratio | 0.45 |
| Toxicity ratio | 0.50 |
| Profanity ratio | 0.35 |
| Identity attack ratio | 0.35 |
| Engagement ratio | 0.35 |

Default content pressure:

```text
5.2*0.50 + 3.0*0.35 + 4.1*0.35 + 2.2*0.35
= 2.60 + 1.05 + 1.435 + 0.77
= 5.855
```

This means that, before bystander actions are even added, the environment has an upward harmful-content pressure of about `+5.86` per step.

This explains why the default environment tends to escalate unless defenders create enough counter-pressure.

## 11. Reinforcement Learning Settings

Learning was simple reward-based updating.

The update rule was:

```python
new_value = current_value + learning_rate * reward_strength * reward
```

Default values:

```python
learning_rate = 0.30
reward_strength = 0.90
```

So each reward was multiplied by:

```text
0.30 * 0.90 = 0.27
```

Reward rules:

| Role | Action | Reward condition |
| --- | --- | --- |
| Instigator | support bully | +1.0 if bullying increased, -0.8 if bullying decreased |
| Instigator | other actions | +0.2 if bullying increased, -0.3 if bullying decreased |
| Defender | support victim | +1.0 if bullying decreased, -0.8 if bullying increased |
| Defender | other actions | +0.2 if bullying decreased, -0.3 if bullying increased |
| Neutral | stay silent | -0.7 if bullying increased, +0.1 if bullying decreased |
| Neutral | support victim | +0.6 if bullying decreased, -0.2 if bullying increased |
| Other | step aside | +0.1 if change was small, -0.1 otherwise |

## 12. Continual Learning Settings

Continual learning was tested separately using a persistent `MesaLearningState`.

The memory update formula was:

```python
stored_value =
    memory_retention_strength * old_stored_value
  + adaptation_speed * new_working_value
```

Default values:

```python
memory_retention_strength = 0.80
adaptation_speed = 0.35
```

In plain English:

**The model keeps much of its old learning, but also blends in new experience.**

The continual learning experiment ran:

```text
40 repeated simulations
seeds 501 to 540
carry_learning = True
```

## 13. Experiment 1: Scenario Comparison

Each scenario was run 40 times.

Seeds used:

```text
100 to 139
```

### Scenario Parameter Table

| Scenario | Changed parameters |
| --- | --- |
| Balanced baseline | no changes from default |
| Instigator-heavy | instigator 50%, defender 15%, neutral 25%, other 10% |
| Defender-heavy | instigator 15%, defender 50%, neutral 25%, other 10% |
| Neutral-heavy | instigator 15%, defender 15%, neutral 60%, other 10% |
| Low-harm context | initial aggression 25, toxicity 20, profanity 15, identity attack 10, likes 15, retweets 15 |
| High-harm context | initial aggression 65, toxicity 85, profanity 75, identity attack 80, likes 70, retweets 70 |
| High engagement | likes 85, retweets 85 |

All other parameters stayed at their default values.

### Results

| Scenario | Mean final bullying level | Mean change | Got worse | Calmed down | Unresolved | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Balanced baseline | 85.3 | +40.3 | 100% | 0% | 0% | 5.0 |
| Defender-heavy | 84.0 | +39.0 | 100% | 0% | 0% | 5.2 |
| High engagement | 84.7 | +39.7 | 100% | 0% | 0% | 4.4 |
| High-harm context | 89.6 | +24.6 | 100% | 0% | 0% | 1.9 |
| Instigator-heavy | 85.0 | +40.0 | 100% | 0% | 0% | 4.2 |
| Low-harm context | 82.4 | +57.4 | 100% | 0% | 0% | 13.3 |
| Neutral-heavy | 84.9 | +39.9 | 100% | 0% | 0% | 5.2 |

### How the conclusion was reached

The final outcome was counted across 40 runs per scenario.

Because all standard scenarios reached the escalation threshold in 100% of runs, the conclusion was:

**Under the current standard calibration, the simulation strongly tends toward escalation.**

The mean steps show speed:

- high-harm context escalated fastest, in about 1.9 steps
- low-harm context escalated slower, in about 13.3 steps

This shows that lower harm delays escalation, but did not stop escalation under the tested baseline role mix.

## 14. Experiment 2: Behaviour Module Comparison

Each setting was run 40 times.

Seeds used:

```text
100 to 139
```

### Behaviour Settings

| Setting | ToM influence | Learning rate | Reward strength | Memory retention | Adaptation speed | Carry learning |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Rules only | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | False |
| Social influence only | 0.65 | 0.00 | 0.00 | 0.00 | 0.00 | False |
| Learning only | 0.00 | 0.35 | 0.90 | 0.00 | 0.00 | False |
| Social + learning | 0.65 | 0.35 | 0.90 | 0.80 | 0.35 | True |

### Results

| Behaviour setting | Mean final bullying level | Mean change | Got worse | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| Learning only | 84.5 | +39.5 | 100% | 5.0 |
| Rules only | 83.7 | +38.7 | 100% | 5.5 |
| Social + learning | 84.5 | +39.5 | 100% | 4.9 |
| Social influence only | 83.0 | +38.0 | 100% | 5.4 |

### How the conclusion was reached

All four behaviour settings escalated in 100% of runs.

The difference in mean final bullying level was small:

- lowest mean final level: 83.0
- highest mean final level: 84.5

Therefore, the conclusion was:

**Under the standard environment settings, harmful-content pressure dominates the adaptive behaviour modules.**

This means ToM and learning are present, but their effect is not strong enough to reverse escalation under the default harmful-content settings.

## 15. Experiment 3: Role Mix Sweep

This experiment gradually replaced instigators with defenders.

Each setting was run 40 times.

Seeds used:

```text
100 to 139
```

Fixed values:

```text
neutral = 30%
other = 10%
```

Changed values:

| Role mix | Instigator % | Defender % | Neutral % | Other % |
| --- | ---: | ---: | ---: | ---: |
| Defenders 0% / Instigators 60% | 60 | 0 | 30 | 10 |
| Defenders 10% / Instigators 50% | 50 | 10 | 30 | 10 |
| Defenders 20% / Instigators 40% | 40 | 20 | 30 | 10 |
| Defenders 30% / Instigators 30% | 30 | 30 | 30 | 10 |
| Defenders 40% / Instigators 20% | 20 | 40 | 30 | 10 |
| Defenders 50% / Instigators 10% | 10 | 50 | 30 | 10 |
| Defenders 60% / Instigators 0% | 0 | 60 | 30 | 10 |

### Results

| Role mix | Mean final bullying level | Mean change | Mean steps |
| --- | ---: | ---: | ---: |
| Defenders 0% / Instigators 60% | 86.0 | +41.0 | 3.9 |
| Defenders 10% / Instigators 50% | 84.8 | +39.8 | 4.2 |
| Defenders 20% / Instigators 40% | 85.0 | +40.0 | 4.4 |
| Defenders 30% / Instigators 30% | 85.4 | +40.4 | 4.8 |
| Defenders 40% / Instigators 20% | 84.9 | +39.9 | 5.1 |
| Defenders 50% / Instigators 10% | 84.0 | +39.0 | 5.3 |
| Defenders 60% / Instigators 0% | 83.9 | +38.9 | 6.0 |

### How the conclusion was reached

As defenders increased, the mean number of steps before escalation increased:

- 0% defenders: 3.9 steps
- 60% defenders: 6.0 steps

But the final bullying level still stayed above the escalation threshold.

Therefore, the conclusion was:

**More defenders slowed escalation, but did not prevent escalation under standard harmful-content settings.**

## 16. Experiment 4: Targeted Calming Test

Because the first three experiments showed strong escalation, a fourth experiment tested whether the model can produce calming outcomes under lower-risk conditions.

Each setting was run 50 times.

Seeds used:

```text
200 to 249
```

### Targeted Calming Results

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

### How the conclusion was reached

This experiment showed that defenders can calm the simulation when:

- defenders strongly dominate
- toxicity is low
- the starting aggression is not already too severe

The clearest numeric evidence is the toxicity test with 80% defenders:

| Toxicity | Calmed down rate | Got worse rate |
| ---: | ---: | ---: |
| 0 | 100% | 0% |
| 10 | 82% | 0% |
| 25 | 22% | 54% |
| 50 | 0% | 100% |
| 75 | 0% | 100% |

Therefore, the conclusion was:

**Toxicity is one of the strongest drivers of escalation in the current model.**

## 17. Experiment 5: Continual Learning Across Repeated Runs

This experiment tested memory across repeated simulations.

Settings:

```text
runs = 40
seeds = 501 to 540
carry_learning = True
memory_retention_strength = 0.80
adaptation_speed = 0.35
learning_rate = 0.30
reward_strength = 0.90
```

The same persistent `MesaLearningState` was passed from one run into the next.

### First Run

| Metric | Value |
| --- | ---: |
| Final bullying level | 87.44 |
| Change | +42.44 |
| Outcome | Got worse |
| Defender tendency | -0.0898 |
| Bully-support tendency | 0.2150 |
| Silent tendency | -0.0614 |
| Defender action share | 16.3% |
| Bully-support action share | 44.2% |
| Silent action share | 18.6% |

### Final Run

| Metric | Value |
| --- | ---: |
| Final bullying level | 92.61 |
| Change | +47.61 |
| Outcome | Got worse |
| Defender tendency | -102.14 |
| Bully-support tendency | 492.53 |
| Silent tendency | -62.36 |
| Defender action share | 2.4% |
| Bully-support action share | 66.7% |
| Silent action share | 19.0% |

### How the conclusion was reached

The learning state showed that bully-support tendency increased strongly across repeated runs.

This happened because, in the current reward setup, instigator agents are rewarded when bullying increases. Since the baseline environment often escalates, bully-support actions become increasingly reinforced.

Therefore, the conclusion was:

**The current learning system learns what is rewarded inside the simulation. If the environment rewards escalation, harmful behaviour can become stronger.**

This is not a bug in reinforcement learning. It is a lesson about reward design.

For a bullying-intervention project, future reward logic should prioritise harm reduction and victim safety more strongly.

## 18. How the Final Conclusions Were Produced

The final conclusions came from comparing:

1. mean final bullying levels
2. mean change from start to end
3. percentage of runs that got worse
4. percentage of runs that calmed down
5. average number of steps before stopping
6. learning tendency changes across repeated runs

The strongest conclusions were:

### Conclusion 1: The current model is escalation-biased.

Evidence:

- Standard scenarios escalated in 100% of runs.
- Balanced baseline mean final bullying level was 85.3.
- Escalation threshold was 80.

### Conclusion 2: Defenders slow escalation under standard settings.

Evidence:

- With 0% defenders, escalation happened in about 3.9 steps.
- With 60% defenders, escalation happened in about 6.0 steps.

### Conclusion 3: Defenders can calm the environment under low-harm settings.

Evidence:

- 80% defenders in low harm calmed down in 74% of runs.
- 90% defenders in low harm calmed down in 92% of runs.

### Conclusion 4: Toxicity is a strong driver of escalation.

Evidence:

- With 80% defenders and toxicity 0, 100% of runs calmed down.
- With 80% defenders and toxicity 50, 100% of runs got worse.

### Conclusion 5: Current learning logic needs careful reward design.

Evidence:

- In repeated baseline runs, bully-support tendency increased from 0.2150 to 492.53.
- This happened because harmful support was rewarded when escalation occurred.

## 19. Output Files Created

The following files were produced:

| File | Purpose |
| --- | --- |
| `sensitivity_runs.csv` | Every individual scenario run |
| `sensitivity_summary.csv` | Summary of scenario, role mix, and module experiments |
| `targeted_calming_summary.csv` | Low-harm and defender-dominant tests |
| `average_trajectories_over_time.csv` | Step-by-step mean bullying level over time |
| `trajectory_summary.csv` | Additional trajectory summary |
| `continual_learning_runs.csv` | Repeated-run continual learning results |
| `SENSITIVITY_ANALYSIS_REPORT.md` | Shareable written report |
| `SENSITIVITY_ANALYSIS_REPORT.pdf` | PDF report for the team |

## 20. Important Scientific Limitation

The results are valid for the current simulation calibration only.

They do not prove that real cyberbullying always escalates. They show how the current Mesa model behaves under the tested assumptions.

This is still useful because sensitivity analysis reveals model behaviour. In this case, it revealed that harmful-content pressure is currently very strong, and the next scientific improvement should be recalibration.

