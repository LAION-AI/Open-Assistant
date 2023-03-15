from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ARTICLE = """ New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York.
# A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband.
# Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other.
# In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage.
# Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the
# 2010 marriage license application, according to court documents.
# Prosecutors said the marriages were part of an immigration scam.
# On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further.
# After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective
# Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002.
# All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say.
# Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages.
# Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted.
# The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s
# Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali.
# Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force.
# If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18.
# """

ARTICLE = """
In Greek mythology, Achilles ( ) or Achilleus () was a hero of the Trojan War, the greatest of all the Greek warriors, and is the central character of Homer's Iliad. He was the son of the Nereid Thetis and Peleus, king of Phthia.
Achilles' most notable feat during the Trojan War was the slaying of the Trojan prince Hector outside the gates of Troy. Although the death of Achilles is not presented in the Iliad, other sources concur that he was killed near the end of the Trojan War by Paris, who shot him with an arrow. Later legends (beginning with Statius' unfinished epic Achilleid, written in the 1st century AD) state that Achilles was invulnerable in all of his body except for one heel, because when his mother Thetis dipped him in the river Styx as an infant, she held him by one of his heels. Alluding to these legends, the term "Achilles' heel" has come to mean a point of weakness, especially in someone or something with an otherwise strong constitution. The Achilles tendon is also named after him due to these legends.
Etymology
Linear B tablets attest to the personal name Achilleus in the forms a-ki-re-u and a-ki-re-we, the latter being the dative of the former. The name grew more popular, even becoming common soon after the seventh century BC and was also turned into the female form Ἀχιλλεία (Achilleía), attested in Attica in the fourth century BC (IG II² 1617) and, in the form Achillia, on a stele in Halicarnassus as the name of a female gladiator fighting an "Amazon".
Achilles' name can be analyzed as a combination of () "distress, pain, sorrow, grief" and () "people, soldiers, nation", resulting in a proto-form *Akhí-lāu̯os "he who has the people distressed" or "he whose people have distress". The grief or distress of the people is a theme raised numerous times in the Iliad (and frequently by Achilles himself). Achilles' role as the hero of grief or distress forms an ironic juxtaposition with the conventional view of him as the hero of ("glory", usually in war). Furthermore, laós has been construed by Gregory Nagy, following Leonard Palmer, to mean "a corps of soldiers", a muster. With this derivation, the name obtains a double meaning in the poem: when the hero is functioning rightly, his men bring distress to the enemy, but when wrongly, his men get the grief of war. The poem is in part about the misdirection of anger on the part of leadership.
Another etymology relates the name to a Proto-Indo-European compound *h₂eḱ-pṓds "sharp foot" which first gave an Illyrian *āk̂pediós, evolving through time into *ākhpdeós and then *akhiddeús. The shift from -dd- to -ll- is then ascribed to the passing of the name into Greek via a Pre-Greek source. The first root part *h₂eḱ- "sharp, pointed" also gave Greek ἀκή (akḗ "point, silence, healing"), ἀκμή (akmḗ "point, edge, zenith") and ὀξύς (oxús "sharp,
"""
print(summarizer(ARTICLE, max_length=500, min_length=200, do_sample=False))
