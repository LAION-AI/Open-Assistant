# Generate Topics, Questions, and Answers from a paragraph of text

This python code can be used to generate topics, questions, and answers from a
paragraph of text. This is a good way to generate ground truth knowledge about a
topic from a trusted source.

## Definitions

- **Topic:** A word that describes the topic of the paragraph, such as _Biology_
  or _Stem Cells_.
- **Prefix:** An introductory phrase that adds context to a question, such as
  _"Speaking of stem cells,"_
- **Open Book Answer:** An answer to a question that was generated using the
  provided paragraph as guidance.
- **Closed Book Answer:** An answer to a question that was generated without the
  use of the provided paragraph.
- **Formatted Answer:** An adjusted answer that expresses certainty in an answer
  based on the answer's confidence.
- **Confidence:** A score between 0 and 1 that is calculated by measuring the
  similarity between the given closed book answer and the open book answer.

## Output

The output of this is a dictionary with the following information:

1. Submitted paragraph
2. Sample topics
3. Sample questions
4. Sample answers
5. Generated topics
6. Generated questions
7. Generated prefixes
8. Generated open book answer
9. Generated closed book answer
10. Generated closed book answer with generated prefix as context
11. Formatted generated closed book answer
12. Formatted generated closed book answer with generated prefix as context

## Requirements

This code is verified to work on a 24GB vram graphics card (like an RTX3090). We
are working on getting it to run on Google Colab TPUs, and also it may be
possible to use smaller T5 models like the 3 billion parameter model and still
get acceptable results.
