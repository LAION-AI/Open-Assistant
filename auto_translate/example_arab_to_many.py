# Author: ParisNeo
# Description : An example of multi language translation using MBart50
# TODO : use to translate the database

from mbart_translator import MBartTranslator

translator = MBartTranslator()

texts_to_translate = [
    "هذا هو Open Assistant",
    "مرحبًا بعودتك!",
    "الصبر كالجدار، لا يحطمه إلا الزمان",
    "الخير لا ينتظر، والشر يسعى إليه",
    "إذا لم تعد تعلم، فتعلم أن تعشق التعلم",
]

conversion_languages = [
    {"name" : "English", "value" : "en_XX"},
    {"name" : "Français", "value" : "fr_XX"},
    {"name" : "Deutsch", "value" : "de_DE"},
    {"name" : "Italiano", "value" : "it_IT"},
    {"name" : "Español", "value" : "es_XX"},
    {"name" : "українська", "value" : "uk_UA"},
    {"name" : "Русский", "value" : "ro_RO"},
    {"name" : "हिंदी", "value" : "hi_IN"},
]

for text_to_translate in texts_to_translate:
    print("--")
    for lang in conversion_languages:
        output_text = translator.translate(text_to_translate, "ar_AR", lang["value"])
        print(f"{lang['name']}  : {output_text}")
