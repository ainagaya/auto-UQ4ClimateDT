# auto-aifs

!WIP

Integration of `ai-models` with Autosubmit, to run using data from an FDB. 

### Prerequisites
- Autosubmit

### Generate an experiment

```
autosubmit expid \
  --description "auto-aifs" \
  --HPC MareNostrum5 \
  --minimal_configuration \
  --git_as_conf conf/ \
  --git_repo git@github.com:ainagaya/auto-aifs.git \
  --git_branch main

```

### Configure the experiment

### Run the experiment

```
autosubmit create $EXPID

autosubmit run $EXPID
```


