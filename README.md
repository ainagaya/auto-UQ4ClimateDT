# auto-UQ4ClimateDT

!WIP

Integration of `ai-models` with Autosubmit, to run using data from an FDB.

### Prerequisites
- Autosubmit

### Generate an experiment

```
autosubmit expid \
  --description "auto-aifs" \
  --HPC MareNostrum5ACC \
  --minimal_configuration \
  --git_as_conf conf/ \
  --git_repo git@github.com:ainagaya/auto-UQ4ClimateDT.git \
  --git_branch main

```

### Configure the experiment

### Run the experiment

```
autosubmit create $EXPID

autosubmit run $EXPID
```
