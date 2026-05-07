# Codex + Mesa Guide for the Cyber-Bystander Simulation

This document explains how Codex and Mesa are used together in our cyber-bystander simulation project.

The main goal is to keep a clear separation between:
- `Mesa` as the real simulation framework
- `Codex` as the AI-assisted development support tool

This distinction is important for our team, our documentation, and any explanation we give to instructors.

## 1. Why This Document Exists

In this project, we are building an agent-based simulation of cyber-bystander behaviour in online bullying discussions.

Because we are using both Mesa and Codex, it is important that the team can clearly explain:
- what Mesa is doing
- what Codex is doing
- how they work together
- where human judgement is still essential

This file is meant to help the team speak about the project clearly and honestly.

## 2. Mesa: What It Does in This Project

Mesa is the actual agent-based modelling framework used to build and run the simulation.

Mesa is responsible for:
- defining the simulation model
- defining bystander agents
- stepping the simulation forward over time
- managing model-level state
- scheduling agent actions
- collecting run data

In practical terms, Mesa is what makes the project a real agent-based simulation rather than just a custom script.

### In our project, Mesa is used for:

- creating the `CyberBystanderMesaModel`
- creating bystander agents such as:
  - `InstigatorAgent`
  - `DefenderAgent`
  - `NeutralAgent`
  - `OtherAgent`
- running the simulation one step at a time
- updating bullying intensity over time
- collecting outputs through `DataCollector`

### Important point

If Codex were removed, Mesa would still remain the real backend used to run the simulation.

## 3. Codex: What It Does in This Project

Codex is not the simulation framework.

Codex is used as a development support tool to help the team build, refine, explain, and document the project more efficiently.

Codex can help with:
- generating starter code
- refactoring code into cleaner modules
- explaining Mesa concepts in plain English
- helping debug errors
- improving comments and documentation
- helping convert technical logic into dashboard-friendly explanation text

### In our project, Codex can support:

- writing the first version of `mesa_agents.py`
- helping structure `mesa_model.py`
- helping design the bridge between Mesa and Streamlit
- helping explain Theory of Mind, reinforcement learning, and continual learning
- helping write README and technical build guides
- helping prepare presentation-ready explanations for instructors

### Important point

If Mesa were removed, Codex alone would not make this a proper simulation framework.

Codex helps us build the project, but Mesa is what actually runs the model.

## 4. How Codex and Mesa Work Together

The simplest explanation is:

- `Mesa` builds and runs the simulation
- `Codex` helps us create, improve, and explain the Mesa project

This means the workflow often looks like this:

1. We decide what simulation feature we want to build.
2. We use Codex to help draft or improve the code.
3. We implement that feature in Mesa.
4. We test it ourselves.
5. We review whether it makes sense for the project.

### Example

If we want to add defender behaviour:

- Mesa handles the actual `DefenderAgent` class and simulation step logic
- Codex may help us draft the class, improve the function structure, or explain the logic in plain English

So Mesa is the engine, while Codex is the assistant.

## 5. Why This Combination Is Useful

Using Codex and Mesa together is useful because each serves a different purpose.

### Mesa gives us:

- a real agent-based modelling framework
- a structured model and agent system
- proper simulation logic
- extensibility for future work

### Codex gives us:

- faster prototyping
- support with modular code structure
- help translating technical work into understandable language
- support with documentation and debugging

Together, they help the team:
- build faster
- stay organised
- document the system more clearly
- keep the project manageable within one semester

## 6. What Codex Should Be Used For

Codex is most useful when used as a technical assistant.

Good uses of Codex in this project include:
- asking for help writing a Mesa model skeleton
- asking for help separating logic into files
- asking for help explaining a Mesa step loop
- asking for help debugging import errors or state issues
- asking for help writing documentation
- asking for help refining Streamlit labels and explanations

### Example Codex tasks by project stage

During preprocessing:
- help clean the dataset loader
- help normalize bystander role labels

During Mesa development:
- help define agent classes
- help structure model state
- help implement learning helpers

During dashboard development:
- help simplify interface text
- help build plain-English summaries
- help keep the UI understandable to non-technical users

## 7. What Codex Should Not Replace

Codex should not replace:
- the team's own understanding
- testing and validation
- critical thinking
- ethical collaboration
- academic responsibility

The team must still:
- understand the code before presenting it
- check that generated code works properly
- review all assumptions
- make final design decisions ourselves
- explain the system honestly

Codex can help us move faster, but it should never become a substitute for understanding.

## 8. How to Talk About Codex in a University Project

If instructors ask how Codex was used, a good explanation is:

“Codex was used as an AI coding assistant to help with development, debugging, documentation, and explanation. The actual simulation backend was implemented in Mesa, which is the real agent-based modelling framework used in the project.”

That wording is clear and honest.

Avoid saying things like:
- “Codex built the whole project for us”
- “The project runs on Codex”

Those statements are misleading.

Better phrasing:
- “Codex supported development”
- “Mesa powers the simulation”
- “The team reviewed, tested, and refined the implementation”

## 9. Ethical and Team Use

As a team, we should use Codex responsibly.

That means:
- sharing prompts and outputs openly if they affect team work
- reviewing generated code together when needed
- keeping clear authorship responsibility
- avoiding blind copy-paste without understanding

This matters because a university project still requires:
- real understanding
- original judgement
- ethical collaboration

## 10. Suggested Team Workflow

Here is a practical Codex + Mesa workflow for the team.

### Step 1: Define the feature ourselves

Decide what we want to add, for example:
- dataset preprocessing
- defender behaviour
- role-based learning
- dashboard explanation text

### Step 2: Use Codex for support

Ask Codex for:
- starter structure
- refactoring ideas
- bug fixes
- explanations

### Step 3: Implement in Mesa

Put the actual simulation logic into:
- `mesa_agents.py`
- `mesa_model.py`
- `mesa_learning.py`

### Step 4: Review together

Check:
- does the code work
- does it match the project scope
- is it understandable
- is it still honest and interpretable

### Step 5: Test and document

Run the simulation, inspect the dashboard, and document what the feature does.

## 11. Short Summary for Teammates

Use this summary if someone on the team wants the simplest explanation:

Mesa is the framework that actually runs the cyber-bystander simulation.  
Codex is the AI tool that helps us write, improve, debug, and explain the Mesa-based project.  
Mesa is the engine. Codex is the assistant.

## 12. Final Guidance

For this project, we should always keep the roles clear:

- Mesa = simulation framework
- Codex = development support
- Team = decision-makers, reviewers, testers, and presenters

That is the cleanest and most defensible way to explain how the project was built.
