# Project Proposal: Cyber-Bystander Behaviour Simulation Using Mesa and CYBY23

## 1. Project Context and Problem Definition

Online bullying is a serious problem for schools, universities, social media platforms, and digital communities. Harmful online conversations are not shaped only by the person who posts abusive content. They are also shaped by the people who reply, watch, support, defend, stay silent, or ignore the situation.

This project focuses on cyber-bystander behaviour in online bullying discussions. A cyber-bystander is someone who is present in an online harmful conversation but is not necessarily the original bully or the direct victim. Their response can make the situation worse, help calm it down, or allow it to continue.

The professional context for this project sits between online safety, education, digital wellbeing, and responsible artificial intelligence. Organisations that manage online communities need better ways to understand how harmful conversations develop. However, real online behaviour is complex, sensitive, and difficult to test directly. It would not be ethical or practical to create harmful situations with real users just to observe what happens.

This creates a suitable opportunity for an agent-based simulation. Instead of predicting exact human behaviour, the project builds a controlled simulation where different types of bystanders interact in a cyberbullying scenario. The simulation allows users to explore questions such as:

- What happens when more people support the bully?
- What happens when more people defend the victim?
- What happens when most people stay silent?
- How can social influence and repeated experience change bystander behaviour over time?

The problem is therefore:

**How can we build an understandable agent-based simulation that helps explain how different cyber-bystander roles may influence whether an online bullying conversation gets worse, calms down, or remains unresolved?**

This is a well-scoped problem for a one-semester Work Integrated Learning project because it does not require deploying a real-world moderation system. Instead, it produces a research prototype, a Mesa-based simulation backend, and an interactive dashboard that can be demonstrated to instructors and teammates.

The project is intentionally not framed as a prediction product. It does not claim to predict exactly what real people will do. Its purpose is to help stakeholders understand behavioural dynamics in a safe, transparent, and explainable way.

## 2. Evidence and Context Review

The project is supported by evidence from cyberbullying research, agent-based modelling, and a base paper on Theory of Mind, Reinforcement Learning, and Continual Learning for bullying intervention.

### Cyberbullying and Bystander Behaviour

Cyberbullying is a social problem, not just an individual behaviour problem. In online spaces, harmful posts can be amplified by replies, likes, shares, silence, or group pressure. This makes bystanders important because their behaviour can influence whether harm spreads or is challenged.

The CYBY23 cyber-bystander dataset is directly relevant because it contains online discussion data with labelled bystander roles. These labels allow the project to represent realistic categories of online responses, including people who reinforce harmful content, defend against it, stay neutral, or post unrelated replies.

For this project, the dataset is used to ground the simulation in real cyber-bystander role patterns. It is not used as a supervised machine learning target. This is important because the project is about behavioural exploration, not classification accuracy.

### Base Paper: Theory of Mind and Continual Reinforcement Learning for Bullying Intervention

The assigned base paper for this project is:

**Zhinin-Vera, L., González-García, J. J., López-Jaquero, V., Navarro, E., and González, P. (2026). _Theory of mind and continual reinforcement learning for bullying intervention_. Neural Computing and Applications, 38, Article 160. DOI: 10.1007/s00521-025-11835-w.**

This paper is central to the academic direction of the project. It proposes a multi-agent system for bullying intervention that combines:

- **Theory of Mind**, where agents reason about the beliefs, intentions, and emotional states of others.
- **Reinforcement Learning**, where agents learn from the results of previous actions.
- **Continual Learning**, where agents retain useful experience over time and adapt to new situations without starting from zero.

The paper uses a simulated school bullying environment with agents such as a bully, victim, observer, and teacher. It was implemented in Python using the Mesa framework. This makes it highly relevant because our project also uses Mesa to model social behaviour through interacting agents.

The base paper supports three important design decisions in this project.

First, it shows why a bullying simulation should include social roles. Bullying situations involve more than one person, and observers can influence whether harm continues or is interrupted. This directly supports our use of bystander roles such as Instigator, Defender, Neutral, and Other.

Second, it shows why fixed rules alone are limited. If agents always behave in the same way, the simulation cannot show how behaviour may change when social context changes. This supports our addition of simplified Theory of Mind, where agents consider what other bystanders appear to be doing.

Third, it shows why learning and memory matter. In the base paper, reinforcement learning and continual learning help agents improve over repeated scenarios. Our project adapts this idea in a simpler way by allowing bystander agents to adjust their tendencies across repeated simulation runs.

The paper's ablation study is also useful evidence. It compares a complete system using ToM, RL, and CL with reduced versions that remove some of those components. The results reported in the paper show that the complete system performs better than the simpler alternatives, especially because it combines social reasoning with long-term adaptation. This supports the project rationale for including all three concepts, while keeping them simplified and explainable for a university prototype.

