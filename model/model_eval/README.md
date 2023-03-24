## Evaluate Sampling Reports using Reward Model

### Requirements

- cd model/
  - `pip install -e . `
- cd oasst-data
  - `pip install -e .`

### Run

```
python model/model_eval/sampling_score.py --model andreaskoepf/oasst-rm-1-pythia-1b --data_path model/model_eval/manual/sampling_reports/2023-03-01_theblackcat102_pythia-12b-deduped-sft_sampling.json
```

## Example results

```
 {'beam5': -1.592665433883667, 'greedy': -1.592665433883667, 'k50': -1.592665433883667, 'magic_numbers': -1.592665433883667, 'mean_reward': '-1.5926653'}
```
