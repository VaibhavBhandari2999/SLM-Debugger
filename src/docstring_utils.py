from vllm import LLM, SamplingParams
import ast
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time
import torch
import os

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

def extract_docstring_block(llm_output):
    """Extract the docstring from the LLM output."""
    if '"""' not in llm_output:
        return llm_output.strip()
    parts = llm_output.split('"""', 2)
    if len(parts) == 1:
        return llm_output.strip()
    elif len(parts) == 2:
        return parts[1].strip()
    else:
        return parts[1].strip()

def create_summary_prompt(func):
    """Create a prompt for the function summary generation."""
    # Verify the function has the required fields
    if 'source' not in func:
        # Print the function to help debug
        print(f"Error: 'source' field missing in function: {func}")
        raise KeyError("'source' field missing in function")
    
    return f"""# Original function:
{func['source']}

# Generate a Python docstring for the provided function. The summary should include key parameters, keywords, and indicate input/output details.
\"\"\""""

def add_ast_parents_module_level(node):
    """Add parent attribute to all AST nodes."""
    for child in ast.iter_child_nodes(node):
        child.parent = node
        add_ast_parents_module_level(child)

def insert_docstring_by_class_and_name(file_path, class_name, function_name, generated_docstring, n, weightBM25, weightSemantic):
    """Insert the generated docstring into the function."""
    try:
        new_file_path = f"summary/{n}/{weightBM25}_{weightSemantic}" + file_path
        with open(new_file_path, "r", encoding="utf-8") as f:
            source = f.read()
        lines = source.splitlines()
        tree = ast.parse(source)
        add_ast_parents_module_level(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                actual_class = None
                parent = node
                while hasattr(parent, "parent"):
                    parent = parent.parent
                    if isinstance(parent, ast.ClassDef):
                        actual_class = parent.name
                        break
                if actual_class != class_name:
                    continue
                if ast.get_docstring(node) is not None:
                    print(f"Function '{function_name}' in class '{class_name}' in {new_file_path} already has a docstring. Skipping.")
                    return
                start_line = node.lineno - 1
                indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                doc_indent = " " * (indent + 4)
                doc_lines = [f'{doc_indent}"""']
                for line in generated_docstring.strip().split("\n"):
                    doc_lines.append(f"{doc_indent}{line.strip()}")
                doc_lines.append(f'{doc_indent}"""')
                doc_lines.append("")
                insert_at = start_line + 1
                lines[insert_at:insert_at] = doc_lines
                with open(new_file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
                print(f"Inserted docstring for function '{function_name}' in class '{class_name}' in {new_file_path}")
                return
        print(f"Function '{function_name}' in class '{class_name}' not found in {new_file_path}")
    except Exception as e:
        print(f"Error inserting docstring for '{function_name}' in class '{class_name}' in {new_file_path}: {e}")

def validate_function(func):
    """Validate that a function object has all required fields."""
    if not isinstance(func, dict):
        return False
    
    required_fields = ['source', 'file', 'name', 'class_name']
    return all(field in func for field in required_fields)

def batch_generate_summaries(functions, model):
    """Generate summaries for a batch of functions using vLLM."""
    # Validate and filter functions
    valid_functions = functions
    # for i, func in enumerate(functions):
    #     try:
    #         if validate_function(func):
    #             valid_functions.append(func)
    #         else:
    #             print(f"Skipping invalid function at index {i}: {func}")
    #     except Exception as e:
    #         print(f"Error validating function at index {i}: {e}")
    
    # if not valid_functions:
    #     print("No valid functions in batch!")
    #     return []
    
    # # Create prompts for all valid functions in this batch
    prompts = []
    for func in valid_functions:
        # try:
        prompts.append(create_summary_prompt(func))
        # except Exception as e:
        #     print(f"Error creating prompt for function {func.get('name', 'unknown')}: {e}")
        #     # Remove this function from the list of valid functions
        #     valid_functions.remove(func)
    
    # if not prompts:
    #     print("No valid prompts created!")
    #     return []
    
    # Configure sampling parameters
    sampling_params = SamplingParams(
        temperature=0.2,
        max_tokens=100,
        stop=['"""'],
        top_k=50,
    )
    
    # Use vLLM to generate all outputs at once
    outputs = model.generate(prompts, sampling_params)
    
    # Process the results
    results = []
    for i, output in enumerate(outputs):
        generated = output.outputs[0].text
        extracted = extract_docstring_block(generated)
        results.append((valid_functions[i], extracted))
    
    return results

def process_single_function(func, model):
    """Process a single function for debugging purposes."""
    print(f"Processing single function: {func.get('name', 'unknown')}")
    
    try:
        if not validate_function(func):
            print(f"Invalid function structure: {func}")
            return None
        
        prompt = create_summary_prompt(func)
        sampling_params = SamplingParams(
            temperature=0.2,
            max_tokens=100,
            stop=['"""'],
        )
        
        outputs = model.generate([prompt], sampling_params)
        generated = outputs[0].outputs[0].text
        extracted = extract_docstring_block(generated)
        
        return (func, extracted)
    except Exception as e:
        print(f"Error processing single function: {e}")
        return None

def summarise_functions(filtered_funcs, n, weightBM25, weightSemantic):
    """Process all functions using batched vLLM inference and parallel file I/O."""
    # Initialize the model with multiple GPUs
    model = get_summary_model()
    func_list = filtered_funcs
    batch_size = 16
    num_gpus_available = torch.cuda.device_count()
    adjusted_batch_size = batch_size * max(1, num_gpus_available)
    print(f"Using adjusted batch size: {adjusted_batch_size} based on GPU count: {num_gpus_available}")
    
    # Split functions into batches
    batches = [func_list[i:i+adjusted_batch_size] for i in range(0, len(func_list), adjusted_batch_size)]
    
    # Process each batch with vLLM
    all_results = []
    for batch_idx, batch in enumerate(tqdm(batches, desc="Generating docstrings")):
        print(f"\nProcessing batch {batch_idx+1}/{len(batches)} with {len(batch)} functions")
        
        try:
            # Validate the batch before processing
            valid_batch = [func for func in batch if validate_function(func)]
            if not valid_batch:
                print(f"Skipping batch {batch_idx+1} - no valid functions found")
                continue
                
            batch_results = batch_generate_summaries(valid_batch, model)
            all_results.extend(batch_results)
        except Exception as e:
            print(f"Error processing batch {batch_idx+1}: {str(e)}")
            # Try processing one by one for this batch
            for func_idx, func in enumerate(batch):
                try:
                    if validate_function(func):
                        print(f"Processing function {func_idx+1}/{len(batch)} individually")
                        result = process_single_function(func, model)
                        if result:
                            all_results.append(result)
                except Exception as e2:
                    print(f"Failed to process function {func_idx+1} individually: {str(e2)}")
    
    # save the results to a JSON file
    os.makedirs(f"decoupled/{n}/{weightBM25}_{weightSemantic}/Filtered", exist_ok=True)
    # Create the directory if it doesn't exist
    with open(f"decoupled/{n}/{weightBM25}_{weightSemantic}/Filtered/docstrings.json", "w") as f:
        json.dump(all_results, f, indent=4)
    print(f"Saved {len(all_results)} docstrings to summary/{n}/{weightBM25}_{weightSemantic}/docstrings.json")
    # Calculate CPU worker count based on system
    import multiprocessing
    cpu_workers = min(8, multiprocessing.cpu_count())
    
    # Now process file insertions in parallel
    if all_results:
        print(f"\nInserting {len(all_results)} docstrings")
        with ThreadPoolExecutor(max_workers=cpu_workers) as executor:
            futures = []
            for func, docstring in all_results:
                try:
                    futures.append(
                        executor.submit(
                            insert_docstring_by_class_and_name,
                            func["file"],
                            func["class_name"],
                            func["name"],
                            docstring, n, weightBM25, weightSemantic
                        )
                    )
                except Exception as e:
                    print(f"Error submitting file insertion job: {e}")
            
            # Wait for all file operations to complete with progress bar
            completed = 0
            for future in tqdm(futures, desc="Inserting docstrings"):
                try:
                    future.result()  # This will block until the future is done
                    completed += 1
                except Exception as e:
                    print(f"Error during file insertion: {e}")
            
            print(f"Successfully inserted {completed} docstrings out of {len(futures)} attempted")
    else:
        print("No results to insert!")



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

def module_summary(repo_details, n, weightBM25, weightSemantic):
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
            full_path = f"decoupled/{n}/{weightBM25}_{weightSemantic}/{repo_with_underscore}/{file_path}"
            output_path = f"module_summary/{n}/{weightBM25}_{weightSemantic}/{repo_with_underscore}/{file_path}"
            
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