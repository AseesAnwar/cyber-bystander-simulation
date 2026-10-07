# Detailed Project Report: Day 1 to Current State

## 1. Report Purpose

This report explains the full development journey of the cyber-bystander simulation project from the very first prompt to the current state.

It is written for instructors, teammates, and project stakeholders who want to understand:

- what the project started as
- how the goals changed over time
- how the codebase evolved
- how Mesa, CYBY23, Theory of Mind, Reinforcement Learning, and Continual Learning were used
- what testing and calibration were completed
- what the final scientific findings are so far

This report is not just a code summary. It is a development and research narrative.

## 2. Day 1: Initial Project Goal

The project began with a request to build a clean, runnable Python project using Mesa for an academic prototype on modelling cyber-bystander behaviour in online bullying discussions.

The project was grounded in the **CYBY23 cyber-bystander dataset**.

The first requested goals were:

- load and preprocess the CYBY23 Excel dataset
- identify source posts and bystander replies
- normalize cyber-bystander role labels
- build a Mesa simulation where agents represent users in online conversations
- model whether bystanders reinforce, defend, stay neutral, or act unrelated
- keep the first version simple, interpretable, and academically defensible

The first concept was therefore:

```text
Use real cyber-bystander role labels from CYBY23 to build a Mesa-based simulation of harmful online conversations.
```

At this stage, the project was still close to a structured prototype rather than a full interactive behavioural dashboard.

## 3. Dataset Foundations

From the beginning, the CYBY23 dataset was central to the project.

The intended use of the dataset was:

- source of role structure
- source of harmful-content context
- source of labels for reinforce, defend, neutral, and unrelated behaviour

The project did **not** ultimately use CYBY23 as a prediction target in a supervised machine learning sense.

Instead, the dataset was used to ground the simulation in real labelled cyber-bystander behaviour while keeping the project focused on behavioural dynamics.

The bystander role mapping used throughout the project became:

- `reinforce` → `instigator`
- `defend` → `defender`
- `neutral` → `neutral`
- `unrelated` → `other`

This dataset grounding remained an important part of how the project was explained to instructors.

## 4. Early Technical Structure

The earliest requested deliverables included:

- preprocessing script
- Mesa agent classes
- Mesa model class
- runnable simulation script
- plots using matplotlib
- demo script or notebook
- README

At this stage, the project was mostly code-centric and academically structured.

The main technical direction was:

```text
Start with a transparent rule-based simulation first, then extend later if needed.
```

This was an important early design choice because it kept the prototype explainable.

## 5. Transition to Interactivity

Soon after the initial build request, the project direction shifted because there was a request to make everything interactive and available through a web browser.

This introduced a new project goal:

```text
The simulation should not just exist as backend code. It should be visible and interactive in a browser.
```

This led to the use of **Streamlit** for the front-end dashboard.

The dashboard was first treated as a web interface for showing the simulation, but over time it became a major part of the project itself.

Temporary browser links were later created using public tunnel tools so the dashboard could be shared in meetings.

## 6. Plain-English Dashboard Requirement

After the dashboard appeared, the next major development direction was usability.

It was recognised that the interface felt too technical and too much like a data science or prediction dashboard.

The dashboard was then redesigned in plain English.

Examples of terminology changes:

- Thread → Conversation
- Source post → Original post
- Bystander → People replying
- Observed → Real data
- Simulated → Model prediction
- Escalation score → How much the conversation becomes more hostile
- Defence score → How much people push back against the harmful post
- Random seed → Repeat setting

This was a major design milestone because it changed the project from “technical prototype” to something that could be shown to mixed audiences, including non-technical instructors.

The dashboard began to tell a story instead of just showing numbers.

## 7. Shift Away From Prediction Thinking

One of the most important project direction changes happened when it became clear that the system should **not** feel like a prediction model.

The project was explicitly reframed as:

```text
Behavioural simulation + interactive dashboard
```

and not:

```text
prediction analytics dashboard
```

This changed the visual, conceptual, and technical priorities.

The project stopped emphasising:

- prediction accuracy
- training loss
- confusion matrices
- prediction probabilities

and started emphasising:

- bystander composition
- aggression over time
- escalation vs de-escalation
- social interaction
- what-if scenario exploration

