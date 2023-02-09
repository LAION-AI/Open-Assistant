# MBartTranslator :
# Author : ParisNeo inspired by hugging face examples
# Description : MBartTranslator class provides a simple interface for translating text using the MBart language model.
#
#    The class can translate between 50 languages and is based on the "facebook/mbart-large-50-many-to-one-mmt"
#    pre-trained MBart model. However, it is possible to use a different MBart model by specifying its name.

from transformers import MBart50TokenizerFast, MBartForConditionalGeneration


class MBartTranslator:
    """MBartTranslator class provides a simple interface for translating text using the MBart language model.

    The class can translate between 50 languages and is based on the "facebook/mbart-large-50-many-to-one-mmt"
    pre-trained MBart model. However, it is possible to use a different MBart model by specifying its name.

    Attributes:
        model (MBartForConditionalGeneration): The MBart language model.
        tokenizer (MBart50TokenizerFast): The MBart tokenizer.
    """

    def __init__(self, model_name="facebook/mbart-large-50-many-to-many-mmt", src_lang=None, tgt_lang=None):

        self.supported_languages = [
            "ar_AR",
            "de_DE",
            "en_XX",
            "es_XX",
            "fr_XX",
            "hi_IN",
            "it_IT",
            "ja_XX",
            "ko_XX",
            "pt_XX",
            "ru_XX",
            "zh_XX",
            "af_ZA",
            "bn_BD",
            "bs_XX",
            "ca_XX",
            "cs_CZ",
            "da_XX",
            "el_GR",
            "et_EE",
            "fa_IR",
            "fi_FI",
            "gu_IN",
            "he_IL",
            "hi_XX",
            "hr_HR",
            "hu_HU",
            "id_ID",
            "is_IS",
            "ja_XX",
            "jv_XX",
            "ka_GE",
            "kk_XX",
            "km_KH",
            "kn_IN",
            "ko_KR",
            "lo_LA",
            "lt_LT",
            "lv_LV",
            "mk_MK",
            "ml_IN",
            "mr_IN",
            "ms_MY",
            "ne_NP",
            "nl_XX",
            "no_XX",
            "pl_XX",
            "ro_RO",
            "si_LK",
            "sk_SK",
            "sl_SI",
            "sq_AL",
            "sr_XX",
            "sv_XX",
            "sw_TZ",
            "ta_IN",
            "te_IN",
            "th_TH",
            "tl_PH",
            "tr_TR",
            "uk_UA",
            "ur_PK",
            "vi_VN",
            "war_PH",
            "yue_XX",
            "zh_CN",
            "zh_TW",
        ]

        self.model = MBartForConditionalGeneration.from_pretrained(model_name)
        self.tokenizer = MBart50TokenizerFast.from_pretrained(model_name, src_lang=src_lang, tgt_lang=tgt_lang)

    def translate(self, text: str, input_language: str, output_language: str) -> str:
        """Translate the given text from the input language to the output language.

        Args:
            text (str): The text to translate.
            input_language (str): The input language code (e.g. "hi_IN" for Hindi).
            output_language (str): The output language code (e.g. "en_US" for English).

        Returns:
            str: The translated text.
        """
        if input_language not in self.supported_languages:
            raise ValueError(f"Input language not supported. Supported languages: {self.supported_languages}")
        if output_language not in self.supported_languages:
            raise ValueError(f"Output language not supported. Supported languages: {self.supported_languages}")

        self.tokenizer.src_lang = input_language
        encoded_input = self.tokenizer(text, return_tensors="pt")
        generated_tokens = self.model.generate(
            **encoded_input, forced_bos_token_id=self.tokenizer.lang_code_to_id[output_language]
        )
        translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

        return translated_text[0]
