# random lists for ws

# sim_questions
random_list_sim_en_q = [
    "Are the words {word1} and {word2} synonymous?",
    'Are "{word1}" and "{word2}" synonymous?',
    "Is there any connection between the words '{word1}' and '{word2}'?",
]
random_list_sim_ru_q = [
    "Являются ли слова {word1} и {word2} синонимами?",
    'Синонимы ли "{word1}" и "{word2}"?',
    "Есть ли какая-то связь между словами '{word1}' и '{word2}'?",
]
random_list_sim_de_q = [
    "Sind die Wörter {word1} und {word2} Synonyme?",
    'Sind "{word1}" und "{word2}" Synonyme?',
    "Gibt es eine Verbindung zwischen den Wörtern '{word1}' und '{word2}'?",
]
random_list_sim_it_q = [
    "Le parole {word1} e {word2} sono sinonimi?",
    '"{word1}" e "{word2}" sono sinonimi?',
    "C'è qualche connessione tra le parole '{word1}' e '{word2}'?",
]

# sim_answers:

# yes;
random_list_sim_en_a_y = [
    "Yes, {word1} and {word2} are synonymous.",
    '"{word1}" and "{word2}" are synonymous.',
    "Yes. The type of connection between words '{word1}' and '{word2}' is synonymous.",
]
random_list_sim_ru_a_y = [
    "Да, {word1} и {word2} являются синонимами.",
    '"{word1}" и "{word2}" являются синонимами.',
    "Да. Тип связи между словами '{word1}' и '{word2}' синонимичен.",
]
random_list_sim_de_a_y = [
    "Ja, {word1} und {word2} sind Synonyme.",
    '"{word1}" und "{word2}" sind Synonyme.',
    "Ja. Der Typ der Verbindung zwischen den Wörtern '{word1}' und '{word2}' ist synonym.",
]

random_list_sim_it_a_y = [
    "Sì, {word1} e {word2} sono sinonimi.",
    '"{word1}" e "{word2}" sono sinonimi.',
    "Sì. Il tipo di connessione tra le parole '{word1}' e '{word2}' è sinonimico.",
]

# 50%;
random_list_sim_en_a_50 = [
    "There is some connection between the words {word1} and {word2}, but they are not full-fledged synonyms.",
    'No, "{word1}" and "{word2}" are not synonymous, but they do have a slight semantic similarity.',
    "Yes, there is some connection between '{word1}' and '{word2}', but they cannot be called synonyms.",
]
random_list_sim_ru_a_50 = [
    "Между словами {word1} и {word2} есть некая связь, но они не являются полноценными синонимами.",
    'Нет, "{word1}" и "{word2}" не синонимы, но у них есть небольшое семантическое сходство.',
    "Да, между '{word1}' и '{word2}' есть некоторая связь, но их нельзя назвать синонимами.",
]
random_list_sim_de_a_50 = [
    "Es gibt eine gewisse Verbindung zwischen den Wörtern {word1} und {word2}, aber sie sind keine vollwertigen Synonyme.",
    'Nein, "{word1}" und "{word2}" sind keine Synonyme, aber sie haben eine leichte semantische Ähnlichkeit.',
    "Ja, es gibt eine Verbindung zwischen '{word1}' und '{word2}', aber man kann sie nicht als Synonyme bezeichnen.",
]
random_list_sim_it_a_50 = [
    "C'è una certa connessione tra le parole {word1} e {word2}, ma non sono sinonimi completi.",
    'No, "{word1}" e "{word2}" non sono sinonimi, ma hanno una leggera somiglianza semantica.',
    "Sì, c'è una connessione tra le parole '{word1}' e '{word2}', ma non possono essere chiamate sinonimi.",
]

# no;
random_list_sim_en_a_n = [
    "No, the words {word1} and {word2} are not synonyms.",
    'No, "{word1}" and "{word2}" are not synonymous.',
    "There is no direct connection between '{word1}' and '{word2}'.",
]
random_list_sim_ru_a_n = [
    "Нет, слова {word1} и {word2} не являются синонимами.",
    'Нет, "{word1}" и "{word2}" не синонимы.',
    "Между словами '{word1}' и '{word2}' нет прямой связи.",
]
random_list_sim_de_a_n = [
    "Nein, die Wörter {word1} und {word2} sind keine Synonyme.",
    'Nein, "{word1}" und "{word2}" sind keine Synonyme.',
    "Es besteht keine direkte Verbindung zwischen '{word1}' und '{word2}'.",
]

random_list_sim_it_a_n = [
    "No, le parole {word1} e {word2} non sono sinonimi.",
    'No, "{word1}" e "{word2}" non sono sinonimi.',
    "Non c'è una connessione diretta tra '{word1}' e '{word2}'.",
]

# rel_questions:
random_list_rel_en_q = [
    "Are there any associations between the words {word1} and {word2}?",
    'Are the words "{word1}" and "{word2}" related?',
    "What is the association between '{word1}' and '{word2}'?",
]
random_list_rel_ru_q = [
    "Есть ли ассоциации между словами {word1} и {word2}?",
    'Связаны ли как-то слова "{word1}" и "{word2}"?',
    "Насколько ассоциативно значение слов '{word1}' и '{word2}'?",
]
random_list_rel_de_q = [
    "Gibt es Assoziationen zwischen den Wörtern {word1} und {word2}?",
    'Sind die Wörter "{word1}" und "{word2}" miteinander verwandt?',
    "Welche Verbindung besteht zwischen '{word1}' und '{word2}'?",
]
random_list_rel_it_q = [
    "Ci sono associazioni tra le parole {word1} e {word2}?",
    'Esiste una relazione tra le coppie di parole "{word1}" e "{word2}"?',
    "Qual è l'associazione tra '{word1}' e '{word2}'?",
]

