import argparse
import torch
from datasets import load_dataset
from model.model_training.models.patching_utils import load_peft_model
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaForCausalLM, LlamaTokenizer
from matplotlib.pyplot import plt

def load_model_tokenizer(model_name, peft_model=None, **model_args,):
    
    
    if "llama" not in model_name:
        model = AutoModelForCausalLM.from_pretrained(model_name, **model_args)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    else:
        model = LlamaForCausalLM.from_pretrained(model_name, **model_args)
        tokenizer = LlamaTokenizer.from_pretrained(model_name)
    
    if peft_model is not None:
        model = load_peft_model(model, peft_model, tokenizer)
    
    model.eval()
    
    return model, tokenizer


class Perplexity:
    
    def __init___(
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
        
        input_tokens = self.tokenizer.batch_encode_plus(
            dataset,
            truncation="max_length",
            max_length=max_length,
            padding=False,
            return_attention_mask=True,
            return_tensors="pt"

        )
        loss = 0.0
        for i, idx in enumerate(range(0, input_tokens.size(1), self.batch_size)):
            batch_tokens = input_tokens[idx:idx+self.batch_size]
            batch_tokens = tokenizer.pad(
                batch_tokens,
                padding="longest",
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
    parser.add_argument("--datset_split", type=str,default="test", help="dataset split")
    parser.add_argument("--dataset_size", type=int,default=50, help="dataset split")


    parser.add_argument("--max_length", type=int, default=8000, help="Maximum sequence length for the model")
    parser.add_argument("--min_length", type=int,default=100, help="min tokens")
    parser.add_argument("--stride", type=int, default=100, help="Stride for data chunks")
    parser.add_argument("--bit", type=int,default=16, help="Model inference type")
    parser.add_argument("--peft_model", type=str, help="model path of peft model")
    parser.add_argument("--device", type=str,default="cuda", help="GPU DEVICE")
    parser.add_argument("--device_index", type=str,default="0", help="GPU DEVICE Index")


    args = parser.parse_args().__dict__
    perplexity_dict  = {}
    device = torch.device(args.device, args.device_index)
    max_length = args.get("max_length")
    
    model_args = {}
    bits = args.get("bits")
    if bits == 8:
        model_args.update({"load_in_8_bit":True})
    elif bits == 16:
        model_args.update({"torch_dtype":torch.float16})
        
    
    model, tokenizer = load_model_tokenizer(args.get("model_name"),args.get("peft_model"), **model_args)
    model.to(device)
    
    perplexity = Perplexity(model, tokenizer)
    
    dataset = load_dataset("tau/scrolls", name = args.get("dataset"), split=args.get("dataset_split"))
    if "input" not in dataset.features.keys():
        raise KeyError("column input not in dataset")
    input_text = [item["input"] for item in dataset]
    subset_indices = [idx for idx, item in enumerate(input_text) if len(item.split)>=max_length][:args.get("dataset_size")]
    input_text = [input_text[idx] for idx in subset_indices]
    
    
    for max_len in range(0, max_length, args.get("stride")):
        
        # measure perplexity 
        score = perplexity.compute(input_text, max_len)
        perplexity_dict.update({max_len:score})
        
    
    fig = plt.plot(perplexity.keys(), perplexity_dict.values(),".-")
    plt.xlabel("Number of tokens")
    plt.ylabel("Perplexity")
    plt.savefig("perplexity.png")
        
        
    
    

