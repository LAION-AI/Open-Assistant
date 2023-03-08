# Train & Evaluate Safety models

This is the Open Assistant Safety Folder and contains the following:

- Model training scripts
- Model infrence scripts
- Data processing scripts

## Mission Statment

Our mission at LAION-AI OpenAssistant safety team is to create a safety pipeline
that is not only compatible with the OpenAssistant model and project but can
also integrate with other systems outside of it. We are dedicated to making this
pipeline modifiable and robust to accommodate the diverse preferences of our
users.

We understand that our users come from different backgrounds and use various
types of hardware. Therefore, we strive to make our safety pipeline accessible
and able to run on consumer hardware, so everyone can benefit from its
protective features.

Through our commitment to innovation and collaboration, we will continue to
provide safety solutions that ensure the well-being of our users and the wider
community.

## Why create a safety pipeline?

Open source and extendable safety pipelines unfortunately do not exist on the
same on the same scale as those in ChatGPT and other commerical systems. To
further research in implementable, accurate, and extendable safety pipelines,
Open Assistant Safety Team will continue to push models and code to the public.
Much research has been done in things like toxicity detection and bias
mitigation in LLMs, however the implementation of such research in systems that
use language models as conversational agents in production settings has largely
gone undocumented. Furthermore, safety systems that interact with diverse
communities of users must be able accommodate user prefrences. This is paramount
in introducing LLM based systems all over the world. We hope that our work will
generate more research in this field, and allow others to create safe LLM based
systems.

## Training

- Set training configuration using `config.yaml`

```python
python model_training/t5_trainer.py
```
