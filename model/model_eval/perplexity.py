import argparse
import torch
from datasets import load_dataset
from model.model_training.models.peft_modeling import load_peft_model
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaForCausalLM, LlamaTokenizer
import matplotlib.pyplot as plt
from typing import List 
import json
from tqdm import tqdm

def load_model_tokenizer(model_name, peft_model=None, **model_args,):
    
    
    if "llama" not in model_name:
        model = AutoModelForCausalLM.from_pretrained(model_name, **model_args)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    else:
        model = LlamaForCausalLM.from_pretrained(model_name, **model_args)
        tokenizer = LlamaTokenizer.from_pretrained(model_name)
    
    if peft_model is not None:
        print("PEFT NOW")
        model = load_peft_model(model, peft_model, tokenizer)
    
    model.eval()
    
    return model, tokenizer


class Perplexity:
    
    def __init__(
        self,
        model,
        tokenizer,
        batch_size=16,
    ):
        self.model = model
        self.tokenizer = tokenizer 
        self.batch_size = batch_size
        self.device = self.model.device
    
        
    
    def compute(
        self,
        dataset:List[str],
        max_length:int,
        
    ):
        
        input_tokens = self.tokenizer(
            dataset,
            truncation=True,
            max_length=max_length,
            padding=False,
            return_attention_mask=True,
        )
        
        loss = 0.0
        for i, idx in enumerate(range(0, len(input_tokens.input_ids), self.batch_size)):
            batch_tokens = {key:input_tokens[key][idx:idx+self.batch_size] for key in input_tokens.keys()}
            batch_tokens = tokenizer.pad(
                batch_tokens,
                padding="longest",
                return_attention_mask=True,
                return_tensors="pt",
            ).to(self.device)
            labels = batch_tokens["input_ids"].clone()
            batch_tokens["labels"] = torch.where(labels==self.tokenizer.pad_token_id, -100, labels)
            with torch.no_grad():
                loss += torch.exp(self.model(**batch_tokens).loss)
                
                
        return loss/i 
    
                
        
        
        
        
    


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--model_name", type=str, help="Model url or filepath")
    parser.add_argument("--dataset", type=str,default="gov_report", help="dataset subset for scrolls")
    parser.add_argument("--dataset_split", type=str,default="test", help="dataset split")
    parser.add_argument("--dataset_size", type=int,default=50, help="dataset split")


    parser.add_argument("--max_length", type=int, default=8000, help="Maximum sequence length for the model")
    parser.add_argument("--min_length", type=int,default=100, help="min tokens")
    parser.add_argument("--stride", type=int, default=100, help="Stride for data chunks")
    parser.add_argument("--bit", type=int,default=16, help="Model inference type")
    parser.add_argument("--peft_model", type=str, help="model path of peft model")
    parser.add_argument("--device", type=str,default="cuda", help="GPU DEVICE")
    parser.add_argument("--device_index", type=int,default=0, help="GPU DEVICE Index")
    parser.add_argument("--batch_size", type=int,default=4, help="GPU  batch size")


    args = parser.parse_args().__dict__
    perplexity_dict  = {}
    device = torch.device(args["device"], args["device_index"])
    max_length = args.get("max_length")
    
    
    dataset = load_dataset("tau/scrolls", name = args.get("dataset"), split=args.get("dataset_split"))
    if "input" not in dataset.features.keys():
        raise KeyError("column input not in dataset")
    input_text = [item["input"] for item in dataset]
    subset_indices = [idx for idx, item in enumerate(input_text) if len(item.split())>=max_length][:args.get("dataset_size")]
    input_text = [input_text[idx] for idx in subset_indices]
    
    model_args = {}
    bits = args.get("bits")
    if bits == 8:
        model_args.update({"load_in_8_bit":True})
    elif bits == 16:
        model_args.update({"torch_dtype":torch.float16})
        
        
    model, tokenizer = load_model_tokenizer(args.get("model_name"),args.get("peft_model"), **model_args)
    model.to(device)
    
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        model.resize_token_embeddings(len(tokenizer))
    
    perplexity = Perplexity(model, tokenizer, args.get("batch_size"))
    

    
    
    for max_len in tqdm(range(100, max_length, args.get("stride"))):
        
        try:
            # measure perplexity 
            score = perplexity.compute(input_text, max_len)
            perplexity_dict.update({max_len:score.item()})
        except Exception as e:
            print(e)
          
    filename = args.get("model_name").split('/')[-1]  
    with open(f"{filename}-perplexity.json", "w") as file:
        json.dump(perplexity_dict, file, indent=4)
    fig = plt.plot(perplexity_dict.keys(), perplexity_dict.values(),".-")
    plt.xlabel("Number of tokens")
    plt.ylabel("Perplexity")
    plt.savefig(f"{filename}.png")
        
        
    
    