This was one of the most important conceptual improvements in the project.

## 8. Emergence of the Main Behavioural Simulation Concept

The core simulation environment eventually stabilised around:

- 1 abuser or harmful situation
- 1 victim context
- multiple bystanders

Main bystander roles:

- **Instigator:** supports the bully and increases pressure
- **Defender:** supports the victim and reduces pressure
- **Neutral:** stays silent and may allow bullying to continue
- **Other:** unrelated or low-impact participant

The model tracks a bullying level over time and classifies the conversation outcome as:

- Got worse
- Calmed down
- Stayed unresolved

This made the simulation much easier to explain and defend academically.

## 9. Introduction of Theory of Mind, Reinforcement Learning, and Continual Learning

The next major development stage involved adding learning and social reasoning.

The request was not to build deep learning or neural networks. Instead, the requirement was:

- keep everything modular
- keep everything interpretable
- make the model explainable in a university presentation

### Theory of Mind

Theory of Mind was simplified into social-context reasoning.

Agents estimate:

- perceived aggression
- perceived vulnerability
- perceived behaviour trend in the thread

In practice, this became a mechanism where agents look at:

- how many others seem to support the bully
- how many others seem to defend
- how many others seem to stay silent

This influenced later decisions.

### Reinforcement Learning

Reinforcement learning was simplified into reward-based adaptation.

Agents receive feedback after actions, and their preferences are adjusted using lightweight numeric updates rather than complex Q-networks.

### Continual Learning

Continual learning was implemented as persistent memory across repeated runs.

Agents can carry some learned tendencies forward instead of always restarting from zero.

Together, these features made the project more dynamic while still staying explainable.

## 10. Use of the Base Paper

At a later stage, the assigned base paper was explicitly added into the project understanding and proposal:

**Theory of mind and continual reinforcement learning for bullying intervention**

The project used this paper as an academic foundation.

What the paper contributed conceptually:

- bullying should be modelled as a multi-agent social environment
- Theory of Mind can help agents reason about others
- Reinforcement Learning can help agents adapt from outcomes
- Continual Learning can help agents carry experience across scenarios
- Mesa is an appropriate framework for this style of simulation

Important clarification:

The project did **not** copy the paper line-by-line or implement its full Algorithm 1 directly.

Instead, the paper was used as **conceptual inspiration**.

The correct interpretation of the project became:

```text
We adapted the paper’s ideas into a simpler Mesa-based cyber-bystander simulation that is easier to explain and defend in a university setting.
```

## 11. Mesa Backend Consolidation

Eventually, the project moved to a proper Mesa backend structure.

Main files:

- `mesa_model.py`
- `mesa_agents.py`
- `mesa_learning.py`
- `mesa_bridge.py`

This allowed the Streamlit dashboard to work as a front-end while the actual simulation logic remained in Mesa.

This separation was important because it allowed the project to be explained honestly:

```text
The dashboard is the interface, but the actual simulation engine is Mesa.
```

This also made later testing and experiments easier, because the model could be run repeatedly through scripts.

## 12. Dashboard Evolution Into a Mesa-Style Environment

The dashboard itself went through several changes:

- plain-English redesign
- behavioural simulation framing
- agent-based visual layout
- side-by-side control panel and results
- support for role composition changes
- support for social influence and learning toggles

Later, the dashboard also adopted:

- what-if scenario exploration
- clearer outcome cards
- explanation panels
- teacher/instructor-friendly labels

This made the dashboard more than just a visual layer; it became a central communication tool for the project.

## 13. Technical Debugging and UI Logic Fixes

There were multiple rounds of debugging and interface fixes.

Some of the important issues addressed were:

- blank or expired browser links
- Streamlit state errors
- broken bystander count logic
- confusion between counts and percentages
- repeated need to keep total bystanders equal to the sum of role counts
- confusing “repeat setting” terminology
- role count widgets causing session-state conflicts

One major clarification that improved the UI logic was:

```text
If total bystanders is 20, then all role counts together must equal 20.
```

That sounds simple, but it was crucial for making the dashboard understandable.

## 14. First Large Scientific Testing Phase: Sensitivity Analysis

