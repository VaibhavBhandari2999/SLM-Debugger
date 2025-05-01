# src/model_utils.py - Updated version
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

def get_qwen_model():
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.float16)
    return tokenizer, model

def get_summary_model():
    """
    Initialize a model for summary generation. 
    This function now avoids using vLLM for pooling models, using HuggingFace's transformers instead.
    """
    try:
        # Direct HuggingFace transformers approach (avoiding vLLM's pooling issue)
        summary_model_id = "Qwen/Qwen2.5-7B-Instruct"
        summary_tokenizer = AutoTokenizer.from_pretrained(summary_model_id)
        summary_model = AutoModelForCausalLM.from_pretrained(
            summary_model_id, 
            device_map="auto", 
            torch_dtype=torch.float16
        )
        print("Using HuggingFace transformers for summary model")
        return summary_tokenizer, summary_model
    except Exception as e:
        print(f"Error initializing HuggingFace model: {e}")
        print("Falling back to CPU model")
        
        # Fall back to CPU if needed
        summary_model_id = "Qwen/Qwen2.5-7B-Instruct" 
        summary_tokenizer = AutoTokenizer.from_pretrained(summary_model_id)
        summary_model = AutoModelForCausalLM.from_pretrained(
            summary_model_id, 
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        return summary_tokenizer, summary_model

def get_semantic_model():
    """
    Get a model for semantic embeddings.
    """
    # Use a smaller model that's less likely to cause issues
    try:
        # Try with a smaller model first
        return SentenceTransformer('paraphrase-MiniLM-L3-v2')
    except Exception as e:
        print(f"Error loading SentenceTransformer: {e}")
        try:
            # Fall back to an even simpler model
            return SentenceTransformer('distilbert-base-nli-mean-tokens')
        except Exception as e:
            print(f"Error loading fallback SentenceTransformer: {e}")
            # If all else fails, return None and let the calling code handle it
            return None
