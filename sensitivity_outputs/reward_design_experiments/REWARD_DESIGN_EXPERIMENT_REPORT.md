# Reward Design Experiment Report

## Purpose

This experiment explores a key scientific finding from the Mesa cyber-bystander simulation:

**Agents learn according to the reward system we give them.**

This matters because in a social simulation, the reward function is not just a technical detail. It represents what the model treats as success.

If the reward system rewards escalation for some agents, those agents may learn harmful behaviour. If the reward system rewards victim safety, agents may learn more protective behaviour.

## Research Question

How does reward design affect what cyber-bystander agents learn over repeated bullying simulations?

## Method

The experiment used the same Mesa backend as the dashboard.

Main files used:

- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`
- `mesa_bridge.py`
- `reward_design_experiments.py`

The dashboard and core model were not permanently changed. The experiment temporarily swapped the reward function during the run.

Each reward design was tested in three scenario types:

1. low-risk defended scenario
2. medium tipping-point scenario
3. high-risk pressure scenario

Each condition was run:

```text
40 repeated simulations
```

Learning was carried across repeated runs so agents could adapt over time.

## Reward Designs Tested

### 1. Role-Based Reward

This is closest to the original reward logic.

| Agent role | What it is rewarded for |
| --- | --- |
| Instigator | bullying increases |
| Defender | bullying decreases |
| Neutral | silence is penalised when bullying increases |
| Other | small reward when the situation stays stable |

Plain-English meaning:

**Agents learn according to their role. Instigators can learn to become better instigators.**

### 2. Victim-Safety Reward

All agents are rewarded when bullying decreases and penalised when bullying increases.

Plain-English meaning:

**The whole system is taught that reducing harm is the goal.**

### 3. Mixed Ethical Reward

Agents keep some role identity, but severe escalation is penalised for everyone.

Plain-English meaning:

**Agents still have different personalities, but the model discourages harmful escalation.**

## Scenario Settings

### Low-Risk Defended Scenario

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

### Medium Tipping-Point Scenario

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

### High-Risk Pressure Scenario

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

## Results Summary

| Scenario | Reward design | Mean final level | Got worse | Calmed down | Bully-support tendency change | Defender tendency change |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Low-risk defended | Role-based | 18.6 | 0% | 98% | 0.05 to -62.39 | 0.97 to 1444.38 |
| Low-risk defended | Victim-safety | 18.2 | 0% | 100% | -0.09 to -27.92 | 1.60 to 2246.89 |
| Low-risk defended | Mixed ethical | 18.5 | 0% | 100% | -0.13 to -30.20 | 1.40 to 2125.41 |
| Medium tipping-point | Role-based | 81.2 | 90% | 0% | -0.09 to -137.77 | -0.31 to -610.30 |
| Medium tipping-point | Victim-safety | 18.6 | 0% | 100% | 0.01 to 1.13 | 1.71 to 2753.35 |
| Medium tipping-point | Mixed ethical | 18.5 | 0% | 98% | -0.04 to -16.55 | 1.58 to 2710.10 |
| High-risk pressure | Role-based | 85.9 | 100% | 0% | 0.18 to 337.77 | -0.06 to -90.61 |
| High-risk pressure | Victim-safety | 83.8 | 100% | 0% | -0.34 to -511.81 | -0.17 to -267.83 |
| High-risk pressure | Mixed ethical | 83.4 | 100% | 0% | -0.24 to -368.70 | -0.18 to -245.52 |

## Main Findings

## Finding 1: Reward design strongly changes what agents learn

The medium tipping-point scenario showed the clearest difference.

Under role-based reward:

```text
Got worse: 90%
Calmed down: 0%
Mean final bullying level: 81.2
```

Under victim-safety reward:

```text
Got worse: 0%
Calmed down: 100%
Mean final bullying level: 18.6
```

Under mixed ethical reward:

```text
Got worse: 0%
Calmed down: 98%
Mean final bullying level: 18.5
```

Plain-English interpretation:

**The same scenario can become harmful or safe depending on what the agents are rewarded for learning.**

## Finding 2: Role-based learning can reinforce harmful dynamics

In the high-risk scenario, role-based reward increased bully-support tendency:

```text
0.18 to 337.77
```

This happened because instigator agents were rewarded when bullying increased.

Plain-English interpretation:

**If the model tells harmful agents that escalation is success, they learn to keep escalating.**

## Finding 3: Safety-based rewards reduce harmful learning, but cannot always overcome severe environments

In the high-risk scenario, victim-safety reward strongly reduced bully-support tendency:

```text
-0.34 to -511.81
```

However, the scenario still escalated in 100% of runs.

Plain-English interpretation:

**Better rewards can teach agents safer behaviour, but very severe harmful-content pressure can still overwhelm the system.**

This is important because it shows that reward design matters, but environment severity also matters.

## Finding 4: The tipping-point scenario is the best place to study reward design

Low-risk scenarios usually calm down regardless of reward design.

High-risk scenarios usually escalate regardless of reward design.

Medium tipping-point scenarios show the biggest difference.

Plain-English interpretation:

**Reward design matters most when the situation could go either way.**

## Scientific Conclusion

The experiment shows that reward design is one of the most important modelling choices in the simulation.

The model does not simply “learn.” It learns according to the values built into the reward function.

For a cyberbullying intervention project, this means the reward system should be designed around victim safety and harm reduction, not only role-based success.

The strongest conclusion is:

```text
In agent-based cyber-bystander simulations, reward design changes the direction of agent learning. If rewards are role-based, harmful agents may learn harmful behaviour. If rewards are safety-based, agents are more likely to learn protective behaviour, especially in medium-risk situations.
```

## How This Helps the Project

This finding strengthens the academic value of the project because it links the simulation to responsible AI.

It shows that:

- learning systems are not neutral
- reward definitions shape behaviour
- social simulations need ethical calibration
- a cyberbullying intervention model should reward harm reduction

This can be connected to the base Theory of Mind, Reinforcement Learning, and Continual Learning paper. That paper argues that bullying intervention agents need adaptive learning. This experiment adds an important project-specific point:

**Adaptive learning is only useful if the reward system teaches the right social goal.**

## Recommended Next Step

The dashboard should later include a plain-English reward setting:

```text
Learning goal
```

Options:

- role-based learning
- victim-safety learning
- mixed ethical learning

This would allow instructors and teammates to see how the same scenario changes when the model is taught different goals.

## Output Files

The experiment produced:

- `reward_design_run_level_results.csv`
- `reward_design_summary.csv`
- `REWARD_DESIGN_EXPERIMENT_REPORT.md`

