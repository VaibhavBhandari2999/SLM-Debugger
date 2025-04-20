from vllm import LLM, SamplingParams
import ast
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os
import torch
from common import get_summary_model

def extract_module_docstring(llm_output):
    """Extract the docstring from the LLM output."""
    # Clean up and extract the relevant part of the output
    if '"""' in llm_output:
        # If triple quotes are in the output, use them as delimiters
        start_idx = llm_output.find('"""')
        if start_idx >= 0:
            content = llm_output[start_idx+3:]
            end_idx = content.find('"""')
            if end_idx >= 0:
                return '"""' + content[:end_idx] + '"""'
            else:
                return '"""' + content.strip() + '"""'
    
    # If we reached here, no proper docstring format was found
    # Format it properly as a docstring
    cleaned_output = llm_output.strip()
    if "### Summary:" in cleaned_output:
        # Extract just the summary part
        cleaned_output = cleaned_output.split("### Summary:", 1)[1].strip()
    
    # Format as proper docstring
    return f'"""{cleaned_output}"""'

def create_module_prompt(file_path, content):
    """Create a prompt for module summary generation."""
    return f"""Below is the complete source code of a Python file.

Your task is to read the file and generate a concise and informative docstring that describes:
- The overall purpose of the file
- The main classes and functions it defines
- Key responsibilities or logic handled in this file
- How the classes and functions interact (if applicable)

Be concise, but include technical details where useful.

### Python File: {file_path}
{content}

### Summary:
"""

