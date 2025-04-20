import torch
from vllm import LLM, SamplingParams

def get_summary_model(num_gpus=None):
    """Initialize the vLLM model for generating summaries on multiple GPUs."""
    # Get the number of available GPUs if not specified
    if num_gpus is None:
        num_gpus = torch.cuda.device_count()
    
    print(f"Initializing model with {num_gpus} GPUs")
    
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    # Use vLLM with tensor parallelism across multiple GPUs
    model = LLM(
        model=model_id,
        tensor_parallel_size=num_gpus,  # Use all available GPUs
        trust_remote_code=True,  # Required for some models like Qwen
        dtype="half",  # Use half precision for efficiency
        gpu_memory_utilization=0.8,  # Prevent OOM errors
        # Enable swap space for handling larger models
        swap_space=4,  # GB, adjust based on available RAM
    )
    return model