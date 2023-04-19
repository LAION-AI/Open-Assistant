from enum import Enum, unique
from itertools import zip_longest
from random import shuffle

from pydantic import BaseModel, validator
from pydantic.fields import ModelField

QA_SPECIAL_TOKENS = {
    "Question": "<|prompter|>",
    "Answer": "<|assistant|>",
    "System": "<|system|>",
    "StartPrefix": "<|prefix_begin|>",
    "EndPrefix": "<|prefix_end|>",
}


class Mode(Enum):
    sft = "sft"
    rm = "rm"
    rl = "rl"


def format_system_prefix(prefix, eos_token):
    return "{}{}{}".format(
        QA_SPECIAL_TOKENS["System"],
        prefix,
        eos_token,
    )


@unique
class Language(str, Enum):
    AB = "ab"  # Abkhazian
    AA = "aa"  # Afar
    AF = "af"  # Afrikaans
    AK = "ak"  # Akan
    SQ = "sq"  # Albanian
    AM = "am"  # Amharic
    AR = "ar"  # Arabic
    AN = "an"  # Aragonese
    HY = "hy"  # Armenian
    AS = "as"  # Assamese
    AV = "av"  # Avaric
    AE = "ae"  # Avestan
    AY = "ay"  # Aymara
    AZ = "az"  # Azerbaijani
    BM = "bm"  # Bambara
    BA = "ba"  # Bashkir
    EU = "eu"  # Basque
    BE = "be"  # Belarusian
    BN = "bn"  # Bengali
    BH = "bh"  # Bihari languages
    BI = "bi"  # Bislama
    BS = "bs"  # Bosnian
    BR = "br"  # Breton
    BG = "bg"  # Bulgarian
    MY = "my"  # Burmese
    CA = "ca"  # Catalan, Valencian
    CH = "ch"  # Chamorro
    CE = "ce"  # Chechen
    NY = "ny"  # Chichewa, Chewa, Nyanja
    ZH = "zh"  # Chinese
    CV = "cv"  # Chuvash
    KW = "kw"  # Cornish
    CO = "co"  # Corsican
    CR = "cr"  # Cree
    HR = "hr"  # Croatian
    CS = "cs"  # Czech
    DA = "da"  # Danish
    DV = "dv"  # Divehi, Dhivehi, Maldivian
    NL = "nl"  # Dutch, Flemish
    DZ = "dz"  # Dzongkha
    EN = "en"  # English
    EO = "eo"  # Esperanto
    ET = "et"  # Estonian
    EE = "ee"  # Ewe
    FO = "fo"  # Faroese
    FJ = "fj"  # Fijian
    FI = "fi"  # Finnish
    FR = "fr"  # French
    FF = "ff"  # Fulah
    GL = "gl"  # Galician
    KA = "ka"  # Georgian
    DE = "de"  # German
    EL = "el"  # Greek, Modern (1453-)
    GN = "gn"  # Guarani
    GU = "gu"  # Gujarati
    HT = "ht"  # Haitian, Haitian Creole
    HA = "ha"  # Hausa
    HE = "he"  # Hebrew
    HZ = "hz"  # Herero
    HI = "hi"  # Hindi
    HO = "ho"  # Hiri Motu
    HU = "hu"  # Hungarian
    IA = "ia"  # Interlingua (International Auxiliary Language Association)
    ID = "id"  # Indonesian
    IE = "ie"  # Interlingue, Occidental
    GA = "ga"  # Irish
    IG = "ig"  # Igbo
    IK = "ik"  # Inupiaq
    IO = "io"  # Ido
    IS = "is"  # Icelandic
    IT = "it"  # Italian
    IU = "iu"  # Inuktitut
    JA = "ja"  # Japanese
    JV = "jv"  # Javanese
    KL = "kl"  # Kalaallisut, Greenlandic
    KN = "kn"  # Kannada
    KR = "kr"  # Kanuri
    KS = "ks"  # Kashmiri
    KK = "kk"  # Kazakh
    KM = "km"  # Central Khmer
    KI = "ki"  # Kikuyu, Gikuyu
    RW = "rw"  # Kinyarwanda
    KY = "ky"  # Kirghiz, Kyrgyz
    KV = "kv"  # Komi
    KG = "kg"  # Kongo
    KO = "ko"  # Korean
    KU = "ku"  # Kurdish
    KJ = "kj"  # Kuanyama, Kwanyama
    LA = "la"  # Latin
    LB = "lb"  # Luxembourgish, Letzeburgesch
    LG = "lg"  # Ganda
    LI = "li"  # Limburgan, Limburger, Limburgish
    LN = "ln"  # Lingala
    LO = "lo"  # Lao
    LT = "lt"  # Lithuanian
    LU = "lu"  # Luba-Katanga
    LV = "lv"  # Latvian
    GV = "gv"  # Manx
    MK = "mk"  # Macedonian
    MG = "mg"  # Malagasy
    MS = "ms"  # Malay
    ML = "ml"  # Malayalam
    MT = "mt"  # Maltese
    MI = "mi"  # Maori
    MR = "mr"  # Marathi
    MH = "mh"  # Marshallese
    MN = "mn"  # Mongolian
    NA = "na"  # Nauru
    NV = "nv"  # Navajo, Navaho
    ND = "nd"  # North Ndebele
    NE = "ne"  # Nepali
    NG = "ng"  # Ndonga
    NB = "nb"  # Norwegian Bokm√•l
    NN = "nn"  # Norwegian Nynorsk
    NO = "no"  # Norwegian
    II = "ii"  # Sichuan Yi, Nuosu
    NR = "nr"  # South Ndebele
    OC = "oc"  # Occitan
    OJ = "oj"  # Ojibwa
    CU = "cu"  # Church¬†Slavic, Old Slavonic, Church Slavonic, Old Bulgarian, Old¬†Church¬†Slavonic
    OM = "om"  # Oromo
    OR = "or"  # Oriya
    OS = "os"  # Ossetian, Ossetic
    PA = "pa"  # Panjabi, Punjabi
    PI = "pi"  # Pali
    FA = "fa"  # Persian
    PL = "pl"  # Polish
    PS = "ps"  # Pashto, Pushto
    PT = "pt"  # Portuguese
    QU = "qu"  # Quechua
    RM = "rm"  # Romansh
    RN = "rn"  # Rundi
    RO = "ro"  # Romanian, Moldavian, Moldovan
    RU = "ru"  # Russian
    SA = "sa"  # Sanskrit
    SC = "sc"  # Sardinian
    SD = "sd"  # Sindhi
    SE = "se"  # Northern Sami
    SM = "sm"  # Samoan
    SG = "sg"  # Sango
    SR = "sr"  # Serbian
    GD = "gd"  # Gaelic, Scottish Gaelic
    SN = "sn"  # Shona
    SI = "si"  # Sinhala, Sinhalese
    SK = "sk"  # Slovak
    SL = "sl"  # Slovenian
    SO = "so"  # Somali
    ST = "st"  # Southern Sotho
    ES = "es"  # Spanish, Castilian
    SU = "su"  # Sundanese
    SW = "sw"  # Swahili
    SS = "ss"  # Swati
    SV = "sv"  # Swedish
    TA = "ta"  # Tamil
    TE = "te"  # Telugu
    TG = "tg"  # Tajik
    TH = "th"  # Thai
    TI = "ti"  # Tigrinya
    BO = "bo"  # Tibetan
    TK = "tk"  # Turkmen
    TL = "tl"  # Tagalog
    TN = "tn"  # Tswana
    TO = "to"  # Tonga (Tonga Islands)
    TR = "tr"  # Turkish
    TS = "ts"  # Tsonga
    TT = "tt"  # Tatar
    TW = "tw"  # Twi
    TY = "ty"  # Tahitian
    UG = "ug"  # Uighur, Uyghur
    UK = "uk"  # Ukrainian
    UR = "ur"  # Urdu
    UZ = "uz"  # Uzbek
    VE = "ve"  # Venda
    VI = "vi"  # Vietnamese
    VO = "vo"  # Volap√ºk
    WA = "wa"  # Walloon
    CY = "cy"  # Welsh
    WO = "wo"  # Wolof
    FY = "fy"  # Western Frisian
    XH = "xh"  # Xhosa
    YI = "yi"  # Yiddish
    YO = "yo"  # Yoruba
    ZA = "za"  # Zhuang, Chuang
    ZU = "zu"  # Zulu


