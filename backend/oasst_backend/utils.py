import requests

def get_detoxify_classification(inputs, hf_token):
  API_URL = "https://api-inference.huggingface.co/models/unitary/multilingual-toxic-xlm-roberta"
  headers = {"Authorization": f'Bearer {hf_token}'}
  payload = {"inputs": inputs}
  response = requests.post(API_URL, headers=headers, json=payload)
  return response.json()