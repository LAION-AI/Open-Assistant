# Automatically generate Q & A pairs from the WikiData graph

The goal of this notebook is to help users generate questions and answer prompt
pairs by generating a few plausible ones based on the information publicly
available in the network of the WikiData graphs.

NOTE: the method is **limited** and manual review of each generated question and
answer pair is necessary!

A step-by-step guide:

1. Create a WikiGraph crawler instance and define a cache file to avoide
   redownloading nodes (only English is supported at the moment)

```Python
wg = WikiGraph("cache.csv")
```

2. Think of a concept and search for its identifier

```Python
wg.search("chatgpt")

>>> [{'id': 'Q115564437',
  'label': 'ChatGPT',
  'description': 'language model optimized for dialogue'},
 {'id': 'Q116488506',
  'label': 'ChatGPT is fun, but not an author',
  'description': ''},
 {'id': 'Q116294278',
  'label': 'ChatGPT listed as author on research papers: many scientists disapprove',
  'description': ''}]
```

3. Generate Q & A pairs for selected ID (a TQDM bar will show up the first time
   while downloading the graph elements), note that the results will be
   different due to randomness

```Python
print(wg.generate("Q115564437"))

>>> Questions and Answers on ChatGPT (also known as GPT-3.5, Generative Pre-trained Transformer):

Q: What is the offical website for Generative Pre-trained Transformer?
A: Its web address is: https://chat.openai.com/chat

Q: What's ChatGPT's license?
A: ChatGPT has the following license: proprietary license.

...
```

The generate() function will generate a single question and answer pair for ALL
defined nodes in the class, rerunning it will only change the order and the
wording of these prompts!

As you can see, the wording is a bit clunky, and "website for [the]" is missing,
but it's still a good first draft to work with.

4. Caveats

Pass "pronoun" argument when the concept is an actual person:

```Python
print(wg.generate("Q5284", pronoun="he")) # bill gates

Q: Who are his brothers and sisters?
A: Bill Gates has 2 siblings: Kristianne Gates and Libby Gates MacPhee.
```

Pass "proper = False" if the concept isn't a proper noun:

```Python
print(wg.generate("Q6663", proper=False)) # hamburger

Q: What are the ingredients of the hamburger?
A: The ingredients of the hamburger are patty, cheese, bread, lettuce, tomato and onion.
```

Pass "zalgo = True" to add random typos to the questions to simulate messy user
feedback (all lowercase, all caps, multiple questionmarks, missing characters,
switched characters, etc.):

```Python
print(wg.generate("Q1781", zalgo=True)) # budapest

Q: WHAT ARE ITS COORDINATES?
A: Its GPS location is 47.498333333333 19.040833333333.
```

NOTE: since the NODEs can encode multiple meanings, the generated questions and
answer can often be off. For instance the _start time (P580)_ node can mean
"from, starting, began, from time, since, from date, building date, starttime,
introduced, introduction, started in, beginning, join date, join time, start
date, joined" which can result in weird sentences like:

```Python
Q: When did the hamburger start?
A: The hamburger first started at 1758.
```