There is one important difference. The base paper focuses on school bullying intervention, while this project focuses on cyberbullying discussions and cyber-bystander behaviour. Therefore, this project does not copy the paper exactly. Instead, it adapts the modelling idea to an online setting using the CYBY23 dataset.

### Agent-Based Modelling and Mesa

Agent-based modelling is appropriate for this problem because the outcome of a bullying conversation depends on the interaction of many individuals. A simple average or static chart cannot show how one person's action may influence the next person's response.

Mesa is a Python framework for agent-based modelling. It supports model classes, agent classes, step-by-step simulation, data collection, and reproducible experiments. This makes it suitable for building a transparent university prototype.

In this project, Mesa is used to represent:

- the online bullying environment
- the abuser and victim context
- bystander agents with different roles
- step-by-step changes in bullying intensity
- learning and memory across repeated runs

Mesa also helps separate the simulation logic from the dashboard. This is useful for academic presentation because the project can show both the user-friendly web interface and the underlying agent-based model.

### Responsible and Ethical Use of AI Assistance

Codex is used in this project as a coding and documentation assistant. It helps generate code structure, debug errors, improve explanations, and prepare documentation. Codex is not the simulation framework, and it is not the research method by itself.

The technical method remains a Mesa-based agent simulation written in Python. Codex supports development productivity, but the project logic, interpretation, scope, and academic framing are reviewed and explained by the project team.

This distinction is important for ethical collaboration. Using Codex is acceptable as a development aid when the team understands the code, verifies the outputs, and clearly explains what was built.

## 3. Project Aim and Research Questions

### Project Aim

The aim of this project is to build an interactive Mesa-based simulation that helps users understand how different cyber-bystander roles can influence whether an online bullying conversation escalates, de-escalates, or remains unresolved.

The project will use the CYBY23 dataset to ground bystander roles and harmful-content context, while using a simplified agent-based model to explore behavioural dynamics.

### Research Questions

1. How do different mixes of cyber-bystander roles influence whether a harmful online conversation becomes worse, calms down, or stays unresolved?

2. How does silence from neutral bystanders affect the simulated bullying level compared with active defending or active support for the bully?

3. How can simplified Theory of Mind help bystander agents respond to the visible behaviour of others in the conversation?

4. How can simple reinforcement learning and continual learning allow agents to adapt their behaviour across repeated simulation runs?

5. How can an interactive dashboard explain cyber-bystander dynamics clearly to both technical and non-technical stakeholders?

## 4. Proposed Methodology

### Data to Be Used

The project uses the CYBY23 cyber-bystander dataset provided as an Excel file.

Relevant fields include:

- user and user_id
- tweet_id and reply_id
- created_at
- text
- retweet_count and favorite_count
- Insult, Threat, Identity_Attack, Profanity, Toxicity, Severe_Toxicity
- polarity, subjectivity, sentiment
- Class label
- Bystander Roles Label

The dataset is used to identify role categories and harmful-content context. The bystander role labels are mapped into four simulation roles:

- reinforce becomes Instigator
- defend becomes Defender
- neutral becomes Neutral
- unrelated becomes Other

The dataset has limitations. It cannot fully reveal why a person acted in a certain way. It also does not directly contain Theory of Mind, reinforcement learning, or continual learning labels. These are modelling extensions inspired by the base paper, not direct measurements from the dataset.

### Technical Approach

The project uses an agent-based modelling approach.

The simulation environment represents one online bullying scenario at a time. It includes:

- one abuser or harmful original post
- one victim or target
- multiple bystanders
- a bullying level that changes over time

Each bystander is represented as an agent with a role:

- Instigator: tends to support the bully and increase bullying pressure
- Defender: tends to support the victim and reduce bullying pressure
- Neutral: tends to stay silent, which can indirectly allow harm to continue
- Other: has little or no direct effect on the bullying level

At each simulation step, bystander agents observe the current situation and choose an action. Their choices influence the bullying level. The simulation stops when the situation gets much worse, calms down, or reaches the maximum number of steps.

### Theory of Mind Method

Theory of Mind is implemented in a simplified way. Agents do not have full human-like reasoning. Instead, they estimate the visible social context:

- Are more people supporting the bully?
- Are more people defending the victim?
- Are most people staying silent?

This estimate influences later choices. For example, if defending appears common, undecided agents may become more likely to defend. If bully support dominates, some agents may hesitate or move toward harmful support.

This method answers the research questions by showing how perceived social pressure can change cyber-bystander behaviour.

### Reinforcement Learning Method

Reinforcement learning is implemented as simple reward-based updating, not deep learning.

Agents receive feedback after actions:

- defenders are rewarded when bullying decreases
- instigators are rewarded when bullying increases
- silence may be penalised when it contributes to worsening harm
- unrelated action has little effect

The agent then slightly adjusts its future tendencies. This allows the project to demonstrate learning without using complex neural networks.

This method answers the research questions by showing how repeated outcomes can influence future bystander behaviour.

### Continual Learning Method