class DatasetEntry(BaseModel):
    questions: list[str]
    answers: list[str]
    context: str | None
    lang: Language | None
    length: int | None
    quality: float | None
    humor: float | None
    creativity: float | None

    @validator("length")
    def above_zero(cls, v) -> int:
        if v is not None and v < 0:
            raise ValueError(f"Length cannot be lower than 0. Received {v}")
        return v

    @validator("quality", "humor", "creativity")
    def between_0_1(cls, v, field: ModelField) -> float:
        if v is not None and not (0 <= v <= 1):
            raise ValueError(f"Field {field.name} must be between 0 and 1. Received {v}.")
        return v

    def system_tag(self, eos_token: str) -> str | None:
        relevant_system_infos = [
            (k, v) for k, v in self.__dict__.items() if k not in ["questions", "answers"] and v is not None
        ]
        if len(relevant_system_infos) > 0:
            shuffle(relevant_system_infos)
            system_tag_key_values = "\n".join([f"{k}: {v}" for k, v in relevant_system_infos])
            system_tag = f"{QA_SPECIAL_TOKENS['System']}{system_tag_key_values}\n{eos_token}"
            return system_tag

    def get_formatted(self, mode: Mode, eos_token: str) -> str | list[str]:
        system_tag = self.system_tag(eos_token)
        if mode == Mode.rl:
            if system_tag is not None:
                return f"{system_tag}{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{QA_SPECIAL_TOKENS['Answer']}"
            else:
                return f"{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{QA_SPECIAL_TOKENS['Answer']}"
        if system_tag is not None:
            qa_list = [system_tag]
        else:
            qa_list = list()
        for q, a in zip_longest(self.questions, self.answers):
            match (q, a):
                case (str(), str()):
                    qa_list.extend(
                        [
                            f"{QA_SPECIAL_TOKENS['Question']}{q}{eos_token}",
                            f"{QA_SPECIAL_TOKENS['Answer']}{a}{eos_token}",
                        ]
                    )
                case (str(), None):
                    qa_list.append(f"{QA_SPECIAL_TOKENS['Question']}{q}{eos_token}")
                case (None, None):
                    break
                case (None, str()):
                    raise ValueError("Received answer without getting corresponding question. Aborting")
        if mode == Mode.sft:
            return qa_list
        elif mode == Mode.rm:
            raise NotImplementedError("This is currently not implemented.")

    @classmethod
    def create_from_prompter_assistant_interplay(cls, qa: dict[str, str]):
        """Creates a DatasetEntry from a qa of given structure. Even if qa contains consecutative assistant or prompter phrases.


        Returns:
            self: DatasetEntry class
        """
        # todo: implement
        NotImplementedError("Function not implemented currently.")


def format_pairs(
    pairs: list[str] | DatasetEntry, eos_token: str, add_initial_reply_token: str = False, mode: Mode | None = None
) -> list[str]:
    if isinstance(pairs, DatasetEntry) and mode is not None:
        return pairs.get_formatted(mode=mode, eos_token=eos_token)
    else:
        # backwards compatibility
        conversations = [
            "{}{}{}".format(QA_SPECIAL_TOKENS["Question" if i % 2 == 0 else "Answer"], pairs[i], eos_token)
            for i in range(len(pairs))
        ]
        if add_initial_reply_token:
            conversations.append(QA_SPECIAL_TOKENS["Answer"])
        return conversations


def format_rl_text(pairs: list[str]) -> str:
    # convert question answer pairs to only the prefix prompt for RLHF
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[0], QA_SPECIAL_TOKENS["Answer"])


def format_reply(text: str, eos_token: str) -> str:
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Answer"], text, eos_token)
