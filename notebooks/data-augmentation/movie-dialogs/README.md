## Dataset Summary

The dataset was created using
[Cornell Movies Dialog Corpus](https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html)
which contains a large metadata-rich collection of fictional conversations
extracted from raw movie scripts. Dialogs and meta-data from the underlying
Corpus were used to design a dataset that can be used to InstructGPT based
models to learn movie scripts.

Example :

```
User: Assume RICK and ALICE are characters from a fantasy-horror movie, continue the conversation between them
    RICK: I heard you screaming.  Was it a bad one?
    ALICE: It was bad.
    RICK: Doesn't the dream master work for you anymore?
Assistant: Sure
    ALICE: I can't find him.
    RICK: Hey, since when do you play Thomas Edison?  This looks like Sheila's.
    ALICE: It is...was. It's a zapper, it might help me stay awake.
    RICK: Yeah, or turn you into toast.
```

## Usage

```python

from datasets import load_dataset
dataset = load_dataset("shahules786/OA-cornell-movies-dialog")
```

## Citations

```
@InProceedings{Danescu-Niculescu-Mizil+Lee:11a,
  author={Cristian Danescu-Niculescu-Mizil and Lillian Lee},
  title={Chameleons in imagined conversations:
  A new approach to understanding coordination of linguistic style in dialogs.},
  booktitle={Proceedings of the Workshop on Cognitive Modeling and Computational Linguistics, ACL 2011},
  year={2011}
}
```