Continual learning is implemented as memory across repeated simulation runs. Agents can carry part of their learned tendencies forward instead of resetting completely each time.

This allows the simulation to show gradual adaptation. For example, if defending repeatedly helps calm the situation, some agents may become more defender-prone over time.

This method is linked to the base paper because the paper argues that agents in bullying environments need to adapt over time rather than rely on fixed behaviour.

### Dashboard Method

The interactive dashboard is built with Streamlit. It allows users to change scenario settings and observe what happens. The dashboard avoids machine-learning language such as accuracy, prediction probability, training loss, or confusion matrix.

Instead, it focuses on:

- bystander role mix
- bullying level over time
- event story
- final outcome
- plain-English explanation
- dataset connection

This makes the project understandable for instructors, teammates, and non-technical stakeholders.

### Tools and Software

The project uses:

- Python for implementation
- Mesa for agent-based modelling
- Streamlit for the interactive dashboard
- pandas for dataset loading and preprocessing
- NumPy for numerical logic
- matplotlib for charts
- openpyxl for Excel loading
- Codex as a coding and documentation assistant
- VS Code and terminal for development

## 5. Expected Outcomes and Deliverables

The expected outputs are:

- a Mesa-based agent simulation backend
- an interactive Streamlit dashboard
- a cleaned CYBY23 preprocessing script
- role-mapping logic from dataset labels to simulation agents
- charts showing bullying level over time and bystander composition
- story-style event logs explaining what happened during the run
- plain-English conclusion panels for non-technical users
- project documentation and setup instructions
- a GitHub-ready codebase for sharing with instructors and teammates

The expected value of the project is educational and exploratory. It can help stakeholders understand that online bullying is not only shaped by the bully, but also by the surrounding audience. It can also provide a baseline for future work in AI-assisted online safety research.

For an industry or organisational setting, this kind of prototype could support early discussion around platform moderation, digital citizenship education, or bystander intervention strategies. However, it should not be used as a real moderation decision tool in its current form.

## 6. Timeline, Milestones, and Team Roles

### Proposed Semester Timeline

| Week | Milestone | Main Output |
| --- | --- | --- |
| 1-2 | Define project scope and review CYBY23 dataset | Problem statement and dataset understanding |
| 3-4 | Review evidence and base paper | Evidence review and modelling rationale |
| 5-6 | Build initial dataset preprocessing and role mapping | Cleaned data pipeline |
| 7-8 | Build Mesa agent model | Working simulation backend |
| 9 | Add simplified ToM, RL, and CL logic | Adaptive behaviour prototype |
| 10 | Build interactive dashboard | Streamlit demonstration app |
| 11 | Test scenarios and refine explanations | Improved usability and clearer outputs |
| 12 | Prepare final report, presentation, and GitHub repository | Final deliverables |

### Suggested Team Roles

If completed as a team project, responsibilities can be divided as follows:

- Technical Lead: designs the Mesa model, manages code structure, and integrates the dashboard.
- Data Lead: handles CYBY23 preprocessing, role mapping, and dataset limitations.
- Research Lead: writes the evidence review and connects the project to the base paper.
- UI and Presentation Lead: improves dashboard clarity, prepares screenshots, and supports the final presentation.
- Documentation Lead: maintains README, setup guide, proposal, and final report.

These roles can overlap, but the team should keep clear records of who contributed to which part. This supports ethical collaboration and avoids plagiarism.

## Learning Outcomes Alignment

This project supports the assessment learning outcomes in the following ways.

The project proposes a solution to a relevant online safety problem by using agent-based simulation rather than a black-box prediction model. It justifies this solution using the CYBY23 dataset, cyberbullying context, and the assigned ToM/RL/CL base paper.

The project builds a logical argument that bystander behaviour matters because online harm is shaped by group interaction. The simulation helps express that argument in a practical and visual way.

The project supports teamwork by separating responsibilities across data, research, modelling, interface design, and documentation. Codex can assist with coding and writing, but team members must understand, verify, and explain the work themselves.

The project is feasible within one semester because it is scoped as an early-stage research prototype. It does not attempt to deploy a production moderation tool or prove real-world causality. Instead, it produces a working simulation, dashboard, and documentation suitable for academic demonstration.

## Important Limitations

This project is an early-stage research prototype.

It does not predict exact real-world behaviour. It does not replace human moderation. It does not claim that CYBY23 directly measures mental states, learning, or memory. The ToM, RL, and CL components are simplified modelling extensions inspired by the base paper.

The dashboard should be presented as a tool for exploring assumptions about cyber-bystander behaviour, not as a tool for making decisions about real people.

## Key Reference

Zhinin-Vera, L., González-García, J. J., López-Jaquero, V., Navarro, E., and González, P. (2026). _Theory of mind and continual reinforcement learning for bullying intervention_. Neural Computing and Applications, 38, Article 160. https://doi.org/10.1007/s00521-025-11835-w
