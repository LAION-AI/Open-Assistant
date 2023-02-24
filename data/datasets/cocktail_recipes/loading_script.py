from datasets import load_dataset

if __name__ == "__main__":
    ds = load_dataset("brianarbuckle/cocktail_recipes")
    print(ds["train"])
