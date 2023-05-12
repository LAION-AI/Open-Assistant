import json
import random
import uuid
from dataclasses import dataclass

import datasets
import iso639
import language_names
import language_paraphrase
import language_translate
import pandas as pd

random.seed(42)


class DataProcess:
    # list of random quotes
    random_quote = [("'", "'"), ("“", "”"), ("῎", "῏"), ("`", "´"), ("«", "»"), ('"', '"')]

    # provide instruction with a text; process of randomization of a text
    def randomize_text(self, text, original_lang=None, target_lang=None):
        templates = (
            language_translate.random_templates_translate.get(original_lang, {})
            if not ((original_lang == target_lang) and (original_lang is not None) and (target_lang is not None))
            else language_paraphrase.random_templates_paraphrase.get(original_lang, {})
        )
        template = random.choice(list(templates.values()))
        quote_pair = random.choice(DataProcess().random_quote)
        opening_quote, closing_quote = quote_pair
        original_lang_name = DataProcess.language_name(None, original_lang, original_lang)
        target_lang_name = DataProcess.language_name(None, target_lang, original_lang)
        return template.format(
            text=text,
            lang1=target_lang_name,
            lang2=original_lang_name,
            opening_quote=opening_quote,
            closing_quote=closing_quote,
        )

    # convert to iso639_1
    def convert_code(self, code):
        mapped_code = iso639.to_iso639_1(code)
        return mapped_code

    # return language #1 name in language #2
    def language_name(self, lang1, lang2):
        name = language_names.language_names.get(lang1, {}).get(lang2)
        if name is not None:
            return name
        # just in case
        elif lang1 == lang2:
            iso_name = iso639.to_native(lang1)
            return iso_name
        else:
            return None


converter = DataProcess()

"""
EXAMPLES:

# get language name; iso639_1 code
print(converter.language_name('ru', 'en')) # Output: Russian
print(converter.convert_code("eng")) # Output: en

# convert into INSTRUCTION format: text; to; from
text = "test"
print(converter.randomize_text(text, "uk", "fr")) # Ти можеш перекласти цей вислів: 'test'?
print(converter.randomize_text(text, "uk", "de")) # Переклади наступний текст "test" з мови "німецька мова"
"""


@dataclass
class QnA:
    INSTRUCTION: str
    RESPONSE: str
    SOURCE: str
    METADATA: str


# format to QnA
def create_qna(row):
    # get rows; create uuid based on texts
    text = row["Text"]
    text_length = len(text)
    translation = row["Translated text"]
    lang_from = converter.convert_code(row["Original lang"])
    lang_to = converter.convert_code(row["Target lang"])
    uuid_val = uuid.uuid3(uuid.NAMESPACE_OID, str(text + translation))
    # json with language, original text length, uuid and langs-pair
    METADATA = {
        "language": f"{lang_to}",
        "length": f"{text_length}",
        "uuid": f"{uuid_val}",
        "langs-pair": f"{lang_from}-{lang_to}",
    }
    metadata_str = json.dumps(METADATA)
    source = "tatoeba"
    # randomizing INSTRUCTION
    instruction = converter.randomize_text(text, lang_to, lang_from)
    response = translation
    return QnA(instruction, response, source, metadata_str)


# load the dataset from Hugging Face
hf_dataset = datasets.load_dataset("0x22almostEvil/tatoeba-mt-llama-only", split="train")

# original is ~3M; with num_shards=30 it'll be ~120K
hf_dataset = hf_dataset.shard(num_shards=30, index=0)
print(hf_dataset)

# convert the dataset to a pandas dataframe
df = pd.DataFrame(hf_dataset)

# apply the create_qna function to each row of the dataframe to create QnA objects
qna_list = df.apply(create_qna, axis=1).tolist()

# save the QnA objects as a parquet file
qna_df = pd.DataFrame(qna_list, columns=["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"])
qna_df.to_parquet("translation-taboeba-qna-120k-oa.parquet", row_group_size=100, engine="pyarrow", index=False)
