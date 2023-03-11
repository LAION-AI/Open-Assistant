## Contents

- This notebook uses data from
  [one million reddit confessions](https://www.kaggle.com/datasets/pavellexyr/one-million-reddit-confessions)
  and [prosocial-dialog]() to synthesize samples to help train safety models.
- A [classifier](https://huggingface.co/shahules786/prosocial-classifier)
  trained on prosocial dialog dataset is used for pseudo labeling.
- More information on dataset can be found
  [here](https://huggingface.co/datasets/shahules786/prosocial-confessions)

## Example

```
{
 'context': 'I lie to my friends to get out of going to bars/restaurants',
 'rots': ["You shouldn't lie to your friends",
  'You should not lie to your friends'],
 'permalink': 'https://old.reddit.com/r/confession/comments/phgi8h/i_lie_to_my_friends_to_get_out_of_going_to/',
 'episone_done': True,
 'confidence': 0.87353515625,
 'safety_label': '__needs_caution__',
 'response': None
 }

```

## Citations

```
@inproceedings{
    kim2022prosocialdialog,
    title={ProsocialDialog: A Prosocial Backbone for Conversational Agents},
    author={Hyunwoo Kim and Youngjae Yu and Liwei Jiang and Ximing Lu and Daniel Khashabi and Gunhee Kim and Yejin Choi and Maarten Sap},
    booktitle={EMNLP},
    year=2022
}
```
