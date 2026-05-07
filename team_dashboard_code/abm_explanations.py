from __future__ import annotations


ROLE_LABELS = {
    "instigator": "bully supporters",
    "defender": "victim supporters",
    "neutral": "silent bystanders",
    "other": "unrelated people",
}


def build_end_of_run_explanation(
    final_outcome: str,
    dominant_role: str,
    tom_strength: float,
    learning_rate: float,
    carry_learning: bool,
    final_bullying_level: float,
) -> tuple[str, str]:
    dominant_role_text = ROLE_LABELS.get(dominant_role, dominant_role)

    if final_outcome == "Got worse":
        main_text = (
            f"In this run, the bullying became worse because the social environment favoured harmful support or silence more than protection. "
            f"The strongest group in the environment was {dominant_role_text}, and the bullying level ended at {final_bullying_level:.1f}."
        )
    elif final_outcome == "Calmed down":
        main_text = (
            f"In this run, the bullying started calming down because supportive action for the victim was strong enough to reduce pressure from the harmful post. "
            f"The strongest group in the environment was {dominant_role_text}, and the bullying level ended at {final_bullying_level:.1f}."
        )
    else:
        main_text = (
            f"In this run, the situation stayed unresolved because harmful pressure and protective pressure stayed too balanced to clearly change direction. "
            f"The strongest group in the environment was {dominant_role_text}, and the bullying level ended at {final_bullying_level:.1f}."
        )

    tom_text = (
        "Social influence mattered a lot in this run because the Theory of Mind setting was high, so agents paid more attention to what they thought others would do."
        if tom_strength >= 0.6
        else "Social influence was present but moderate, so agents only partly adjusted to what they thought others would do."
        if tom_strength >= 0.3
        else "Social influence was kept low, so agents mostly followed their own role tendencies."
    )

    rl_text = (
        "Agents also learned from the results of their actions. When an action helped achieve their goal, they became more likely to repeat it later in the run."
        if learning_rate > 0
        else "Learning was effectively turned off, so the agents did not change much from one step to the next."
    )

    cl_text = (
        "Because carry learning was turned on, some of what agents learned in earlier runs was carried into this scenario."
        if carry_learning
        else "Because carry learning was turned off, the agents started this run without bringing forward earlier experience."
    )

    simple_terms = (
        "This means the bully is not the only reason the situation changes. The people watching also shape what happens next."
    )

    return f"{main_text} {tom_text} {rl_text} {cl_text}", simple_terms


def build_dataset_connection_text() -> str:
    return (
        "The CYBY23 dataset shows what kinds of bystanders appear in real online discussions. "
        "This dashboard uses those role ideas and aggression-related signals as inspiration. "
        "Theory of Mind, reinforcement learning, and continual learning are added here as simulation extensions to make the agents behave in a more adaptive way."
    )
