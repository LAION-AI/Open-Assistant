---
dataset_info:
  features:
    - name: TEXT
      dtype: string
    - name: METADATA
      dtype: string
    - name: SOURCE
      dtype: string
  splits:
    - name: train
      num_bytes: 168860477
      num_examples: 5328
  download_size: 96479923
  dataset_size: 168860477
license: mit
task_categories:
  - conversational
  - text2text-generation
  - text-generation
language:
  - en
tags:
  - OpenAssistant
  - transcripts
  - subtitles
  - television
  - foreverdreaming
pretty_name: TV and Movie dialogue and transcript corpus from ForeverDreaming
size_categories:
  - 1K<n<10K
---

# Dataset Card for "fd_dialogue"

This dataset contains transcripts for famous movies and TV shows from
https://transcripts.foreverdreaming.org/ (the crawler notebooks are not included
with the dataset).

The dataset contains **only a small portion of Forever Dreaming's data**, as
only transcripts with a clear dialogue format are included, such as:

```
PERSON 1: Hello
PERSON 2: Hello Person 2!

(they are both talking)

Something else happens

PERSON 1: What happened?
```

Each row in the dataset is a single TV episode or movie. (**5381** rows total)
following the [OpenAssistant](https://open-assistant.io/) format. The METADATA
column contains _type_ (movie or series), _show_ and the _episode_ ("" for
movies) keys and string values as a JSON string.

| Show                                    | Count |
| --------------------------------------- | ----- |
| A Discovery of Witches                  | 6     |
| Agents of S.H.I.E.L.D.                  | 9     |
| Alias                                   | 102   |
| Angel                                   | 64    |
| Bones                                   | 114   |
| Boy Meets World                         | 24    |
| Breaking Bad                            | 27    |
| Brooklyn Nine-Nine                      | 8     |
| Buffy the Vampire Slayer                | 113   |
| CSI: Crime Scene Investigation          | 164   |
| Charmed                                 | 176   |
| Children/Disney                         | 4     |
| Childrens Hospital                      | 18    |
| Christmas & New Year's                  | 10    |
| Chuck                                   | 17    |
| Crossing Jordan                         | 23    |
| Dawson's Creek                          | 128   |
| Degrassi Next Generation                | 113   |
| Doctor Who                              | 699   |
| Doctor Who Special                      | 21    |
| Doctor Who\_                            | 108   |
| Downton Abbey                           | 18    |
| Dragon Ball Z Kai                       | 57    |
| FRIENDS                                 | 227   |
| Foyle's War                             | 28    |
| Friday Night Lights                     | 7     |
| Game of Thrones                         | 6     |
| Gilmore Girls                           | 149   |
| Gintama                                 | 41    |
| Glee                                    | 11    |
| Gossip Girl                             | 5     |
| Greek                                   | 33    |
| Grey's Anatomy                          | 75    |
| Growing Pains                           | 116   |
| Hannibal                                | 4     |
| Heartland                               | 3     |
| Hell on Wheels                          | 3     |
| House                                   | 153   |
| How I Met Your Mother                   | 133   |
| JoJo's Bizarre Adventure                | 42    |
| Justified                               | 46    |
| Keeping Up With the Kardashians         | 8     |
| Lego Ninjago: Masters of Spinjitzu      | 12    |
| London Spy                              | 5     |
| Lost                                    | 117   |
| Lucifer                                 | 3     |
| Married                                 | 9     |
| Mars                                    | 6     |
| Merlin                                  | 58    |
| My Little Pony: Friendship is Magic     | 15    |
| NCIS                                    | 91    |
| New Girl                                | 3     |
| Once Upon A Time                        | 79    |
| One Tree Hill                           | 163   |
| Open Heart                              | 8     |
| Pretty Little Liars                     | 4     |
| Prison Break                            | 23    |
| Queer As Folk                           | 38    |
| Reign                                   | 9     |
| Roswell                                 | 60    |
| Salem                                   | 23    |
| Scandal                                 | 7     |
| Schitt's Creek                          | 4     |
| Scrubs                                  | 29    |
| Sequels/Trilogies/Sagas                 | 9     |
| Sex and the City                        | 4     |
| Sherlock                                | 8     |
| Skins                                   | 20    |
| Smallville                              | 190   |
| Sons of Anarchy                         | 55    |
| South Park                              | 84    |
| Spy × Family                            | 12    |
| StarTalk                                | 6     |
| Sugar Apple Fairy Tale                  | 5     |
| Superhero's                             | 3     |
| Supernatural                            | 114   |
| Teen Wolf                               | 58    |
| That Time I Got Reincarnated As A Slime | 22    |
| The 100                                 | 3     |
| The 4400                                | 16    |
| The Amazing World of Gumball            | 4     |
| The Big Bang Theory                     | 183   |
| The L Word                              | 3     |
| The Mentalist                           | 38    |
| The Nanny                               | 8     |
| The O.C.                                | 92    |
| The Office                              | 195   |
| The Originals                           | 45    |
| The Secret Life of an American Teenager | 18    |
| The Simpsons                            | 14    |
| The Vampire Diaries                     | 121   |
| The Walking Dead                        | 12    |
| The X-Files                             | 3     |
| Torchwood                               | 31    |
| Trailer Park Boys                       | 10    |
| True Blood                              | 33    |
| Tyrant                                  | 6     |
| Valentine/Romance                       | 4     |
| Veronica Mars                           | 59    |
| Vikings                                 | 7     |

An additional 36 movies with transcripts are also included:

```
Pokémon the Movie: Hoopa and the Clash of Ages (2015)
Frozen (2013)
Home Alone
Lego Batman Movie, The (2017)
Disenchanted ( 2022)
Nightmare Before Christmas, The
Goonies, The (1985)
Polar Express, The (2004)
Frosty the Snowman (1969)
The Truth About Christmas (2018)
A Miser Brothers' Christmas (2008)
Powerpuff Girls: 'Twas the Fight Before Christmas, The (2003)
Tis the Season (2015)
Jingle Hell (2000)
Corpse Party: Book of Shadows (2016)
Mummy, The (1999)
Knock Knock (2015)
Dungeons and Dragons , Honour among thieves ( 2023)
w*r of the Worlds (2005)
Harry Potter and the Sorcerer's Stone
Twilight Saga, The: Breaking Dawn Part 2
Twilight Saga, The: Breaking Dawn Part 1
Twilight Saga, The: Eclipse
Godfather, The (1972)
Transformers (2007)
Creed 3 (2023)
Creed (2015)
Lethal w*apon 3 (1992)
Spider-Man 2 (2004)
Spider-Man: No Way Home (2021)
Black Panther Wakanda Forever ( 2022)
Money Train (1995)
Happys, The (2016)
Paris, Wine and Romance (2019)
Angel Guts: Red p*rn (1981)
Butterfly Crush (2010)
```

Note that there could be overlaps with the
[TV dialogue dataset](https://huggingface.co/datasets/sedthh/tv_dialogue) for
Friends, The Office, Doctor Who, South Park and some movies.
