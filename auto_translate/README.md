# Context
The objective of auto_translate module is enhancing the amount of data by
enriching each language with translations from data written in other languages.


# MBART translator

mbart_translator.py contains a class called MBartTranslator that allows
multilanguages translation. It uses the MBART-50 manu to many model from
facebook to convert textfrom a language to another.

I have already built the MBartTranslator class in
auto_translate/mbart_translator.py. I have also added an example code that shows
how it translates from a non english language to a non english language or from
english to other languages.

The code supports 50 languages : Arabic (ar_AR), Czech (cs_CZ), German (de_DE),
English (en_XX), Spanish (es_XX), Estonian (et_EE), Finnish (fi_FI), French
(fr_XX), Gujarati (gu_IN), Hindi (hi_IN), Italian (it_IT), Japanese (ja_XX),
Kazakh (kk_KZ), Korean (ko_KR), Lithuanian (lt_LT), Latvian (lv_LV), Burmese
(my_MM), Nepali (ne_NP), Dutch (nl_XX), Romanian (ro_RO), Russian (ru_RU),
Sinhala (si_LK), Turkish (tr_TR), Vietnamese (vi_VN), Chinese (zh_CN), Afrikaans
(af_ZA), Azerbaijani (az_AZ), Bengali (bn_IN), Persian (fa_IR), Hebrew (he_IL),
Croatian (hr_HR), Indonesian (id_ID), Georgian (ka_GE), Khmer (km_KH),
Macedonian (mk_MK), Malayalam (ml_IN), Mongolian (mn_MN), Marathi (mr_IN),
Polish (pl_PL), Pashto (ps_AF), Portuguese (pt_XX), Swedish (sv_SE), Swahili
(sw_KE), Tamil (ta_IN), Telugu (te_IN), Thai (th_TH), Tagalog (tl_XX), Ukrainian
(uk_UA), Urdu (ur_PK), Xhosa (xh_ZA), Galician (gl_ES), Slovene (sl_SI)

The model performance is not perfect. It tends to work better from and to
english than between two other languages.

We can also use other models available on Hugging face by just constructing
MBartTranslator with the model path (it will be automatically downloaded)

# TODO
There are still steps to do to make this module work

Now, the interesting part is what comes next.I am not yet familiar with the
database structure, so I am asking if someone can do this in my place:

We create a special user called translator. This user is used when creating new
prompts or answers using translation, it should be excluded from the
leaderboard.

The idea is that before translating a text, the translator user verifies that
this text was not written by him. Other wize we can fall into infinite loops.

So it just scans the database for non translated messages, and translate each
one to all other languages using the code I've added then post it with him as
the writer.

This should be executed periodically say every night for example. This allows us
to know what was written by real users and what was written by the translator.
Translations can be criticised by people using the classical rating tools.

I need a wizard who knows the database to do that.

Any one up for the challenge?
