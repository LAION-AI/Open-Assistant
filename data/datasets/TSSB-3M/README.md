# Dataset summary

This dataset contains over 3 million isolated single statement bug fixes. Each
bug fix is related to a commit in a public Python that does not change more than
a single statement

1. The original dataset comes from the
   [TSSB-3M](https://zenodo.org/record/5845439) dataset
2. By requesting the GitHub api to obtain the commit message, we expand and
   create a new dataset
   [TSSB-3M-ext](https://huggingface.co/datasets/zirui3/TSSB-3M-ext)
3. Convert `TSSB-3M-ext` into instruction form to form the
   [TSSB-3M-instruction](https://huggingface.co/datasets/zirui3/TSSB-3M-instructions)
   dataset
