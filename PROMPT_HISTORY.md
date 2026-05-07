# Prompt History

This file records the main user prompts used to guide development of the cyber-bystander simulation prototype in this project.

It is intended for teammates and instructors who want to understand how the prototype was specified and refined over time.

## 1. Initial project build prompt

The project began with a request to generate a clean, runnable Python project using Mesa that simulates cyberbullying interactions from the CYBY23 dataset.

Key requirements included:

- load and preprocess the CYBY23 Excel dataset
- identify source posts and bystander replies
- normalize bystander role labels into:
  - `reinforce`
  - `defend`
  - `neutral`
  - `unrelated`
- create a Mesa simulation with:
  - `SourcePostAgent`
  - `BystanderAgent`
  - optional `VictimAgent`
  - optional `ModeratorAgent`
- keep the first version rule-based, transparent, and academically defensible
- model bystander decisions using:
  - toxicity of the original post
  - sentiment
  - identity attack / insult / threat intensity
  - previous visible replies
  - conformity tendency
  - empathy tendency
  - moderation signals
- generate outputs including:
  - model class
  - agent classes
  - preprocessing script
  - runnable simulation script
  - matplotlib plots
  - demo script or notebook
  - README
- include metrics such as:
  - counts and proportions of simulated actions
  - escalation score
  - defence score
  - comparison against real labelled roles
- add simple scenario mode:
  - low-risk
  - medium-risk
  - high-risk

## 2. Interactive browser request

The next major request was to make the project interactive and accessible through a web browser.

Key request:

- provide a web browser URL
- make everything interactive

This led to:

- a Streamlit dashboard
- local browser hosting
- temporary public tunnel URLs for sharing the app

## 3. Plain-English dashboard redesign

The dashboard was then simplified for non-technical viewers.

Key request:

- rewrite the UI in plain English
- reduce technical jargon
- add helper text and short explanations
- organize the page as a story:
  - what this tool does
  - what data is being used
  - overall results
  - real behaviour vs model behaviour
  - example conversation walkthrough
  - advanced tables
- simplify chart titles and add short interpretation text
- make it suitable for instructors and teammates in a university setting

This led to:

- a plainer Streamlit dashboard
- friendlier labels
- layman-focused explanations
- separate simple and advanced sections

## 4. Learning extension prompt

The next major step was to extend the rule-based model with simplified Theory of Mind, Reinforcement Learning, and Continual Learning.

Key request:

- keep the model simple, explainable, and modular
- do not use deep learning or neural networks
- add Theory of Mind:
  - perceived aggression
  - perceived target vulnerability
  - perceived social norm
- add tabular Q-learning:
  - dictionary Q-table
  - alpha, gamma, epsilon
  - epsilon-greedy choice
- add continual learning:
  - rolling memory
  - forgetting / decay
  - bias future actions from recent outcomes
- update the decision pipeline to:
  - observe
  - infer mental state
  - build state
  - choose action
  - receive reward
  - update Q-table
  - update memory
- update the dashboard to show:
  - average Q-values
  - learning progress
  - action distribution over time
  - before-vs-after learning comparison
- add a learning mode toggle

This led to:

- `tom_module.py`
- `rl_module.py`
- `memory_module.py`
- learning-mode support in the model and dashboard

## 5. Repository sharing prompt

The project was then prepared for public sharing.

Key request:

- clean the project for GitHub
- improve:
  - `README.md`
  - `requirements.txt`
  - `.gitignore`
  - `LICENSE`
- remove unnecessary local artifacts
- initialize and commit the repository
- prepare it for public sharing with instructors and teammates

This led to:

- repo cleanup
- an MIT license
- a public-facing README
- git initialization and initial commit

## 6. Shareable app URL request

The project was also prepared for temporary web sharing through a public URL.

Key request:

- provide a URL link that teammates and instructors can open
- avoid GitHub-only sharing

This led to:

- public Cloudflare tunnel URLs pointing to the local Streamlit app

## Note

This file records the main prompts at a project level, not every exact assistant response or hidden system instruction.

If needed, a fuller transcript can also be prepared separately as:

- a detailed prompt-and-response log
- a meeting appendix
- a project development timeline
