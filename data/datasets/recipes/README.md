# Recipes dialogue datasets

Here we convert several existing recipe ingredient and instructions datasets
into dialogue. Each notebook processes a different dataset and creates a final
dataset to be uploaded to huggingface.

## tasty_recipes.ipynb

Takes this Kaggle dataset 'Recipes from Tasty'
https://www.kaggle.com/datasets/zeeenb/recipes-from-tasty?select=ingredient_and_instructions.json,
filters for the top 1,000 highest rated recipes, and turns them into basic
dialogue using a preset list of user prompt tempaltes.

### Some ideas for extending this dataset

This dataset is nicely structured, and the ingredients section includes the
quantities and units separated out. Some, but not all already include a
primary_unit (US) and metric_unit. We could find all recipes with both units and
generate dialogue for the prompt 'convert the ingredients into metric', 'what
are the ingredients in UK measurments'? etc..
