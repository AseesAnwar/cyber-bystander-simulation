# Post-Proposal Testing and Progress Log

## Project

**Cyber-Bystander Behaviour Simulation Using Mesa and CYBY23**

This document records the testing, calibration, interpretation, and progress completed after the project proposal stage.

It is written so the project team can explain what was tested, why it was tested, what was discovered, and how the project direction improved.

## 1. Starting Point After the Proposal

After the proposal stage, the project had already moved from a prediction-style dashboard toward a behavioural agent-based simulation.

The core project framing became:

```text
This is a Mesa-based behavioural simulation for exploring cyber-bystander dynamics, not a machine learning prediction product.
```

The simulation represents one online bullying situation with:

- one abuser or harmful source
- one victim or target
- multiple bystanders

Bystander roles:

- **Instigator:** supports the bully and can increase harm
- **Defender:** supports the victim and can reduce harm
- **Neutral:** stays silent and may indirectly allow harm to continue
- **Other:** unrelated or low-impact participant

The simulation tracks a bullying level from 0 to 100.

Outcomes:

- **Calmed down:** bullying level reaches 20 or lower
- **Got worse:** bullying level reaches 80 or higher
- **Stayed unresolved:** maximum steps are reached without either threshold

## 2. Current Technical Setup

The project uses a real Mesa backend.

Main backend files:

- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`
- `mesa_bridge.py`

Dashboard file:

- `tableau_mesa_dashboard.py`

Experiment files created after the proposal:

- `reward_design_experiments.py`

Main output folder:

- `sensitivity_outputs/`

## 3. Core Mesa Logic Used in Testing

Each run follows this process:

1. Create a `CyberBystanderMesaModel`.
2. Create bystander agents according to the chosen role mix.
3. Set starting bullying level and harmful-content settings.
4. Run the simulation step by step.
5. At each step, agents may act.
6. Agents choose actions based on role tendency, social influence, and learned values.
7. The bullying level changes.
8. Agents receive rewards if learning is enabled.
9. The simulation stops when it gets worse, calms down, or reaches the step limit.

Mesa activation method:

```python
self.agents.shuffle_do("step")
```

This means agents act in a shuffled order each step, which adds realistic variation between repeated runs.

## 4. Main Parameters Used in the Simulation

The main simulation parameters are:

| Parameter | Meaning |
| --- | --- |
| `total_bystanders` | number of bystander agents |
| `instigator_pct` | percentage supporting the bully |
| `defender_pct` | percentage supporting the victim |
| `neutral_pct` | percentage staying silent |
| `other_pct` | unrelated/low-impact percentage |
| `initial_aggression` | starting bullying level |
| `toxicity_level` | toxicity/harmfulness of the situation |
| `profanity_level` | profanity intensity |
| `identity_attack_level` | identity-based attack intensity |
| `like_influence` | engagement pressure from likes |
| `retweet_influence` | engagement pressure from retweets |
| `tom_influence_strength` | social influence / Theory of Mind effect |
| `learning_rate` | how quickly agents update from reward |
| `reward_strength` | how strongly rewards affect learning |
| `memory_retention_strength` | how much previous learning is retained |
| `adaptation_speed` | how quickly new learning changes memory |
| `carry_learning` | whether learning carries across repeated runs |

Default thresholds:

| Threshold | Value |
| --- | ---: |
| Calming threshold | 20 |
| Escalation threshold | 80 |
| Maximum steps | 18 |

## 5. First Major Test: Sensitivity Analysis

### Purpose

The first sensitivity analysis tested how the existing Mesa simulation behaved when key settings were changed.

We tested:

- role mix
- harmful-content severity
- engagement pressure
- ToM/social influence
- learning and memory settings

The purpose was to understand the current model behaviour before changing it.

### Default Test Settings

The default baseline used:

| Parameter | Value |
| --- | ---: |
| total bystanders | 24 |
| instigators | 25% |
| defenders | 25% |
| neutral | 35% |
| other | 15% |
| starting bullying level | 45 |
| toxicity | 50 |
| profanity | 35 |
| identity attack | 35 |
| likes | 35 |
| retweets | 35 |
| ToM influence | 0.55 |
| learning rate | 0.30 |
| reward strength | 0.90 |

### Scenarios Tested

Main scenarios included:

- balanced baseline
- instigator-heavy
- defender-heavy
- neutral-heavy
- low-harm context
- high-harm context
- high engagement

Each scenario was repeated across random seeds so results were not based on one run.

### Key Results

| Scenario | Mean final bullying level | Mean change | Got worse | Calmed down | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Balanced baseline | 85.3 | +40.3 | 100% | 0% | 5.0 |
| Defender-heavy | 84.0 | +39.0 | 100% | 0% | 5.2 |
| High engagement | 84.7 | +39.7 | 100% | 0% | 4.4 |
| High-harm context | 89.6 | +24.6 | 100% | 0% | 1.9 |
| Instigator-heavy | 85.0 | +40.0 | 100% | 0% | 4.2 |
| Low-harm context | 82.4 | +57.4 | 100% | 0% | 13.3 |
| Neutral-heavy | 84.9 | +39.9 | 100% | 0% | 5.2 |

### What We Learned

The model was strongly biased toward escalation under the standard settings.

This was not treated as a failure. It was treated as a diagnostic finding.

Main interpretation:

```text
The harmful-content pressure in the model was stronger than the protective effect of defenders under the default settings.
```

This meant that defenders could slow escalation, but they could not reliably stop it unless the situation was lower risk or defenders strongly dominated.

## 6. Role Mix Sweep

### Purpose

The role mix sweep tested what happens when defenders gradually replace instigators.

### Role Mix Results

| Role mix | Mean final bullying level | Mean change | Mean steps |
| --- | ---: | ---: | ---: |
| Defenders 0% / Instigators 60% | 86.0 | +41.0 | 3.9 |
| Defenders 10% / Instigators 50% | 84.8 | +39.8 | 4.2 |
| Defenders 20% / Instigators 40% | 85.0 | +40.0 | 4.4 |
| Defenders 30% / Instigators 30% | 85.4 | +40.4 | 4.8 |
| Defenders 40% / Instigators 20% | 84.9 | +39.9 | 5.1 |
| Defenders 50% / Instigators 10% | 84.0 | +39.0 | 5.3 |
| Defenders 60% / Instigators 0% | 83.9 | +38.9 | 6.0 |

### What We Learned

More defenders delayed escalation.

For example:

- 0% defenders escalated in about 3.9 steps
- 60% defenders escalated in about 6.0 steps

However, under standard harmful-content settings, even 60% defenders did not fully prevent escalation.

Conclusion:

```text
Bystander role mix matters, but environmental harm level also matters.
```

## 7. Behaviour Module Comparison

### Purpose

This test compared whether social influence and learning changed outcomes under the standard setting.

Behaviour settings tested:

- rules only
- social influence only
- learning only
- social influence plus learning

### Results

| Behaviour setting | Mean final bullying level | Mean change | Got worse | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| Learning only | 84.5 | +39.5 | 100% | 5.0 |
| Rules only | 83.7 | +38.7 | 100% | 5.5 |
| Social + learning | 84.5 | +39.5 | 100% | 4.9 |
| Social influence only | 83.0 | +38.0 | 100% | 5.4 |

### What We Learned

Under the standard settings, adaptive behaviour did not change the final outcome much.

Important interpretation:

```text
The ToM and learning modules were working, but their effect was smaller than the harmful-content pressure.
```

This helped us understand that the model needed calibration, not just more features.

## 8. Targeted Calming Test

### Purpose

Because the first results were escalation-heavy, we tested whether the model could produce calming outcomes under lower-harm conditions.

### Key Results

| Case | Mean final bullying level | Got worse | Calmed down | Unresolved |
| --- | ---: | ---: | ---: | ---: |
| 40% defenders low harm | 81.6 | 98% | 0% | 2% |
| 60% defenders low harm | 60.1 | 34% | 20% | 46% |
| 80% defenders low harm | 29.5 | 0% | 74% | 26% |
| 90% defenders low harm | 21.2 | 0% | 92% | 8% |
| 80% defenders toxicity 0 | 18.4 | 0% | 100% | 0% |
| 80% defenders toxicity 10 | 25.3 | 0% | 82% | 18% |
| 80% defenders toxicity 25 | 64.7 | 54% | 22% | 24% |
| 80% defenders toxicity 50 | 83.3 | 100% | 0% | 0% |
| 80% defenders toxicity 75 | 84.4 | 100% | 0% | 0% |

### What We Learned

The model can produce calming outcomes.

Defenders are most effective when:

- defenders strongly dominate
- toxicity is low
- profanity is low
- identity attack is low
- starting bullying level is not too close to escalation

Toxicity was one of the strongest drivers.

Clear finding:

```text
With 80% defenders, toxicity 0 calmed down in 100% of runs, but toxicity 50 escalated in 100% of runs.
```

## 9. First Scientific Conclusion From Testing

After the first sensitivity analysis, the main conclusion was:

```text
Cyberbullying escalation in the simulation is shaped by both bystander behaviour and environmental harm pressure.
```

More specifically:

- defenders help reduce or delay harm
- silent bystanders do not directly attack, but silence can allow harm to continue
- high toxicity and engagement can overwhelm defenders
- the original dashboard settings were too escalation-heavy

This led to the next phase: calibration.

## 10. Calibration Experiments

### Purpose

The calibration experiments were designed to find low, medium, tipping-point, and high escalation scenarios.

The goal was to avoid only showing escalation-heavy results.

### Broad Calibration Grid

The broad calibration grid tested:

```text
6 harm profiles x 5 bystander profiles x 30 repeated runs
```

Total:

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

### Bystander Profiles

| Bystander profile | Bully supporters | Victim supporters | Silent bystanders | Other |
| --- | ---: | ---: | ---: | ---: |
| Protective majority | 5% | 70% | 20% | 5% |
| Defender leaning | 15% | 55% | 25% | 5% |
| Balanced discussion | 25% | 35% | 30% | 10% |
| Silent majority | 15% | 20% | 55% | 10% |
| Bully-support leaning | 45% | 20% | 25% | 10% |

### Broad Calibration Finding

The broad grid found clear low and high regimes, but the low/medium boundary needed a finer search.

Very low harm generally calmed quickly.

High harm generally escalated quickly.

Medium cases produced mixed or unresolved outcomes.

## 11. Fine Calibration Search

### Purpose

The fine calibration search looked closely around the borderline between calming and escalation.

It tested:

```text
588 parameter combinations x 30 repeated runs
```

Total:

```text
17,640 Mesa simulation runs
```

It varied:

- starting bullying level from 22 to 42
- toxicity from 0 to 30
- defenders from 50% to 80%
- instigators from 5% to 20%
- neutral bystanders as the remaining percentage

## 12. Recommended Calibrated Scenarios

These scenarios are now useful for presentation and future dashboard presets.

### Low Escalation Scenario

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

Results:

| Metric | Value |
| --- | ---: |
| mean final bullying level | 34.6 |
| mean change | -3.4 |
| got worse | 0% |
| calmed down | 40% |
| stayed unresolved | 60% |

Interpretation:

```text
The situation stays controlled, but it may remain unresolved rather than fully calm.
```

### Medium Escalation Scenario

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

Results:

| Metric | Value |
| --- | ---: |
| mean final bullying level | 54.6 |
| mean change | +12.6 |
| got worse | 47% |
| calmed down | 3% |
| stayed unresolved | 50% |

Interpretation:

```text
Defenders help, but the situation remains risky and often unresolved.
```

### Tipping-Point Scenario

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

Results:

| Metric | Value |
| --- | ---: |
| mean final bullying level | 48.8 |
| mean change | +10.8 |
| got worse | 33% |
| calmed down | 37% |
| stayed unresolved | 30% |

Interpretation:

```text
This is a fragile scenario where the outcome can go either way.
```

### High Escalation Scenario

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

Results:

| Metric | Value |
| --- | ---: |
| mean final bullying level | 85.0 |
| mean change | +30.0 |
| got worse | 100% |
| calmed down | 0% |
| stayed unresolved | 0% |

Interpretation:

```text
High toxicity and engagement pressure overwhelm the protective effect of defenders.
```

## 13. What Calibration Taught Us

Calibration showed that the model can represent different behavioural regimes.

The earlier escalation-heavy result was not the only possible behaviour of the model. It happened because the original settings were located in a high-pressure part of the parameter space.

After calibration, the model can show:

- low escalation
- unresolved medium-risk situations
- tipping-point uncertainty
- high escalation

This gives the project a stronger scientific story.

## 14. Reward Design Experiments

### Why Reward Design Was Tested

During continual learning tests, we noticed something important:

```text
Agents learn whatever the reward system defines as success.
```

This became one of the strongest findings of the project.

Reward design matters because it decides what the model treats as good behaviour.

### Reward Systems Compared

Three reward systems were tested.

| Reward system | Meaning |
| --- | --- |
| Role-based reward | agents learn according to their role; instigators are rewarded when escalation succeeds |
| Victim-safety reward | all agents are rewarded when harm decreases and penalised when bullying increases |
| Mixed ethical reward | agents keep role tendencies, but everyone is discouraged from severe escalation |

### Scenarios Used

Reward designs were tested in:

- low-risk defended scenario
- medium tipping-point scenario
- high-risk pressure scenario

Each condition ran:

```text
40 repeated simulations
```

Learning was carried across repeated runs.

## 15. Reward Design Results

### Medium Tipping-Point Scenario

This scenario showed the strongest effect.

| Reward design | Mean final bullying level | Got worse | Calmed down |
| --- | ---: | ---: | ---: |
| Role-based reward | 81.2 | 90% | 0% |
| Victim-safety reward | 18.6 | 0% | 100% |
| Mixed ethical reward | 18.5 | 0% | 98% |

### What This Means

The same scenario changed dramatically depending on the reward system.

Plain-English interpretation:

```text
The model does not simply learn automatically. It learns according to the values built into the reward function.
```

## 16. What “Medium Tipping Point” Means

A medium tipping-point scenario is a situation that is not clearly safe and not clearly doomed.

It is a borderline case.

In simple terms:

```text
The bullying is serious enough to become dangerous, but not so severe that escalation is guaranteed.
```

This kind of scenario is scientifically useful because small changes in bystander behaviour, social influence, or reward design can push the outcome in different directions.

Low-risk scenarios usually calm down anyway.

High-risk scenarios usually escalate anyway.

Tipping-point scenarios reveal how learning and social influence matter.

## 17. Why Mixed Ethical Reward Calmed the Tipping-Point Scenario

Mixed ethical reward worked because it combined three effects:

1. Agents kept some role identity.
2. Escalation was penalised for everyone.
3. Victim-support behaviour received a positive push.

This created a feedback loop:

```text
Mixed ethical reward encourages defending
→ more agents support the victim
→ bullying level drops
→ defending gets rewarded again
→ defending becomes more likely
→ the conversation calms down
```

Important limitation:

This does not mean human conversations will always calm down if people are taught to defend.

The correct interpretation is:

```text
In this simulation, when the situation is near a tipping point, victim-safety rewards make calming much more likely.
```

## 18. Rule-Based Simulation vs Learning Simulation

We clarified an important modelling point:

| Simulation type | Needs rewards? | Meaning |
| --- | --- | --- |
| Rule-based simulation | No | agents follow fixed rules |
| Learning simulation | Yes | agents need feedback to change behaviour |
| Continual learning simulation | Yes | agents carry feedback across repeated runs |

Rewards are not required for every simulation.

However, rewards are essential if the simulation includes reinforcement learning or continual learning.

Plain-English explanation:

```text
Without rewards, agents can still act, but they do not learn from what happened.
```

## 19. Overall Understanding So Far

The project has developed from a dashboard into a more defensible Mesa-based behavioural simulation.

The main understanding so far is:

```text
Cyberbullying escalation in the simulation emerges from the interaction between harmful-content pressure, bystander role mix, social influence, and reward-based learning.
```

Key findings:

- Bystander roles matter.
- Defenders can reduce or delay harm.
- Silence can indirectly allow harm to continue.
- Toxicity is a strong driver of escalation.
- Engagement pressure makes escalation faster.
- Calibration is necessary because default settings can bias the model.
- Reward design strongly affects what agents learn.
- Safety-based and mixed ethical rewards can shift borderline scenarios toward calmer outcomes.
- Severe high-risk environments can still escalate even with better reward design.

## 20. Current Scientific Argument

The strongest project argument is now:

```text
The simulation shows that online bullying outcomes are not shaped by one factor alone. They emerge from the combination of harmful content, audience composition, social pressure, and learning incentives.
```

This is important because it supports the project as an agent-based model rather than a classifier.

The simulation is useful because it lets us test:

- what happens if defenders increase
- what happens if silence dominates
- what happens when toxicity increases
- what happens when engagement pressure increases
- what happens when agents are rewarded for different behaviours

## 21. How This Connects to the Base Paper

The base paper uses Theory of Mind, Reinforcement Learning, Continual Learning, and Mesa for bullying intervention.

Our project adapts that direction to cyber-bystander behaviour.

The testing so far supports the same general idea:

- social context matters
- agents need adaptive learning to change behaviour
- memory across runs can change future behaviour
- reward design is central to responsible learning

However, our project remains simpler and more interpretable.

We do not claim to reproduce the full base paper.

We use simplified ToM, RL, and CL to make the simulation explainable for a university applied project.

## 22. Important Limitations

The tests are valid for the current simulation model, not for all real online bullying situations.

Important limitations:

- CYBY23 informs role structure and harmful-content context, but does not directly contain ToM/RL/CL labels.
- The simulation does not predict exact human behaviour.
- The reward systems are modelling choices, not real psychological measurements.
- The model has no full social network graph yet.
- The dashboard is a prototype, not a moderation tool.
- Results depend on calibration and parameter settings.

The honest interpretation is:

```text
The model is useful for exploring assumptions, not for making real-world decisions about people.
```

## 23. Files Created From Testing

### Sensitivity Analysis

- `sensitivity_outputs/SENSITIVITY_ANALYSIS_REPORT.md`
- `sensitivity_outputs/SENSITIVITY_ANALYSIS_REPORT.pdf`
- `sensitivity_outputs/SENSITIVITY_ANALYSIS_METHODS.md`
- `sensitivity_outputs/sensitivity_runs.csv`
- `sensitivity_outputs/sensitivity_summary.csv`
- `sensitivity_outputs/targeted_calming_summary.csv`
- `sensitivity_outputs/average_trajectories_over_time.csv`
- `sensitivity_outputs/continual_learning_runs.csv`

### Calibration Experiments

- `sensitivity_outputs/calibration_experiments/CALIBRATED_SCENARIO_REPORT.md`
- `sensitivity_outputs/calibration_experiments/CALIBRATED_SCENARIO_REPORT.pdf`
- `sensitivity_outputs/calibration_experiments/calibration_run_level_results.csv`
- `sensitivity_outputs/calibration_experiments/calibration_summary.csv`
- `sensitivity_outputs/calibration_experiments/calibration_trajectories.csv`
- `sensitivity_outputs/calibration_experiments/fine_calibration_search.csv`
- `sensitivity_outputs/calibration_experiments/recommended_calibrations.csv`

### Reward Design Experiments

- `reward_design_experiments.py`
- `sensitivity_outputs/reward_design_experiments/REWARD_DESIGN_EXPERIMENT_REPORT.md`
- `sensitivity_outputs/reward_design_experiments/reward_design_summary.csv`
- `sensitivity_outputs/reward_design_experiments/reward_design_run_level_results.csv`

## 24. Recommended Next Steps

Recommended next steps for the project:

1. Add reward design as a dashboard option:

```text
Learning goal:
- Role-based learning
- Victim-safety learning
- Mixed ethical learning
```

2. Add calibrated dashboard presets:

```text
Low escalation
Medium unresolved
Tipping point
High escalation
```

3. Add a short explanation panel that says:

```text
Reward design controls what agents learn to value.
```

4. Recalibrate the default dashboard so it does not always start in a high-escalation region.

5. Keep the dashboard plain-English and avoid prediction-language.

6. Present results as exploratory simulation findings, not real-world causal proof.

## 25. Final Team Summary

Since the proposal stage, the project has progressed from having a working Mesa simulation to having a clearer scientific testing story.

The most important progress is:

- We diagnosed that the original settings were escalation-biased.
- We calibrated the model to show low, medium, tipping-point, and high outcomes.
- We discovered that reward design strongly changes agent learning.
- We created separate experiment outputs and reports without breaking the dashboard.

The most important scientific takeaway is:

```text
In a cyber-bystander agent-based simulation, outcomes depend not only on who is present, but also on what the environment rewards agents for doing.
```

This gives the project a strong applied AI and responsible modelling angle.

