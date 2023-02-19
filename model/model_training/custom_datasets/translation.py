"""
    List of translation dataset

    GroNLP/divemt

    fill in the blanks : https://huggingface.co/datasets/m_lama

"""
import random

from custom_datasets.formatting import format_pair
from datasets import load_dataset
from torch.utils.data import Dataset

# postfix prompt
TRANSLATION_PROMPT = {
    "zh": [  # simplified or any chinese which was not mentioned
        "Translate to chinese simplified: {}",
        "{}, translate to chinese",
        "{} give me the chinese translation",
        "翻译成中文: {}",
        "{} 这句中文翻译怎麽写？",
        "我需要这句话的中文翻译: {}",
    ],
    "zh-tw": [  # WMT code
        "{}. Translate to chinese traditional",
        "{}, translate to chinese",
        "{}. get chinese translation",
        "中文翻譯: {}",
        "幫我翻譯成中文: '{}'",
        "{} 這句中文翻譯怎麼寫？",
    ],
    "ja": [
        "{}: help me translate to japanese",
        "Need japanese translation: {}",
        "{}: にほんごやくをよこす",
        "{}: にほんごやくをおくれ",
        "{}: にほんごやくを じょす",
        "give me the japanese translation, {}",
    ],
    "de": [
        "{}: translate to german",
        "give me the german translation {}",
        "I want german translation {}",
        "{}, ins Deutsche übersetzen",
        "{}, Übersetzen ins Deutsche",
    ],
    "fr": [
        "{}. translate to french",
        "{} write in french",
        "{} french translation",
        "{} ,donnez moi la traduction française",
    ],
    "ko": [
        "{}. translate to Korean",
        "how do we write in korean: {}",
        "give me the korean translation: {}",
        "{}, 한국어 번역을 해주세요",
    ],
    "ms": [
        "{} translate to malay",
        "{} how do we write in Malay",
        "{} give me the malay translation",
        "{} , berikan saya terjemahan dalam bahasa melayu",
        "{}, Jemahan di bahasa melayu",
        "{}, jemahkan ayat ini kepada bahasa melayu",
    ],
    "en": ["{}. translate to english", "{} write in english", "english translation: '{}'"],
    "ru": ["помогите мне перевести это на русский : {}", "{} перевести на русский язык", "russian translation: '{}'"],
    "tr": ["{}. türkçeye çevi̇ri̇n", "{} write in turkish", "turkish translation: '{}'", "türkçeye çevi̇rmek: {}"],
    "it": ["{}. translate to italian", "{} write in italian", "italian translation: '{}'"],
    "nl": ["{}. translate to dutch", "{} write in dutch", "dutch translation: '{}'"],
    "vi": ["{}. Dịch sang tiếng việt nam", "{} write in vietnamese", "vietnamese translation: '{}'"],
    "ar": ["{}. translate to arabic", "{} write in arabic", "arabic translation: '{}'"],
    "es": ["{}. translate to spanish", "{} write in spanish", "spanish translation: '{}'"],
    "hi": ["{}. translate to hindi", "{}. translate to bengali", "{} write in hindi", "bengali translation: '{}'"],
    "uk": [
        "{}. translate to ukrainian",
        "{} write in ukrainian",
        "ukrainian translation: '{}'",
        "переклади українською мовою: {}",
        "переклади на українську мову: {}",
        "{} переклади українською",
    ],
}


class TranslationPair(Dataset):
    def __init__(self, mix_prob=0.2) -> None:
        super().__init__()
        self.pairs = []
        self.length = -1
        self.mix_prob = mix_prob

    def __len__(self):
        if self.length < 0:
            self.length = len(self.pairs)
        return len(self.pairs)

    def __getitem__(self, index):
        if random.random() < self.mix_prob and index > 5 and index < (self.length - 5):
            additional = random.randint(0, 10) - 5
            while additional == index:
                additional = random.randint(0, 10) - 5

            history_text = "".join(format_pair(self.pairs[additional + index]))
            question, answer = self.pairs[index]
            question = history_text + question
            return format_pair((question, answer))

        return format_pair(self.pairs[index])


class WMT2019(TranslationPair):
    def __init__(self, pair="zh-en", split="train", mix_prob=0.2, maximum_size=100000) -> None:
        super().__init__(mix_prob=mix_prob)
        dataset = load_dataset("wmt19", pair)[split]
        self.pairs = []
        src, tgt = pair.split("-")
        for row in dataset:
            row = row["translation"]
            if random.random() > 0.5:
                source = random.choice(TRANSLATION_PROMPT[tgt]).format(row[src])
                self.pairs.append((source, row[tgt]))
            else:  # translating in reverse direction
                source = random.choice(TRANSLATION_PROMPT[src]).format(row[tgt])
                self.pairs.append((source, row[src]))
            # WMT is very large, reduce preprocessing time
            if len(self.pairs) > maximum_size:
                break


class DiveMT(TranslationPair):

    REMAP = {"tur": "tr", "ita": "it", "ukr": "uk", "nld": "nl", "vie": "vi", "ara": "ar"}

    def __init__(self, split="train", mix_prob=0.2) -> None:
        super().__init__(mix_prob=mix_prob)
        dataset = load_dataset("GroNLP/divemt", "main")[split]
        tgt, src = "tgt_text", "src_text"
        for row in dataset:
            # ISO 639-2
            lang_code_2 = row["subject_id"].split("_")[0]
            lang_code = self.REMAP[lang_code_2]
            if lang_code not in TRANSLATION_PROMPT:
                continue

            if random.random() > 0.5:
                source = random.choice(TRANSLATION_PROMPT[lang_code]).format(row[src])
                self.pairs.append((source, row[tgt]))
            else:  # translating in reverse direction
                lang_code = "en"
                source = random.choice(TRANSLATION_PROMPT[lang_code]).format(row[tgt])
                self.pairs.append((source, row[src]))


class TEDTalk(TranslationPair):
    # NOTE: DO NOT use chinese pair, mix with traditional and cantonese, not clean

    def __init__(self, pair="de-ja", split="train", year="2016", mix_prob=0.2, maximum_size=100000) -> None:
        super().__init__(mix_prob=mix_prob)
        dataset = load_dataset("ted_talks_iwslt", language_pair=pair.split("-"), year=year)[split]
        src, tgt = pair.split("-")
        for row in dataset:
            row = row["translation"]
            if random.random() > 0.5:
                source = random.choice(TRANSLATION_PROMPT[tgt]).format(row[src])
                self.pairs.append((source, row[tgt]))
            else:  # translating in reverse direction
                source = random.choice(TRANSLATION_PROMPT[src]).format(row[tgt])
                self.pairs.append((source, row[src]))
            # WMT is very large
            if len(self.pairs) > maximum_size:
                break
