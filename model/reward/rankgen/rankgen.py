import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, T5Tokenizer, T5EncoderModel, AutoModel
from omegaconf import DictConfig
from typing import Literal
import tqdm

class RankGenEncoder():
    def __init__(self, config: DictConfig):
        self.rankgen_hf_hub = config.rankgen_hf_path
        self.max_batch_size = config.max_batch_size
        self.cache_dir = config.cache_dir
        self.eval_mode = config.eval_mode
        
        assert self.rankgen_hf_hub in ["kalpeshk2011/rankgen-t5-xl-all", 
                                       "kalpeshk2011/rankgen-t5-xl-pg19", 
                                       "kalpeshk2011/rankgen-t5-base-all", 
                                       "kalpeshk2011/rankgen-t5-large-all"]
        if "large" in self.rankgen_hf_hub:
            self.tokenizer_hf_hub = f"google/t5-v1_1-large"
        elif "xl" in self.rankgen_hf_hub:
            self.tokenizer_hf_hub = f"google/t5-v1_1-xl"
        else:
            self.tokenizer_hf_hub = f"google/t5-v1_1-base"
            
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self.tokenizer = T5Tokenizer.from_pretrained(self.tokenizer_hf_hub, cache_dir=self.cache_dir)
        self.model = AutoModel.from_pretrained(self.rankgen_hf_hub, trust_remote_code=True)
        self.model.to(self.device)
        if self.eval_mode:
            self.model.eval()

    def encode(self, inputs: list[str], vectors_type="prefix", verbose=False, return_input_ids=False):
        tokenizer = self.tokenizer
        max_batch_size = self.max_batch_size
        
        if vectors_type == 'prefix':
            inputs = ['pre ' + input for input in inputs]
            max_length = 512
        else:
            inputs = ['suffi ' + input for input in inputs]
            max_length = 128

        all_embeddings = []
        all_input_ids = []
        for i in tqdm.tqdm(range(0, len(inputs), max_batch_size), total=(len(inputs) // max_batch_size) + 1, disable=not verbose, desc=f"Encoding {vectors_type} inputs:"):
            tokenized_inputs = tokenizer(inputs[i:i + max_batch_size], return_tensors="pt", padding=True)
            
            for k, v in tokenized_inputs.items():
                tokenized_inputs[k] = v[:, :max_length]
            tokenized_inputs = tokenized_inputs.to(self.device)
            
            if self.eval_mode:
                with torch.inference_mode():
                    batch_embeddings = self.model(**tokenized_inputs)
            else:
                batch_embeddings = self.model(**tokenized_inputs)
                
            all_embeddings.append(batch_embeddings)
            if return_input_ids:
                all_input_ids.extend(tokenized_inputs.input_ids.cpu().tolist())
        return {
            "embeddings": torch.cat(all_embeddings, dim=0),
            "input_ids": all_input_ids
        }
        
        def state_dict(self):
            pass
            
        def load_state_dict(self):
            pass


class RankGenScorer():
    def __init__(self, config: DictConfig):
        self.rankgen_encoder = RankGenEncoder(config)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def score(self, prefix, suffixes, prefix_vector=None):
        rankgen_model = self.rankgen_encoder
        if prefix_vector is None:
            prefix_vector = rankgen_model.encode(prefix, vectors_type="prefix")["embeddings"]
        suffix_vectors = rankgen_model.encode(suffixes, vectors_type="suffix")["embeddings"]
        similarities = torch.matmul(prefix_vector, suffix_vectors.t()).squeeze(dim=0)
        return similarities, prefix_vector, suffix_vectors