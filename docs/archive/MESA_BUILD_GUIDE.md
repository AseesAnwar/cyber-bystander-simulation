# Building the Cyber-Bystander Simulation in Mesa

This document is a technical build guide for our team. It explains how to recreate the cyber-bystander behavioural simulation as a real Mesa-based agent-based model in Python.

The aim of this guide is not only to show what files to create, but also to explain why each part exists, what it should do, and how all parts fit together.

This project is an interactive behavioural simulation, not a prediction product. The purpose is to help users explore how different cyber-bystander roles may influence whether an online bullying conversation gets worse, starts calming down, or stays unresolved.

## 1. Project Purpose

Our project simulates one online bullying conversation at a time.

Each simulated conversation contains:
- 1 abuser
- 1 victim
- multiple bystanders

Each bystander belongs to one of four roles:
- `instigator`: supports the bully and tends to increase aggression
- `defender`: supports the victim and tends to reduce aggression
- `neutral`: stays silent and may indirectly allow aggression to continue
- `other`: has little or no meaningful effect on the conflict

The project uses the CYBY23 dataset as context and inspiration. We use it to inform:
- what types of bystander roles appear in real online conversations
- what kinds of harmful post features are present
- reasonable defaults for role composition and aggression-related settings

We do not use the dataset to build a classifier or a predictive system. This is a behavioural simulation for exploration and explanation.

## 2. Mesa Section: Why We Are Using Mesa

Mesa is the core backend framework for this project because it provides a clean way to model:
- individual agents
- model-level environment state
- step-by-step simulation
- agent scheduling
- data collection across runs

Mesa helps us move from a simple custom simulation script to a proper agent-based modelling structure.

Mesa is useful here because:
- each bystander can be represented as an agent
- agents can make decisions at each simulation step
- the model can keep track of the overall bullying environment
- the simulation can later be extended with richer interactions or network structure

We use current Mesa patterns such as:
- `agents.shuffle_do("step")` for agent activation
- `DataCollector` for model-level and agent-level outputs