def has_module_docstring(file_path):
    """Check if a file already has a module-level docstring."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
            return ast.get_docstring(tree) is not None
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def insert_module_docstring(file_path, docstring):
    """Insert the generated docstring at the beginning of the file."""
    try:
        # Make sure the docstring doesn't have the triple quotes already
        if docstring.startswith('"""') and docstring.endswith('"""'):
            clean_docstring = docstring
        else:
            clean_docstring = f'"""{docstring}"""'
        
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        # Write the docstring at the beginning of the file followed by the original content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{clean_docstring}\n\n{original_content}")
        
        print(f"Successfully inserted module docstring in {file_path}")
        return True
    except Exception as e:
        print(f"Error inserting docstring in {file_path}: {e}")
        return False

def batch_generate_module_summaries(file_details, model):
    """Generate summaries for a batch of modules using vLLM."""
    # Create prompts for all files in this batch
    prompts = []
    valid_files = []
    
    for file_info in file_details:
        try:
            # Create the prompt for this file
            prompts.append(create_module_prompt(file_info['path'], file_info['content']))
            valid_files.append(file_info)
        except Exception as e:
            print(f"Error creating prompt for {file_info.get('path', 'unknown')}: {e}")
    
    # Configure sampling parameters
    sampling_params = SamplingParams(
        temperature=0.2,
        max_tokens=300,
        top_k=50,
    )
    
    # Use vLLM to generate all outputs at once
    outputs = model.generate(prompts, sampling_params)
    
    # Process the results
    results = []
    for i, output in enumerate(outputs):
        generated = output.outputs[0].text
        extracted = extract_module_docstring(generated)
        results.append((valid_files[i], extracted))
    
    return results

def process_files_for_module_docstrings(repo_details, output_dir="summary", n=10):
    """Process all files to generate and insert module-level docstrings."""
    # Initialize the model with multiple GPUs
    model = get_summary_model()
    
    # Adjust batch size based on GPU count
    num_gpus_available = torch.cuda.device_count()
    adjusted_batch_size = batch_size * max(1, num_gpus_available)
    print(f"Using adjusted batch size: {adjusted_batch_size} based on {num_gpus_available} GPUs")
    
    # Collect all files that need module docstrings
    files_to_process = []
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Iterate through each repo
    for repo_id, entry in repo_details.items():
        repo_with_underscore = entry["repo_with_underscore"]
        file_list = entry["top_n_files"]
        
        # Process each file in the repo
        for file_path in file_list:
            if not file_path.endswith(".py"):
                continue
                
            # Full path to the file
            full_path = f"decoupled_top_files_{n}/{repo_with_underscore}/{file_path}"
            output_path = f"{output_dir}/{repo_with_underscore}/{file_path}"
            
            # Skip if output directory doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if the file already has a module docstring
            if has_module_docstring(full_path):
                print(f"Skipping {file_path} - already has module docstring")
                continue
                
            try:
                # Read the file content
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Add to the list of files to process
                files_to_process.append({
                    'repo_id': repo_id,
                    'repo': repo_with_underscore,
                    'path': file_path,
                    'full_path': full_path,
                    'output_path': output_path,
                    'content': content
                })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    print(f"Found {len(files_to_process)} files needing module docstrings")
    
    # Process in batches
    all_results = []
    batches = [files_to_process[i:i+adjusted_batch_size] for i in range(0, len(files_to_process), adjusted_batch_size)]
    
    for batch_idx, batch in enumerate(tqdm(batches, desc="Generating module docstrings")):
        print(f"\nProcessing batch {batch_idx+1}/{len(batches)} with {len(batch)} files")
        
        try:
            batch_results = batch_generate_module_summaries(batch, model)
            all_results.extend(batch_results)
        except Exception as e:
            print(f"Error processing batch {batch_idx+1}: {str(e)}")
            # Process one by one as fallback
            for file_info in batch:
                try:
                    single_result = process_single_file(file_info, model)
                    if single_result:
                        all_results.append(single_result)
                except Exception as e2:
                    print(f"Failed to process {file_info['path']} individually: {str(e2)}")
    
    # Calculate CPU worker count based on system
    import multiprocessing
    cpu_workers = min(8, multiprocessing.cpu_count())
    
    # Insert docstrings in parallel
    if all_results:
        print(f"\nInserting {len(all_results)} module docstrings")
        with ThreadPoolExecutor(max_workers=cpu_workers) as executor:
            futures = []
            for file_info, docstring in all_results:
                # First copy the file to the output directory if needed
                src_path = file_info['full_path']
                dest_path = file_info['output_path']
                
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                if src_path != dest_path:
                    with open(src_path, "r", encoding="utf-8") as src, open(dest_path, "w", encoding="utf-8") as dest:
                        dest.write(src.read())
                
                # Submit the job to insert the docstring
                futures.append(
                    executor.submit(insert_module_docstring, dest_path, docstring)
                )
            
            # Wait for all file operations to complete with progress bar
            completed = 0
            for future in tqdm(futures, desc="Inserting docstrings"):
                try:
                    if future.result():  # This will block until the future is done
                        completed += 1
                except Exception as e:
                    print(f"Error during file operation: {e}")
            
            print(f"Successfully inserted {completed} module docstrings out of {len(futures)} attempted")
    else:
        print("No results to insert!")

def process_single_file(file_info, model):
    """Process a single file for debugging purposes."""
    print(f"Processing single file: {file_info['path']}")
    
    try:
        prompt = create_module_prompt(file_info['path'], file_info['content'])
        sampling_params = SamplingParams(
            temperature=0.2,
            max_tokens=300,
        )
        
        outputs = model.generate([prompt], sampling_params)
        generated = outputs[0].outputs[0].text
        extracted = extract_module_docstring(generated)
        
        return (file_info, extracted)
    except Exception as e:
        print(f"Error processing single file: {e}")
        return None

def main(json_file_path, output_dir="summary", num_gpus=None, batch_size=8, n = 10):
    """Main function to process all files in all repositories."""
    # Print GPU information
    # gpu_count = torch.cuda.device_count()
    # print(f"Available GPUs: {gpu_count}")
    # for i in range(gpu_count):
    #     print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    
    # # Load repository details from JSON file
    # try:
    #     with open(json_file_path, 'r') as f:
    #         try:
    #             repo_details = json.load(f)
    #             print(f"Successfully loaded JSON from {json_file_path}")
    #         except json.JSONDecodeError as e:
    #             print(f"Error decoding JSON: {e}")
    #             return
    # except FileNotFoundError:
    #     print(f"File not found: {json_file_path}")
    #     return
    
    # # Verify the data structure
    # if isinstance(repo_details, dict):
    #     print(f"Loaded {len(repo_details)} repositories from JSON file")
    # else:
    #     print(f"Unexpected format in JSON file: {type(repo_details)}")
    #     return
    with open(json_file_path, 'r') as f:
        repo_details = json.load(f)
    process_files_for_module_docstrings(repo_details, output_dir, n, weightBM25, weightSemantic)

if __name__ == "__main__":
    # You can specify number of GPUs and batch size here
    # If num_gpus is None, it will use all available GPUs
    main("top_60_files.json", output_dir="summary", num_gpus=None, batch_size=8, n = 60)