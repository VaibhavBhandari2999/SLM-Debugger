# src/model_utils.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

def get_qwen_model():
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.float16)
    return tokenizer, model

def get_summary_model():
    summary_model_id = "Qwen/Qwen2.5-7B-Instruct"
    summary_tokenizer = AutoTokenizer.from_pretrained(summary_model_id)
    summary_model = AutoModelForCausalLM.from_pretrained(summary_model_id).to("cuda:0")
    return summary_tokenizer, summary_model

def get_semantic_model():
    return SentenceTransformer('all-MiniLM-L6-v2')