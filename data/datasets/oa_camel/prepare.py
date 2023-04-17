# This program prepares Camel datasets to the Open Assistant format.

import pandas as pd
from datasets import load_dataset
import json

# Load the datasets from Hugging Face
datasets = [
  'camel-ai/biology', 'camel-ai/physics', 'camel-ai/chemistry', 'camel-ai/math'
]

transformed_data = []

# Loop through each dataset and process it
for dataset_id in datasets:
  dataset = load_dataset(dataset_id)
  for entry in dataset['train']:
    metadata = {'Topic': entry['topic;'], 'Sub-Topic': entry['sub_topic']}
    transformed_entry = {
      'INSTRUCTION': entry['message_1'],
      'RESPONSE': entry['message_2'],
      'SOURCE': dataset_id,
      'METADATA': json.dumps(metadata)
    }
    transformed_data.append(transformed_entry)

# Combine the results into a single DataFrame
df = pd.DataFrame(transformed_data)

# Save the DataFrame to disk in the Parquet format
df.to_parquet('output.parquet', row_group_size=100)

# Print the amount of entries in the final converted dataset
print(f'Converted {len(df)} entries')