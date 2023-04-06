### Dataset Summary

This dataset contains 4803 question/answer pairs extracted from the [BioStars](https://www.biostars.org/) website. The site focuses on bioinformatics, computational genomics, and biological data analysis.

# Dataset Location and Details
https://huggingface.co/datasets/cannin/biostars_qa

# Code Details 
* get_biostars_dataset.py: This script downloads the content from [Biostars API](https://www.biostars.org/info/api/); each post is downloaded as an individual JSON file
* extract_accepted_data.py: This script loads the individual files to Pandas then extracts out question/answer pairs. Questions were included if they were an accepted answer and the question had at least 1 vote. The content is then formatted as a Apache Parquet dataset with columns: INSTRUCTION, RESPONSE, SOURCE, METADATA

