from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import GPTJForCausalLM, AutoTokenizer
import torch
torch.cuda.empty_cache()
# tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")……
# model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-j-6B")

print(f"torch.cuda.is_available() = {torch.cuda.is_available()}")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(torch.cuda.memory_summary(device=None, abbreviated=False))


model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", low_cpu_mem_usage=True)
model.to(device)
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")

prompt = "The Belgian national football team "
input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

generated_ids = model.generate(input_ids, do_sample=True, temperature=0.9, max_length=200)
generated_text = tokenizer.decode(generated_ids[0])
print(generated_text)
