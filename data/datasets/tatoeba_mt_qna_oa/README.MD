# Multilingual Tatoeba Q&A Translation Dataset

120K entries

This dataset contains a list of instructions to translate or paraphrase in
multiple languages. It is available in Parquet format and includes the following
columns:

- INSTRUCTION: The instruction of text to be translated or paraphrased.
- RESPONSE: The corresponding response or answer in target language.
- SOURCE (tatoeba): The original source text from the Tatoeba database.
- METADATA (json): Additional information about each entry, including the target
  language, UUID, and pair of languages (source and target). "{"language":
  "lang", "length": "length of original text","uuid": "uuid (original text +
  translated text)", "langs-pair": "from_lang-to_lang"}"

The data in this dataset was collected through crowdsourcing efforts and
includes translations of various types of content, such as sentences, phrases,
idioms, and proverbs.

You can find it here:
https://huggingface.co/datasets/0x22almostEvil/tatoeba-mt-qna-oa Original
dataset is available here:
https://huggingface.co/datasets/Helsinki-NLP/tatoeba_mt
