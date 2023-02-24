---
annotations_creators:
  - no-annotation
language:
  - en
language_creators:
  - machine-generated
license:
  - mit
multilinguality:
  - monolingual
pretty_name: "MT Note Generation"
size_categories:
  - <500
source_datasets:
  - mt_samples
tags:
  - open-assistant
task_categories:
  - conversational
task_ids:
  - dialogue-generation
dataset_info:
  features:
    - name: conversation
      dtype: string
  splits:
    - name: train
      num_bytes: 1060800
      num_examples: 270
    - name: test
      num_bytes: 339323
      num_examples: 90
    - name: validation
      num_bytes: 337018
      num_examples: 90
---

# Dataset Card for MT Samples Clinical Note Generation

## Dataset Description

- **Repository:**
  [Code](https://github.com/LAION-AI/Open-Assistant/data/datasets/mt_note_generation/)

## Dataset Summary

MT Note Generation is a set of synthetic dialogues between Assistant and User
where the user asks the assistant to generate a clinical note for a patient
persona.

This data was created by synthesizing the dialogues in
[MT Samples](https://mtsamples.com/) for clinical note generation.

Example:

```
User: Write a clinical note about a patient with the following chief complaint:  Stomach pain for 2 weeks.

ASSISTANT:

CHIEF COMPLAINT: Stomach pain for 2 weeks. HISTORY OF PRESENT ILLNESS: The patient is a 45yo Mexican man without significant past medical history who presents to the emergency room with complaints of mid-epigastric and right upper quadrant abdominal pain for the last 14 days. The pain was initially crampy and burning in character and was relieved with food intake. He also reports that it initially was associated with a sour taste in his mouth. He went to his primary care physician who prescribed cimetidine 400mg qhs x 5 days; however, this did not relieve his symptoms. In fact, the pain has worsened such that the pain now radiates to the back but is waxing and waning in duration. It is relieved with standing and ambulation and exacerbated when lying in a supine position. He reports a decrease in appetite associated with a 4 lb. wt loss over the last 2 wks. He does have nausea with only one episode of non-bilious, non-bloody emesis on day of admission. He reports a 2 wk history of subjective fever and diaphoresis. He denies any diarrhea, constipation, dysuria, melena, or hematochezia. His last bowel movement was during the morning of admission and was normal. He denies any travel in the last 9 years and sick contacts.PAST MEDICAL HISTORY: Right inguinal groin cyst removal 15 years ago. Unknown etiology. No recurrence.

PAST SURGICAL HISTORY: Left femoral neck fracture with prosthesis secondary to a fall 4 years ago.

FAMILY HISTORY: Mother with diabetes. No history of liver disease. No malignancies.

SOCIAL HISTORY: The patient was born in central Mexico but moved to the United States 9 years ago. He is on disability due to his prior femoral fracture. He denies any tobacco or illicit drug use. He only drinks alcohol socially, no more than 1 drink every few weeks. He is married and has 3 healthy children. He denies any tattoos or risky sexual behavior.

ALLERGIES: NKDA.

MEDICATIONS: Tylenol prn (1-2 tabs every other day for the last 2 wks), Cimetidine 400mg po qhs x 5 days.

REVIEW OF SYSTEMS:  No headache, vision changes. No shortness of breath. No chest pain or palpitations.

PHYSICAL EXAMINATION: Vitals: T 100.9-102.7 BP 136/86 Pulse 117 RR 12 98% sat on room air,Gen: Well-developed, well-nourished, no apparent distress.HEENT: Pupils equal, round and reactive to light. Anicteric. Oropharynx clear and moist.Neck: Supple. No lymphadenopathy or carotid bruits. No thyromegaly or masses.CHEST: Clear to auscultation bilaterally.CV: Tachycardic but regular rhythm, normal S1/S2, no murmurs/rubs/gallops.Abd: Soft, active bowel sounds. Tender in the epigastrium and right upper quadrant with palpation associated with slight guarding. No rebound tenderness. No hepatomegaly. No splenomegaly.Rectal: Stool was brown and guaiac negative.Ext: No cyanosis/clubbing/edema.Neurological: He was alert and oriented x3. CN II-XII intact. Normal 2+ DTRs. No focal neurological deficit.Skin: No jaundice. No skin rashes or lesions.

IMAGING DATA:CT Abdomen with contrast ( 11/29/03 ):  There is a 6x6 cm multilobular hypodense mass seen at the level of the hepatic hilum and caudate lobe which is resulting in mass effect with dilatation of the intrahepatic radicals of the left lobe of the liver. The rest of the liver parenchyma is homogeneous. The gallbladder, pancreas, spleen, adrenal glands and kidneys are within normal limits. The retroperitoneal vascular structures are within normal limits. There is no evidence of lymphadenopathy, free fluid or fluid collections.HOSPITAL COURSE:  The patient was admitted to the hospital for further evaluation. A diagnostic procedure was performed.
```

## Usage

The dataset contains one configuration, `dialogue_modeling`, which has a single
text `conversation` feature.

## Source data

The script modifies data from mtsamples.csv which is hosted in Kaggle:
https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions

## Citation

Please cite our work if you find the resources in this repository useful:

```
@article{pruks2023mtsamplesnotegen,
  author    = {Yada Pruksachatkun},
  title     = {MT Samples Note Generation},
  year      = {2023}
}
```