Official references:
- [Mesa getting started](https://mesa.readthedocs.io/latest/getting_started.html)
- [Mesa AgentSet tutorial](https://mesa.readthedocs.io/stable/tutorials/3_agentset.html)
- [Mesa DataCollector documentation](https://mesa.readthedocs.io/en/stable/apis/datacollection.html)

## 3. Codex + Mesa Section: How We Use Codex Alongside Mesa

Codex and Mesa play different roles in this project.

### Mesa's role

Mesa is the actual simulation framework. It is what we use to:
- define agents
- define the model environment
- step the simulation forward
- collect outputs from each run

If the team removed Codex entirely, Mesa would still remain the real backend technology used to run the simulation.

### Codex's role

Codex is a development support tool. It helps the team build the project faster and more clearly, but it is not the simulation framework itself.

In this project, Codex can help with:
- generating starter code for Mesa files
- explaining Mesa concepts in simple language
- helping refactor code into cleaner modules
- suggesting debugging fixes
- writing documentation and comments
- helping translate technical behaviour into plain-English dashboard text

### How Codex and Mesa work together

The simplest way to explain this is:

- `Mesa` builds and runs the simulation
- `Codex` helps the team write, improve, and explain the Mesa project

This is useful for a university project because:
- Mesa gives us a real agent-based modelling framework
- Codex helps us prototype, document, and troubleshoot more efficiently
- the team can move faster while still keeping the actual model logic transparent

### What Codex should be used for

Good uses of Codex in this project:
- asking for help writing a Mesa model skeleton
- asking for help structuring files
- asking for help debugging errors
- asking for help improving explanations for instructors
- asking for help documenting ToM, RL, and continual learning logic

### What Codex should not replace

Codex should not replace:
- the team's own judgement
- the team's testing process
- critical evaluation of assumptions
- academic integrity and proper authorship responsibility

Every team member should still:
- understand what the code is doing
- review generated code carefully
- test the output before using it
- explain the simulation in their own words

### Team recommendation

Use Codex as a coding assistant and technical explainer, but always keep Mesa as the core framework and keep human review in the loop.

## 4. High-Level System Architecture

The project should be built in three layers:

1. Data layer  
   Loads and cleans CYBY23 data.

2. Mesa simulation layer  
   Runs the actual agent-based model.

3. Dashboard layer  
   Displays the simulation in plain English through Streamlit.

These layers should remain separate so the project stays modular and easy to maintain.

## 5. Recommended Project Structure

Use the following file structure:

```text
cyber-bystander-simulation/
├── preprocess_cyby23.py
├── mesa_learning.py
├── mesa_agents.py
├── mesa_model.py
├── mesa_bridge.py
├── abm_ui_helpers.py
├── abm_explanations.py
├── dashboard.py
├── requirements.txt
└── README.md
```

### What each file does

`preprocess_cyby23.py`  
Loads the Excel file, cleans the data, identifies source posts and replies, and builds simulation-ready thread summaries.

`mesa_learning.py`  
Contains learning logic such as:
- action list
- base role preferences
- reward update logic
- continual learning memory across runs

`mesa_agents.py`  
Defines all bystander agents and their step behaviour.

`mesa_model.py`  
Defines the main Mesa model, simulation environment, model state, step loop, and data collection.

`mesa_bridge.py`  
Converts Mesa outputs into simple dashboard-friendly result objects.

`abm_ui_helpers.py`  
Contains matplotlib visualisations and tables.

`abm_explanations.py`  
Contains plain-English end-of-run explanations and dataset connection text.

`dashboard.py`  
Streamlit dashboard that users interact with.

## 6. Development Environment Setup

### Step 1: Create the project folder

```bash
mkdir cyber-bystander-simulation
cd cyber-bystander-simulation
code .
```

### Step 2: Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -U mesa pandas numpy matplotlib streamlit openpyxl
```

Optional:

```bash
pip freeze > requirements.txt
```

### Why this matters

The virtual environment keeps project packages isolated. This makes the build reproducible across teammates' machines.

## 7. Build Order

Do not try to build the entire dashboard first. The easiest and safest order is:

1. `preprocess_cyby23.py`
2. `mesa_learning.py`
3. `mesa_agents.py`
4. `mesa_model.py`
5. small terminal-only Mesa test
6. `mesa_bridge.py`
7. `abm_explanations.py`
8. `abm_ui_helpers.py`
9. `dashboard.py`
10. final testing and cleanup

This order reduces confusion and makes debugging much easier.

## 8. Step-by-Step Build Plan

### Step A: Build the dataset preprocessing layer

Create `preprocess_cyby23.py`.

Its job is to:
- load the CYBY23 Excel file
- clean missing or malformed values
- identify source posts
- identify labelled bystander replies
- map raw role labels into a smaller simulation-ready set
- build per-thread summaries

### Input dataset

Expected file path:

```text
/mnt/data/CYBERBYSTANDER (CYBY23) dataset.xlsx
```

Useful columns:
- `user`
- `user_id`
- `tweet_id`
- `reply_id`
- `created_at`
- `text`
- `retweet_count`
- `favorite_count`
- `Insult`
- `Threat`
- `Identity_Attack`
- `Profanity`
- `Toxicity`
- `Severe_Toxicity`
- `polarity`
- `subjectivity`
- `sentiment`
- `Class label`
- `Bystander Roles Label`

### Suggested role mapping

Normalize the dataset roles to:

- `reinforce`
- `defend`
- `neutral`
- `unrelated`

Then map those for the simulation to:

- `reinforce` -> `instigator`
- `defend` -> `defender`
- `neutral` -> `neutral`
- `unrelated` -> `other`

### Suggested data structure

Create a thread summary object similar to:

```python
@dataclass
class ThreadRecord:
    thread_id: str
    source_text: str
    source_toxicity: float
    source_profanity: float
    source_identity_attack: float
    source_retweet_count: float
    source_favorite_count: float
    observed_role_distribution: dict[str, int]
```

### Why this preprocessing layer matters

Mesa should not read raw Excel files directly. The simulation needs clean, structured data objects so that:
- dataset-based defaults can be loaded cleanly
- the dashboard can show honest dataset context
- the simulation remains modular

### Minimum tests for preprocessing

After writing `preprocess_cyby23.py`, run:

```bash
python3 preprocess_cyby23.py
```

Confirm that it prints:
- dataset path used
- cleaned row count
- number of source posts
- number of labelled replies
- number of built thread records
- role distribution

Do not move on until this works.

## 9. Build the learning layer

Create `mesa_learning.py`.

This file centralises all role tendencies and learning updates.

### What it should contain

1. Action list

```python
ACTIONS = ["support_bully", "support_victim", "stay_silent", "step_aside"]
```

2. Role order

```python
ROLE_ORDER = ["instigator", "defender", "neutral", "other"]
```

3. Base role preferences

These are the starting behavioural tendencies before any learning occurs.

Example idea:
- instigators prefer `support_bully`
- defenders prefer `support_victim`
- neutrals prefer `stay_silent`
- others prefer `step_aside`

4. Reward update function

This updates how attractive an action becomes after the step result is known.

Example formula:

```python
new_value = current_value + learning_rate * reward_strength * reward
```

5. Role reward logic

Examples:
- instigators are rewarded when the bullying level rises after they support the bully
- defenders are rewarded when the bullying level falls after they support the victim
- neutrals may be penalized if silence contributes to worsening harm
- others get weak or near-neutral rewards

6. Continual learning state

Store:
- role-based learned action values
- run history
- run counter

7. Blending old and new learning

Use:
- `memory_retention_strength`
- `adaptation_speed`
- `carry_learning_into_next_run`

This lets the system keep some old experience while still adapting to new scenarios.

### Why this file matters

If learning logic is mixed into the dashboard or scattered across multiple files, the project becomes hard to debug and explain. This file should be the single place where the learning system is defined.

## 10. Build the agents

Create `mesa_agents.py`.

### Core idea

Each bystander is a Mesa agent.

Each agent should:
- know its role
- know its display position for the dashboard
- observe the current social context
- decide whether to participate this step
- choose an action
- pass that action back to the model

### Recommended classes

- `BaseBystanderAgent`
- `InstigatorAgent`
- `DefenderAgent`
- `NeutralAgent`
- `OtherAgent`

### Suggested agent properties

- `role`
- `visual_id`
- `display_x`
- `display_y`
- `last_action`
- `last_reward`
- `was_active`

### Theory of Mind in the agents

The simplest Theory of Mind layer is:
- look at last step's visible actions
- estimate whether the environment feels more:
  - bully-supporting
  - defending
  - silent

You can define a small helper structure:

```python
@dataclass
class SocialContext:
    bully_support_pressure: float
    defence_pressure: float
    silence_pressure: float
```

Then write a helper:

```python
def infer_social_context(previous_action_counts, total_agents):
    ...
```

### Agent decision process

Inside `step()`:

1. Decide whether the agent participates this step
2. Build ToM adjustments from visible social context
3. Combine:
   - base role preferences
   - learned action values
   - ToM influence
4. Choose one action
5. Register that action with the model

### Important design rule

Agents should not directly change the bullying level themselves.

Instead:
- agents choose actions
- the model collects all actions
- the model updates the environment after all agents have acted

This keeps the simulation logic consistent.

## 11. Build the Mesa model

Create `mesa_model.py`.

This is the main engine.

### What the model represents

The model represents one conversation environment.

It should store:
- number of bystanders
- role counts
- bullying intensity
- toxicity level
- profanity level
- identity attack level
- like influence
- retweet influence
- step count
- final outcome
- previous action counts
- total action counts
- story records
- working learning values
- persistent learning state

### Why the model owns the environment

The model represents the shared conversation environment. Agents are individual decision-makers inside it, but the model decides what happens to the overall bullying level after all actions are known.

### Recommended Mesa features to use

1. Inherit from `mesa.Model`
2. Use `self.agents.shuffle_do("step")`
3. Use `DataCollector`

### Agent activation

Mesa's `shuffle_do("step")` is useful because it:
- activates agents each step
- randomizes order
- keeps the simulation clean and current with Mesa's recommended patterns

### DataCollector

Use `DataCollector` to collect:
- step number
- bullying level
- number of bully-support actions
- number of defender actions
- number of silent actions
- number of unrelated actions
- bullying change
- current outcome

Optional agent-level collection:
- role
- last action
- last reward
- whether the agent acted

### Building agents inside the model

Write a `_build_agents()` method.

Suggested approach:
- convert role percentages into counts
- create that many agents of each type
- place them in a circular layout for visualisation

This is enough for a first version. A full grid or network is not necessary yet.

### The model step loop

Your `step()` method should do the following:

1. reset temporary action storage
2. infer social context from the previous step
3. activate agents using:

```python
self.agents.shuffle_do("step")
```

4. count actions chosen this step
5. compute bullying intensity change
6. update the bullying intensity
7. assign rewards to agents
8. update learning values
9. create a plain-English story line
10. check stopping conditions
11. collect data with `DataCollector`

### Bullying intensity update

Keep this interpretable.

Use:
- content pressure from toxicity, profanity, and identity attack
- support pressure from bully supporters
- defence pressure from defenders
- silence pressure from neutral bystanders
- engagement pressure from likes and retweets
- a small random variation

This formula does not need to be mathematically advanced. It just needs to be:
- transparent
- defensible
- easy to explain

### Stopping conditions

Use simple thresholds:
- if bullying intensity >= 80 -> `Got worse`
- if bullying intensity <= 20 -> `Calmed down`
- else if max steps reached -> `Stayed unresolved`

This makes the final result easy to explain to instructors and non-technical users.

## 12. Add repeated-run learning

At the end of a run:
- calculate action shares
- blend current learned values into the persistent memory state
- add one run-history summary record

Run history should store things like:
- run number
- average defender tendency
- average bully-support tendency
- average silent tendency
- action shares from the run
- final outcome

This makes it possible to show how agents change across runs.

## 13. Build the bridge layer

Create `mesa_bridge.py`.

This file exists because the dashboard should not have to understand Mesa internals.

### What the bridge should do

Take:
- simulation settings from Streamlit
- persistent learning state

Run:
- the Mesa model

Return:
- simple, dashboard-friendly result objects

### Suggested objects

- `SimulationConfig`
- `AgentProfile`
- `RoleComposition`
- `SimulationSnapshot`
- `SimulationPreview`
- `SimulationResult`

### Suggested bridge functions

`build_preview_state(config)`  
Returns the pre-run environment so the dashboard can show the bystander layout before the simulation starts.

`simulate_scenario(config, persistent_learning_state)`  
Runs the Mesa model to completion and returns:
- agent positions
- bullying history
- step-by-step snapshots
- final outcome
- explanation text
- updated learning state

### Why this file matters

Without a bridge layer, the dashboard becomes tightly coupled to Mesa classes and internal model state. That makes the UI harder to maintain.

## 14. Build the explanation layer

Create `abm_explanations.py`.

This file should provide plain-English text for:
- end-of-run explanation
- simple takeaway
- dataset connection text

### What the explanation should answer

1. What happened?
2. Why did it happen?
3. What role did the bystanders play?
4. How did social influence matter?
5. How did learning affect behaviour?
6. What does this mean in simple terms?

### Important communication rule

Do not use prediction language like:
- accuracy
- confidence score
- classifier output
- predicted probability

Use plain behavioural language like:
- the bullying became worse
- more people defended the victim
- silence allowed pressure to continue
- some agents were influenced by what they thought others would do

## 15. Build the chart and visual helper layer

Create `abm_ui_helpers.py`.

Use matplotlib only.

### Charts and outputs to include

1. Environment figure  
   Shows:
   - abuser
   - victim
   - bystanders
   - who was active in the current step

2. Bullying chart  
   Shows how the bullying level changes over time.

3. Role breakdown chart  
   Shows how many bystanders belong to each role.

4. Story table  
   Shows plain-English events at each step.

5. Learning tendency chart  
   Shows how defender, bully-support, and silent tendencies change across runs.

6. Action share chart  
   Shows how common different types of actions become across repeated runs.

### Why this file matters

The dashboard should stay clean. All figure-building code should live outside `dashboard.py`.

## 16. Build the Streamlit dashboard

Create `dashboard.py`.

### Recommended layout

Use three columns:

Left column:
- simulation controls
- presets
- advanced behaviour settings

Center column:
- environment view
- bullying chart
- story mode

Right column:
- final outcome
- role breakdown
- explanation
- dataset connection
- learning-over-runs charts

### Recommended controls

Basic simulation settings:
- total bystanders
- percentage of instigators
- percentage of defenders
- percentage of neutrals
- percentage of others
- starting bullying level
- toxicity level
- profanity level
- identity attack level
- likes influence
- retweets influence
- simulation speed
- random seed

Advanced behaviour settings:
- ToM influence strength
- learning rate
- reward strength
- memory retention strength
- adaptation speed
- carry learning into next run
- reset learning

### Buttons

- `Run Simulation`
- `Reset`
- `Random Scenario`
- `Defender-Heavy Scenario`
- `Neutral-Heavy Scenario`
- `Instigator-Heavy Scenario`
- `Load Dataset Example`

### Plain-English interface rule

Every section should be understandable to a non-technical person.

Examples:
- “How the bullying level changes over time”
- “Who is in this simulation”
- “What happened here?”
- “What this means in simple terms”

## 17. Use Streamlit session state

Store the following in `st.session_state`:
- current control values
- current result
- persistent learning state

This is important because continual learning must survive across repeated runs inside the same dashboard session.

### Why session state matters

Without session state:
- the dashboard resets too often
- learning history disappears
- repeated-run behaviour cannot be shown properly

## 18. How to animate the simulation

When the user clicks `Run Simulation`:

1. build a `SimulationConfig`
2. call the bridge function to run the Mesa model
3. store the result in session state
4. animate through the snapshots using placeholders

At each step:
- redraw the environment figure
- redraw the bullying chart
- redraw the story table
- pause briefly using `time.sleep(simulation_speed)`

This gives the interface a simple Mesa-style live simulation feel.

## 19. How to connect the dataset honestly

The dataset should be presented honestly.

Say:
- “The CYBY23 dataset provides the role patterns and harmful-content context behind this simulation.”

Do not say:
- “The model predicts what will happen in the real thread.”

We can use the dataset for:
- default role distributions
- risk-like starting settings
- thread-inspired scenarios

We should not use it as:
- a direct ground truth replay engine
- a model accuracy benchmark
- a basis for overclaiming realism

## 20. Suggested testing order

Test the system in this order:

1. preprocessing works
2. role mapping works
3. learning helper functions work
4. one Mesa agent can act
5. the Mesa model steps correctly
6. bullying intensity changes sensibly
7. stopping conditions work
8. learning memory updates across runs
9. the bridge returns the expected output shape
10. charts render correctly
11. the dashboard runs
12. dataset-based defaults load correctly

## 21. Useful terminal commands

### Run preprocessing

```bash
python3 preprocess_cyby23.py
```

### Compile-check the project

```bash
python3 -m py_compile preprocess_cyby23.py mesa_learning.py mesa_agents.py mesa_model.py mesa_bridge.py abm_ui_helpers.py abm_explanations.py dashboard.py
```

### Run the Streamlit dashboard

```bash
streamlit run dashboard.py
```

## 22. Common mistakes to avoid

### Technical mistakes

- putting too much logic inside `dashboard.py`
- letting agents directly change the bullying level one by one
- not separating run-specific learning from persistent memory
- mixing dataset preprocessing and simulation code together
- introducing too many advanced features before the basic model works

### Communication mistakes

- presenting the project as a prediction system
- overclaiming realism
- using too much machine learning language in the interface
- making the dashboard too technical for instructors or stakeholders

## 23. Recommended team workflow

### Role 1: Data and preprocessing

Responsible for:
- dataset loading
- cleaning
- role mapping
- thread summaries
- dataset-derived defaults

### Role 2: Mesa backend

Responsible for:
- learning logic
- agent classes
- Mesa model
- step logic
- run history

### Role 3: Dashboard and communication

Responsible for:
- Streamlit UI
- charts
- story mode
- explanation text
- final presentation polish

### Team coordination advice

- agree on shared naming conventions early
- keep dataclasses and interfaces stable
- define a clear output shape for the bridge
- test often rather than waiting until the end

## 24. What counts as “done” for the first full version

The first complete version should be able to:
- load the CYBY23 dataset
- show a simulation environment with agents
- run a real Mesa model
- update bullying intensity over time
- show a clear final outcome
- explain what happened in plain English
- carry some learning across repeated runs

If the project can do these things cleanly, it is already a strong applied prototype.

## 25. What can be extended later

Once the first version works, future extensions could include:
- a richer social network instead of a shared conversation environment
- agent neighbourhoods
- a moderator or platform intervention agent
- more detailed victim state modelling
- stronger dataset-based calibration
- richer continual learning mechanisms
- more advanced Mesa visualisation or deployment options

These are future extensions, not first-version requirements.

## 26. Final Advice for the Team

Build the project in layers.

Do not begin with the dashboard.
Do not begin with advanced learning logic.
Do not begin by trying to make it look impressive.

Begin with:
- clean data
- a small working Mesa model
- one step loop
- one chart
- one explanation

Once the simulation works properly, the rest becomes much easier.

The most important principle for this project is:

keep it interpretable, modular, and honest.

This is what makes the simulation suitable for a university applied project and easy to explain to instructors, teammates, and non-technical stakeholders.
