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
  --git_as_conf conf/bootstrap/ \
  --git_repo git@github.com:ainagaya/auto-UQ4ClimateDT.git \
  --git_branch main

```

### Configure the experiment

Create a `conf/main.yml`:

```
MODEL:
  #NAME: neuralgcm_scaling
  NAME: neuralgcm
  CHECKPOINT_PATH: /gpfs/scratch/bsc32/bsc032376/tfm
  CHECKPOINT_NAME: models_v1_stochastic_1_4_deg.pkl
  CHECKPOINT: "%MODEL.CHECKPOINT_PATH%/%MODEL.CHECKPOINT_NAME%"
  ICS: fdb
    #ICS: era5
  SIMULATION: test
  REGENERATE_ICS: "true"
EXPERIMENT:
  MEMBERS: '1'
  DATELIST: 20210101
    #DATELIST: 19900101 20000101 20100101 
  CHUNKSIZE: 2
```

### Run the experiment

```
autosubmit create $EXPID

autosubmit run $EXPID
```