# rel_answers:

# yes;
random_list_rel_en_a_y = [
    "Yes, there is an association between the words {word1} and {word2}.",
    'Yes, there is an associative relationship between the words "{word1}" and "{word2}".',
    "There is a direct associative link between the words '{word1}' and '{word2}'.",
]
random_list_rel_ru_a_y = [
    "Да, между словами {word1} и {word2} прослеживается ассоциация.",
    'Да, между словами "{word1}" и "{word2}" есть ассоциативная связь.',
    "Есть прямая ассоциативная связь между словами '{word1}' и '{word2}'",
]
random_list_rel_de_a_y = [
    "Ja, es gibt eine Assoziation zwischen den Wörtern {word1} und {word2}.",
    'Ja, es besteht eine assoziative Beziehung zwischen den Wörtern "{word1}" und "{word2}".',
    "Es gibt eine direkte assoziative Verbindung zwischen den Wörtern '{word1}' und '{word2}'.",
]
random_list_rel_it_a_y = [
    "Sì, c'è un'associazione tra le parole {word1} e {word2}.",
    'Sì, c\'è una relazione associativa tra le parole "{word1}" e "{word2}".',
    "C'è un legame associativo diretto tra le parole '{word1}' e '{word2}'.",
]

# 50%;
random_list_rel_en_a_50 = [
    "There is a slight association between the words {word1} and {word2}.",
    'There is an indirect semantic similarity between the words "{word1}" and "{word2}".',
    "There is some association between the words '{word1}' and '{word2}'.",
]
random_list_rel_ru_a_50 = [
    "Есть небольшая ассоциация между словами {word1} и {word2}.",
    'Между словами "{word1}" и "{word2}" есть непрямое семантическое сходство.',
    "Есть некоторая ассоциативность между словами '{word1}' и '{word2}'.",
]
random_list_rel_de_a_50 = [
    "Es besteht eine leichte Assoziation zwischen den Wörtern {word1} und {word2}.",
    'Es gibt eine indirekte semantische Ähnlichkeit zwischen den Wörtern "{word1}" und "{word2}".',
    "Es besteht eine gewisse Verbindung zwischen den Wörtern '{word1}' und '{word2}'.",
]
random_list_rel_it_a_50 = [
    "C'è una leggera associazione tra le parole {word1} e {word2}.",
    'C\'è una somiglianza semantica indiretta tra le parole "{word1}" e "{word2}".',
    "C'è una certa associazione tra le parole '{word1}' e '{word2}'.",
]

# no;
random_list_rel_en_a_n = [
    "No, there is no associative relationship between the words {word1} and {word2}",
    'No, the words "{word1}" and "{word2}" are not related in any direct associative way.',
    "There is no direct associative relationship between '{word1}' and '{word2}'.",
]
random_list_rel_ru_a_n = [
    "Нет, между словами {word1} и {word2} нет ассоциативной связи",
    'Нет, слова "{word1}" и "{word2}" не связаны каким-либо прямым ассоциативным образом.',
    "Нет никакой прямой ассоциативной связи между '{word1}' и '{word2}'.",
]
random_list_rel_de_a_n = [
    "Nein, es besteht keine Assoziationsbeziehung zwischen den Wörtern {word1} und {word2}.",
    'Nein, die Wörter "{word1}" und "{word2}" sind nicht in direkter assoziativer Weise miteinander verbunden.',
    "Es besteht keine direkte assoziative Beziehung zwischen '{word1}' und '{word2}'.",
]
random_list_rel_it_a_n = [
    "No, non c'è alcuna relazione associativa tra le parole {word1} e {word2}.",
    'No, le parole "{word1}" e "{word2}" non sono correlate in alcun modo associativo diretto.',
    "Non c'è una diretta relazione associativa tra '{word1}' e '{word2}'.",
]

# easy-way to call stuff above

# dicts of q
# sim
random_dict_sim_q = {
    "en": random_list_sim_en_q,
    "ru": random_list_sim_ru_q,
    "de": random_list_sim_de_q,
    "it": random_list_sim_it_q,
}
# rel
random_dict_rel_q = {
    "en": random_list_rel_en_q,
    "ru": random_list_rel_ru_q,
    "de": random_list_rel_de_q,
    "it": random_list_rel_it_q,
}

# dicts for a
# sim - random_dict_sim_a["ru"][0]  # returns the list of "yes" answers for Russian
random_dict_sim_a = {
    "en": {
        0: random_list_sim_en_a_y,
        1: random_list_sim_en_a_50,
        2: random_list_sim_en_a_n,
    },
    "ru": {
        0: random_list_sim_ru_a_y,
        1: random_list_sim_ru_a_50,
        2: random_list_sim_ru_a_n,
    },
    "de": {
        0: random_list_sim_de_a_y,
        1: random_list_sim_de_a_50,
        2: random_list_sim_de_a_n,
    },
    "it": {
        0: random_list_sim_it_a_y,
        1: random_list_sim_it_a_50,
        2: random_list_sim_it_a_n,
    },
}
# rel
random_dict_rel_a = {
    "en": {
        0: random_list_rel_en_a_y,
        1: random_list_rel_en_a_50,
        2: random_list_rel_en_a_n,
    },
    "ru": {
        0: random_list_rel_ru_a_y,
        1: random_list_rel_ru_a_50,
        2: random_list_rel_ru_a_n,
    },
    "de": {
        0: random_list_rel_de_a_y,
        1: random_list_rel_de_a_50,
        2: random_list_rel_de_a_n,
    },
    "it": {
        0: random_list_rel_it_a_y,
        1: random_list_rel_it_a_50,
        2: random_list_rel_it_a_n,
    },
}
