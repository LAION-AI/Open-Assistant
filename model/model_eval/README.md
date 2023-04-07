## OA Evaluation

### Requirements

- cd model/
  - `pip install -e . `
- cd oasst-data
  - `pip install -e .`

## Quick Start

- [Generate Sampling reports using SFT model](#generate-sampling-reports)
- [Evaluate Sampling reports using Reward model](#evaluate-sampling-reports-using-rm)
- [Rejection Sampling using Reward Model](#rejection-sampling-using-rm)

### Generate sampling reports

**Run**

```
python model/model_eval/manual/sampling_report.py --model-name facebook/galactica-125m --config config/default.json --prompts data/en_100_text.jsonl --report report_file.json -n 10 --verbose
```

### Evaluate sampling reports using RM

**Run**

```
python model/model_eval/sampling_score.py --model andreaskoepf/oasst-rm-1-pythia-1b --data_path model/model_eval/manual/sampling_reports/2023-03-01_theblackcat102_pythia-12b-deduped-sft_sampling.json
```

**Example Results**

```
 {'beam5': -1.592665433883667, 'greedy': -1.592665433883667, 'k50': -1.592665433883667, 'magic_numbers': -1.592665433883667, 'mean_reward': '-1.5926653'}
```

### Rejection sampling using RM

**Run**

```
python model/model_eval/rejection_sampling.py --data_path model/model_eval/manual/sampling_reports/2023-03-01_theblackcat102_pythia-12b-deduped-sft_sampling.json --model andreaskoepf/oasst-rm-1-pythia-1b
```

**Example Results**

```
{
    "rejected_samples": {
        "mean": "-1.9255",
        "min": "-3.12",
        "max": "-0.5"
    },
    "selected_samples": {
        "mean": "-1.0873333333333335",
        "min": "-2.82",
        "max": "0.26"
    }
}
```

- additionally, selected and rejected samples will be saved to seperate files