Once the Mesa dashboard and backend were stable enough, a major scientific testing phase began.

This sensitivity analysis tested how the simulation responds when key parameters change.

Main categories tested:

- bystander role mix
- harmful-content severity
- engagement pressure
- ToM/social influence
- learning and memory settings

The first major result was:

```text
The default simulation settings were strongly biased toward escalation.
```

This happened because the harmful-content pressure was high enough that most scenarios got worse, even when defenders were present.

This finding was important because it revealed a calibration issue in the model.

It also showed that the simulation was behaving consistently enough to be diagnosed scientifically.

## 15. Role Mix Findings

The role mix sweep tested what happens when defenders gradually replace instigators.

Main observation:

- more defenders delayed escalation
- but defenders did not fully prevent escalation under the original high-pressure settings

This led to a more careful interpretation:

```text
Role mix matters, but harmful-content severity can still dominate the outcome.
```

This was a useful finding because it kept the project realistic and avoided oversimplified claims.

## 16. Targeted Calming Tests

Because the early results were too escalation-heavy, targeted calming tests were created.

These tests lowered:

- toxicity
- profanity
- identity attack
- starting aggression

and increased defender dominance.

These experiments showed that the model could produce calming outcomes under certain conditions.

Important findings included:

- with strong defenders and very low toxicity, conversations could calm reliably
- once toxicity reached higher levels, escalation returned even with many defenders

This showed that the model could represent more than one type of behaviour, but only after calibration.

## 17. Calibration Phase

After the initial sensitivity analysis, a new project direction emerged:

```text
Calibrate the simulation so it can produce low, medium, tipping-point, and high escalation regimes.
```

This led to broad and fine calibration experiments.

### Broad Calibration

The broad calibration grid tested multiple harm profiles against multiple bystander profiles.

This revealed:

- very low harm regimes
- high escalation regimes
- intermediate cases needing closer study

### Fine Calibration

The fine calibration search focused on the region between calming and escalation.

This identified:

- low escalation scenarios
- medium-risk unresolved scenarios
- tipping-point scenarios

This was one of the most important scientific improvements to the project because it transformed the simulation from “mostly escalating” to “capable of representing different behavioural regimes.”

## 18. Tipping-Point Scenarios

One particularly important concept that emerged was the **medium tipping-point scenario**.

This refers to a case that is:

- not clearly safe
- not clearly doomed
- sensitive to bystander behaviour, social influence, and reward design

This scenario became important because it showed where the model was most informative.

Low-risk scenarios often calm down regardless.

High-risk scenarios often escalate regardless.

Tipping-point scenarios show whether learning rules or social dynamics can actually change outcomes.

## 19. Continual Learning Observation

When repeated runs with memory were examined, an important finding emerged:

```text
Agents learn whatever the environment rewards as success.
```

This led directly to the next experimental stage.

## 20. Reward-Design Experiments

The project then explored a very important scientific question:

```text
How does reward design affect what agents learn?
```

Three reward systems were compared:

1. **Role-based reward**
   - instigators rewarded when escalation succeeds
   - defenders rewarded when bullying decreases

2. **Victim-safety reward**
   - all agents rewarded when harm decreases
   - all agents penalised when harm increases

3. **Mixed ethical reward**
   - role identity kept
   - severe escalation discouraged for everyone

### Main finding

In the medium tipping-point scenario, reward design changed the outcome dramatically.

Role-based reward led mostly to escalation.

Victim-safety reward led to calming outcomes.

Mixed ethical reward also led to calming outcomes.

This became one of the strongest findings of the whole project.

The key interpretation was:

```text
The model does not simply learn. It learns according to the values built into the reward system.
```

This gave the project a responsible-AI angle and significantly strengthened its academic value.

## 21. Clarification on Rewards

It was later clarified that rewards are essential only if agents are expected to learn.

This led to a clean explanation:

| Simulation type | Needs rewards? |
| --- | --- |
| Rule-based simulation | No |
| Learning simulation | Yes |
| Continual learning simulation | Yes |

This distinction helped explain the project more clearly to non-technical audiences.

## 22. Documentation and Export Phase

As the project matured, a major documentation phase took place.

Several reports and guides were created:

