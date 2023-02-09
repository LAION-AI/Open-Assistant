# Author: ParisNeo
# Description : An example of multi language translation using MBart50 (english to others)
# TODO : use to translate the database

from mbart_translator import MBartTranslator

translator = MBartTranslator()

texts_to_translate = [
    "Hello world",
    "Welcome back!",
    "Open assistant is a revolutionary chat bot",
    "A friend in need is a friend indeed",
]

conversion_languages = [
    {"name": "Arabic", "value": "ar_AR"},
    {"name": "Français", "value": "fr_XX"},
    {"name": "Deutsch", "value": "de_DE"},
    {"name": "Italiano", "value": "it_IT"},
    {"name": "Español", "value": "es_XX"},
    {"name": "українська", "value": "uk_UA"},
    {"name": "Русский", "value": "ro_RO"},
    {"name": "हिंदी", "value": "hi_IN"},
]

for text_to_translate in texts_to_translate:
    print("--")
    for lang in conversion_languages:
        output_text = translator.translate(text_to_translate, "en_XX", lang["value"])
        print(f"{lang['name']}  : {output_text}")
