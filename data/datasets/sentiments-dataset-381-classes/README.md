---
dataset_info:
  features:
    - name: text
      dtype: string
    - name: sentiment
      dtype: string
  splits:
    - name: train
      num_bytes: 104602
      num_examples: 1061
  download_size: 48213
  dataset_size: 104602
license: apache-2.0
task_categories:
  - text-classification
language:
  - en
pretty_name: sentiments-dataset-381-classes
size_categories:
  - 1K<n<10K
---

# Sentiments Dataset (381 Classes)

## Dataset Description

This dataset contains a collection of labeled sentences categorized into 381
different sentiment classes. The dataset provides a wide range of sentiment
labels to facilitate fine-grained sentiment analysis tasks. Each sentence is
associated with a sentiment class name.

## Dataset Information

- Number of classes: 381
- Features: `text` (string), `sentiment` (string)
- Number of examples: 1,061

## Class Names

The dataset includes the following sentiment class names as examples:

- Positive
- Negative
- Neutral
- Joyful
- Disappointed
- Worried
- Surprised
- Grateful
- Indifferent
- Sad
- Angry
- Relieved
- Sentiment
- Excited
- Hopeful
- Anxious
- Satisfied
- Happy
- Nostalgic
- Inspired
- Impressed
- Amazed
- Touched
- Proud
- Intrigued
- Relaxed
- Content
- Comforted
- Motivated
- Frustrated
- Delighted
- Moved
- Curious
- Fascinated
- Engrossed
- Addicted
- Eager
- Provoked
- Energized
- Controversial
- Significant
- Revolutionary
- Optimistic
- Impactful
- Compelling
- Enchanted
- Peaceful
- Disillusioned
- Thrilled
- Consumed
- Engaged
- Trendy
- Informative
- Appreciative
- Enthralled
- Enthusiastic
- Influenced
- Validated
- Reflective
- Emotional
- Concerned
- Promising
- Empowered
- Memorable
- Transformative
- Inclusive
- Groundbreaking
- Evocative
- Respectful
- Outraged
- Unity
- Enlightening
- Artistic
- Cultural
- Diverse
- Vibrant
- Prideful
- Captivated
- Revealing
- Inspiring
- Admiring
- Empowering
- Connecting
- Challenging
- Symbolic
- Immersed
- Evolving
- Insightful
- Reformative
- Celebratory
- Validating
- Diversity
- Eclectic
- Comprehensive
- Uniting
- Influential
- Honoring
- Transporting
- Resonating
- Chronicle
- Preserving
- Replicated
- Impressive
- Fascinating
- Tributary
- Momentum
- Awe-inspiring
- Unearthing
- Exploratory
- Immersive
- Transportive
- Personal
- Resilient
- Mesmerized
- Legendary
- Awareness
- Evidence-based
- Contemporary
- Connected
- Valuable
- Referencing
- Camaraderie
- Inspirational
- Evoke
- Emotive
- Chronicling
- Educational
- Serene
- Colorful
- Melodious
- Dramatic
- Enlivened
- Wonderstruck
- Enchanting
- Grandiose
- Abundant
- Harmonious
- Captivating
- Mesmerizing
- Dedicated
- Powerful
- Mystical
- Picturesque
- Opulent
- Revitalizing
- Fragrant
- Spellbinding
- Lush
- Breathtaking
- Passionate
- Melodic
- Wonderland
- Invigorating
- Dappled
- Flourishing
- Ethereal
- Elaborate
- Kaleidoscope
- Harmonizing
- Tragic
- Transforming
- Marveling
- Enveloped
- Reverberating
- Sanctuary
- Graceful
- Spectacular
- Golden
- Melancholic
- Transcendent
- Delicate
- Awakening
- Intertwined
- Indelible
- Verdant
- Heartrending
- Fiery
- Inviting
- Majestic
- Lullaby-like
- Kissed
- Behold
- Soulful
- Splendid
- Whispering
- Masterpiece
- Moving
- Crystalline
- Tapestry
- Haunting
- Renewal
- Wisdom-filled
- Stunning
- Sun-kissed
- Symphony
- Awestruck
- Dancing
- Heart-wrenching
- Magical
- Gentle
- Emotion-evoking
- Embracing
- Floating
- Tranquil
- Celestial
- Breathless
- Symphonic
- Stillness
- Delightful
- Flawless
- Commanding
- Embraced
- Heartfelt
- Precise
- Adorned
- Beautiful
- Scattering
- Timeless
- Radiant
- Regal
- Sparkling
- Resilience
- Recognized
- Echoing
- Rebirth
- Cradled
- Tirelessly
- Glowing
- Icy
- Brilliant
- Anticipation
- Awakened
- Blossoming
- Enthralling
- Excitement
- Vivid
- Spellbound
- Mellifluous
- Intricate
- Silent
- Contrasting
- Poignant
- Perfumed
- Pure
- Magnificent
- Exquisite
- Anguished
- Harmonic
- Kaleidoscopic
- Gripping
- Soothing
- Intense
- Poetic
- Fragile
- Unwavering
- Intriguing
- Fairy-tale
- Ephemeral
- Joyous
- Resplendent
- Elegant
- Coaxing
- Illuminating
- Thunderous
- Cool
- Exciting
- Teeming
- Blissful
- Enduring
- Raw
- Adventurous
- Mysterious
- Enrapturing
- Marvelous
- Swirling
- Resonant
- Careful
- Whimsical
- Intertwining
- - and more

## Usage example

```python
from datasets import load_dataset
#Load the dataset
dataset = load_dataset("Falah/sentiments-dataset-381-classes")
#Convert the dataset to a pandas DataFrame
df = pd.DataFrame(dataset['train'])
#Get the unique class names from the "sentiment" column
class_names = df['sentiment'].unique()
#Print the unique class names
for name in class_names:
    print(f"Class Name: {name}")

```

## Application

The Sentiments Dataset (381 Classes) can be applied in various NLP applications,
such as sentiment analysis and text classification.

## Citation

If you use this dataset in your research or publication, please cite it as
follows:

For more information or inquiries about the dataset, please contact the dataset
author(s) mentioned in the citation.

```
@dataset{sentiments_dataset_381_classes),
  author = {Falah.G.Salieh},
  title = {Sentiments Dataset (381 Classes)},
  year = {2023},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/Falah/sentiments-dataset-381-classes},
}
```
