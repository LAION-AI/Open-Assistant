---
dataset_info:
  features:
    - name: INSTRUCTION
      dtype: string
    - name: RESPONSE
      dtype: string
    - name: SOURCE
      dtype: string
    - name: METADATA
      struct:
        - name: answer_score
          dtype: int64
        - name: question_score
          dtype: int64
        - name: tags
          dtype: string
  splits:
    - name: train
      num_bytes: 6549838664
      num_examples: 6331083
  download_size: 3755782987
  dataset_size: 6549838664
license: cc-by-sa-4.0
language:
  - en
  - uk
  - ru
  - de
  - fr
  - it
  - es
pretty_name: Open-Assistant StackExchange Instruction
---

# Stackexchange Instructions for OpenAssistant

This dataset is taken from https://archive.org/details/stackexchange.

There's a single parquet file combining all stackexchange sites. The threads
have been filtered as follows: only threads with an accepted answer, for which
both the question and response is less than 1000 characters have been chosen.
Other answers, or questions without accepted answers, or long entries have been
dropped.

Each row consists of

- INSTRUCTION
- RESPONSE
- SOURCE («stackexchange-ai«)
- METADATA (tags, question_score, answer_score).

Original extraction code by https://github.com/b-mc2

## How to Reproduce this Dataset

1. Download all XML files from the stackexchange archive into the xml/ folder

```
./download.py
```

2. Process the XML, filter conversations and convert to OA format into parquet/
   folder

```
./process.py
```

3. Run stats on all files in the parquet/ folder

```
./stats.py
```

4. Combine all parquet files into one large stackexchange.parquet file

```
./combine.py
```

5. Upload to huggingface hub, you'll first need use huggingface-cli login

```
./upload.py
```

## Statistics

- 3dprinting: 1,006
- academia: 6,956
- ai: 1,169
- android: 11,591
- anime: 3,688
- apple: 32,603
- arduino: 3,725
- askubuntu: 78,472
- astronomy: 2,425
- aviation: 4,945
- avp: 1,949
- beer: 387
- bicycles: 4,835
- bioacoustics: 70
- bioinformatics: 903
- biology: 5,344
- bitcoin: 7,456
- blender: 25,527
- boardgames: 4,538
- bricks: 1,457
- buddhism: 911
- cardano: 670
- chemistry: 7,430
- chess: 2,185
- chinese: 4,897
- christianity: 1,248
- civicrm: 3,221
- codegolf: 943
- codereview: 2,171
- coffee: 350
- cogsci: 645
- computergraphics: 540
- conlang: 101
- cooking: 7,951
- craftcms: 4,533
- crafts: 438
- crypto: 4,425
- cs: 9,478
- cseducators: 71
- cstheory: 2,196
- datascience: 5,045
- dba: 16,850
- devops: 961
- diy: 14,400
- drones: 190
- drupal: 24,090
- dsp: 4,470
- earthscience: 922
- ebooks: 323
- economics: 2,120
- electronics: 41,717
- elementaryos: 1,769
- ell: 30,428
- emacs: 7,140
- engineering: 2,314
- english: 42,415
- eosio: 626
- es_stackoverflow: 21,475
- esperanto: 617
- ethereum: 9,603
- expatriates: 973
- expressionengine: 3,638
- fitness: 1,833
- freelancing: 338
- french: 5,193
- gamedev: 9,678
- gaming: 44,899
- gardening: 4,492
- genealogy: 487
- german: 6,715
- gis: 30,249
- graphicdesign: 10,563
- ham: 790
- hardwarerecs: 647
- health: 804
- hermeneutics: 782
- hinduism: 1,036
- history: 1,776
- homebrew: 2,357
- hsm: 484
- interpersonal: 199
- iot: 331
- iota: 292
- islam: 1,496
- italian: 1,356
- ja_stackoverflow: 9,734
- japanese: 13,862
- joomla: 1,875
- judaism: 6,156
- korean: 754
- languagelearning: 135
- latin: 1,387
- law: 3,475
- lifehacks: 934
- linguistics: 1,507
- literature: 582
- magento: 20,537
- martialarts: 364
- materials: 338
- math: 501,019
- matheducators: 316
- mathematica: 19,529
- mathoverflow_net_7z: 23,803
- mechanics: 4,735
- meta: 34,161
- meta_askubuntu: 2,076
- meta_mathoverflow_net_7z: 333
- meta_serverfault: 823
- meta_stackoverflow: 12,641
- meta_superuser: 1,748
- moderators: 39
- monero: 1,443
- money: 7,996
- movies: 6,789
- music: 5,740
- musicfans: 781
- mythology: 271
- networkengineering: 4,637
- opendata: 1,117
- opensource: 805
- or: 586
- outdoors: 1,503
- parenting: 815
- patents: 582
- pets: 1,081
- philosophy: 1,505
- photo: 6,386
- physics: 35,386
- pm: 982
- poker: 431
- politics: 1,903
- portuguese: 658
- proofassistants: 87
- pt_stackoverflow: 27,650
- puzzling: 11,959
- quant: 3,303
- quantumcomputing: 1,604
- raspberrypi: 6,794
- retrocomputing: 1,016
- reverseengineering: 1,606
- robotics: 1,020
- rpg: 9,517
- ru_stackoverflow: 106,714
- rus: 8,210
- russian: 1,960
- salesforce: 27,962
- scicomp: 1,403
- scifi: 15,174
- security: 11,733
- serverfault: 81,229
- sharepoint: 24,934
- sitecore: 2,691
- skeptics: 1,043
- softwareengineering: 10,526
- softwarerecs: 3,032
- solana: 602
- sound: 2,031
- space: 3,145
- spanish: 3,049
- sports: 1,715
- sqa: 1,944
- stackapps: 702
- stackoverflow: 4,269,779
- stats: 23,102
- stellar: 373
- substrate: 812
- superuser: 128,488
- sustainability: 240
- tex: 42,808
- tezos: 635
- tor: 887
- travel: 9,957
- tridion: 1,769
- ukrainian: 577
- unix: 54,338
- ux: 7,403
- vegetarianism: 151
- vi: 4,360
- webapps: 10,159
- webmasters: 9,413
- windowsphone: 1,110
- woodworking: 677
- wordpress: 24,270
- workplace: 4,104
- worldbuilding: 2,766
- writers: 1,957

---

## license: cc-by-sa-4.0 // See https://archive.org/details/stackexchange for details
