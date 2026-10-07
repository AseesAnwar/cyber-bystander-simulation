# CYBY23 Data

The raw CYBERBYSTANDER (CYBY23) spreadsheet is intentionally not committed to this public repository.

Place a permitted local copy at:

```text
data/CYBERBYSTANDER (CYBY23) dataset.xlsx
```

or pass an explicit file path to the preprocessing / simulation command that supports it.

## Required columns

The preprocessing pipeline validates the presence of:

- `tweet_id`
- `reply_id`
- `created_at`
- `text`
- `user`
- `user_id`
- `sentiment`
- `Bystander Roles Label`
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
- `Class label`

If any required field is missing, preprocessing stops with a readable schema-validation error instead of continuing with partial data.

## Role normalization

Raw CYBY23 bystander labels are normalized into four simulation categories:

| CYBY23 meaning | Simulation role |
|---|---|
| agrees with harmful main post | reinforce / instigator |
| disagrees with harmful main post | defend / defender |
| takes neither side | neutral |
| unrelated reply | unrelated / other |

## Public-data note

The repository documents how the data are used without assuming permission to redistribute the source spreadsheet.