- project proposal
- Mesa build guide
- Codex + Mesa guide
- testing and progress log
- sensitivity analysis report
- calibration report
- reward design report
- methods document
- prompt transparency log

Files were exported in:

- Markdown
- PDF
- Word
- Excel
- CSV
- ZIP packages for teammates

This turned the project into something much more shareable and presentation-ready.

## 23. Team Sharing and Handoff

The project also generated:

- code packages for teammates
- handoff instructions for the dashboard
- Excel workbooks for test results
- standalone Mesa runner packages

This was especially important because the live tunnel links were temporary and unreliable.

The project therefore shifted from:

```text
“here is a temporary live link”
```

to:

```text
“here is the actual dashboard code and experiment package your teammates can run locally”
```

## 24. Manual Test Replication

Later, manually specified spreadsheet-style tests were also converted into Mesa scripts.

This included:

- transcribing manual scenarios
- generating repeated Mesa runs
- exporting Excel workbooks
- making teammate-style script structures

This was useful because it linked the simulation more directly to manual testing workflows that teammates were already using.

## 25. Current Project Framing

The project can now be described as:

```text
A Mesa-based behavioural simulation dashboard for exploring cyber-bystander dynamics in online bullying discussions, grounded in CYBY23 and extended with simplified Theory of Mind, Reinforcement Learning, and Continual Learning.
```

It should **not** be described as:

- a prediction product
- a real-world moderation tool
- a classifier
- a human behaviour certainty model

It **should** be described as:

- an exploratory simulation
- an applied university project
- a behavioural modelling prototype
- a tool for understanding how bystanders affect escalation and calming

## 26. Main Scientific Findings So Far

The strongest findings so far are:

### 1. Default settings matter a lot

The original default settings were too strongly biased toward escalation.

### 2. Bystander mix matters

Defenders reduce or delay harm, while silence and instigator support increase risk.

### 3. Harmful-content severity matters

Toxicity, identity attack, profanity, and engagement can overpower defenders.

### 4. Calibration is essential

Without calibration, the model is not balanced enough to show realistic behavioural variety.

### 5. Reward design is one of the most important modelling decisions

Agents learn what the reward system values.

This means reward design changes the direction of learned behaviour and therefore changes the simulation outcome.

### 6. Tipping-point scenarios are especially informative

These are the scenarios where social influence and reward design matter most.

## 27. Main Limitations

Important limitations remain:

- CYBY23 informs the structure but is not replayed thread-by-thread
- the simulation does not predict exact real-world human behaviour
- ToM, RL, and CL are simplified
- the model is intentionally interpretable rather than highly complex
- no full social network graph is implemented yet
- dashboard sharing via live links remains temporary unless hosted properly

These limitations are not weaknesses to hide. They are part of the honest framing of the project.

## 28. Current Deliverables

The project currently includes:

- Mesa backend files
- Streamlit dashboard
- preprocessing pipeline
- experiment scripts
- sensitivity analysis outputs
- calibration outputs
- reward-design outputs
- PDF/Word/Markdown reports
- Excel workbooks
- teammate handoff code packages

This means the project has progressed far beyond a concept draft. It now has a working codebase, research outputs, and a documented testing history.

## 29. Overall Development Summary

From day 1 until now, the project progressed through these main phases:

1. initial Mesa + CYBY23 simulation request
2. move to interactive browser dashboard
3. plain-English redesign
4. behavioural simulation reframing
5. ToM/RL/CL extension
6. proper Mesa backend structure
7. dashboard debugging and usability fixes
8. sensitivity testing
9. calibration testing
10. reward-design experiments
11. documentation, reports, exports, and team handoff

This is a significant development arc.

## 30. Final Project Interpretation

The clearest overall conclusion is:

```text
The simulation shows that cyberbullying outcomes are not shaped by one factor alone. They emerge from the interaction between harmful-content severity, bystander role composition, social influence, and learning incentives.
```

The strongest current academic contribution of the project is not that it “predicts” cyberbullying.

It is that it provides a **transparent, Mesa-based behavioural environment** for exploring how:

- defenders can reduce harm
- silence can permit escalation
- high toxicity can overwhelm intervention
- reward design changes what agents learn

This makes the project suitable for a university applied research context and gives it a strong base for future extension.

