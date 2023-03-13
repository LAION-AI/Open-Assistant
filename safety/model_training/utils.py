def add_special_tokens(special_tokens, tokenizer, model):
    for key, value in special_tokens.items():
        setattr(tokenizer, key, value)
        tokenizer.add_tokens([value])
        setattr(tokenizer, key + "_id", tokenizer.encode(value)[0])

    model.resize_token_embeddings(len(tokenizer))
