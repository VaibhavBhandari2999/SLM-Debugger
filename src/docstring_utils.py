from vllm import LLM, SamplingParams
import ast
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time
import torch

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


# # src/docstring_utils.py
# import ast
# import os
# from collections import defaultdict

# def has_module_docstring(file_path, repo_with_underscore, row_idx, n, weightBM25, weightSemantic):
#     full_path = os.path.join(f"decoupled/{n}/{weightBM25}_{weightSemantic}/{row_idx}/{repo_with_underscore}/", file_path)
#     try:
#         with open(full_path, "r", encoding="utf-8") as f:
#             tree = ast.parse(f.read(), filename=full_path)
#             return ast.get_docstring(tree) is not None
#     except Exception as e:
#         print(f"Error processing {file_path}: {e}")
#         return False

# def get_files_missing_module_docstrings(file_list, repo_with_underscore, row_idx=None, n=10, weightBM25=0.5, weightSemantic=0.5):
#     missing_docstring_files = []
#     for file in file_list:
#         if file.endswith(".py") and not has_module_docstring(file, repo_with_underscore, row_idx, n, weightBM25, weightSemantic):
#             missing_docstring_files.append(file)
#     return missing_docstring_files

# def add_ast_parents(node, parent=None):
#     node.parent = parent
#     for child in ast.iter_child_nodes(node):
#         add_ast_parents(child, node)
#     return node

# def extract_functions_without_docstrings(file_path, repo_with_underscore, row_idx, n, weightBM25, weightSemantic):
#     full_path = os.path.join(f"decoupled/{n}/{weightBM25}_{weightSemantic}/{row_idx}/{repo_with_underscore}/", file_path)
#     functions_data = []
#     try:
#         with open(full_path, "r", encoding="utf-8") as f:
#             source = f.read()
#         tree = ast.parse(source, filename=full_path)
#         add_ast_parents(tree)
#         lines = source.splitlines()
#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef) and ast.get_docstring(node) is None:
#                 start = node.lineno - 1
#                 end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
#                 func_source = "\n".join(lines[start:end])
#                 class_name = None
#                 parent = getattr(node, "parent", None)
#                 while parent is not None:
#                     if isinstance(parent, ast.ClassDef):
#                         class_name = parent.name
#                         break
#                     parent = getattr(parent, "parent", None)
#                 functions_data.append({
#                     "name": node.name,
#                     "source": func_source,
#                     "start_lineno": start + 1,
#                     "end_lineno": end,
#                     "file": full_path,
#                     "class_name": class_name
#                 })
#     except Exception as e:
#         print(f"Error processing {file_path}: {e}")
#     return functions_data

# def extract_functions_from_files(file_list, repo_with_underscore, row_idx, n, weightBM25, weightSemantic):
#     all_functions = []
#     for file in file_list:
#         if file.endswith(".py"):
#             funcs = extract_functions_without_docstrings(file, repo_with_underscore, row_idx, n, weightBM25, weightSemantic)
#             all_functions.extend(funcs)
#     return all_functions

# def extract_docstring_block(llm_output):
#     if '"""' not in llm_output:
#         return llm_output.strip()
#     parts = llm_output.split('"""', 2)
#     if len(parts) == 1:
#         return llm_output.strip()
#     elif len(parts) == 2:
#         return parts[1].strip()
#     else:
#         return parts[1].strip()

# def generate_function_summary(func, summary_tokenizer, summary_model, tokenizer):
#     prompt = f"""# Original function:
# {func['source']}

# # Generate a Python docstring for the provided function. The summary should include key parameters, keywords, and indicate input/output details.
# \"\"\""""
#     inputs = summary_tokenizer(prompt, return_tensors="pt").to("cuda")
#     outputs = summary_model.generate(
#         **inputs,
#         max_new_tokens=100,
#         temperature=0.2,
#         do_sample=False,
#         eos_token_id=tokenizer.convert_tokens_to_ids('\"\"\"')
#     )
#     generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     print("Generated: ", generated)
#     extracted = extract_docstring_block(generated)
#     print("Extracted docstring: ", extracted)
#     return extracted

# def add_ast_parents_module_level(tree):
#     for node in ast.walk(tree):
#         for child in ast.iter_child_nodes(node):
#             child.parent = node
#     return tree

# def insert_docstring_by_class_and_name(file_path, class_name, function_name, generated_docstring):
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             source = f.read()
#         lines = source.splitlines()
#         tree = ast.parse(source)
#         add_ast_parents_module_level(tree)
#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef) and node.name == function_name:
#                 actual_class = None
#                 parent = node
#                 while hasattr(parent, "parent"):
#                     parent = parent.parent
#                     if isinstance(parent, ast.ClassDef):
#                         actual_class = parent.name
#                         break
#                 if actual_class != class_name:
#                     continue
#                 if ast.get_docstring(node) is not None:
#                     print(f"Function '{function_name}' in class '{class_name}' in {file_path} already has a docstring. Skipping.")
#                     return
#                 start_line = node.lineno - 1
#                 indent = len(lines[start_line]) - len(lines[start_line].lstrip())
#                 doc_indent = " " * (indent + 4)
#                 doc_lines = [f'{doc_indent}"""']
#                 for line in generated_docstring.strip().split("\n"):
#                     doc_lines.append(f"{doc_indent}{line.strip()}")
#                 doc_lines.append(f'{doc_indent}"""')
#                 doc_lines.append("")
#                 insert_at = start_line + 1
#                 lines[insert_at:insert_at] = doc_lines
#                 with open(file_path, "w", encoding="utf-8") as f:
#                     f.write("\n".join(lines) + "\n")
#                 print(f"Inserted docstring for function '{function_name}' in class '{class_name}' in {file_path}")
#                 return
#         print(f"Function '{function_name}' in class '{class_name}' not found in {file_path}")
#     except Exception as e:
#         print(f"Error inserting docstring for '{function_name}' in class '{class_name}' in {file_path}: {e}")

# def filter_global_missing_functions_docstrings(global_missing_func_docstring_list):
#     filtered_functions = [
#         func for func in global_missing_func_docstring_list
#         if (func["end_lineno"] - func["start_lineno"]) >= 3 and (func["end_lineno"] - func["start_lineno"]) <= 100
#     ]
#     func_count = {}
#     print("Length of Filtered Functions: ", len(filtered_functions))
#     for func in filtered_functions:
#         diff = func["file"]
#         func_count[diff] = func_count.get(diff, 0) + 1
#     function_file_count = defaultdict(list)
#     for file_name, count in func_count.items():
#         function_file_count[count].append(file_name)
#     files_to_remove = set()
#     for key, files in function_file_count.items():
#         if key > 40:
#             files_to_remove.update(files)
#     final_filtered_list = [func for func in filtered_functions if func["file"] not in files_to_remove]
#     print("After filtering files with too many functions: ", len(final_filtered_list))
#     return final_filtered_list

# def extract_module_docstring(generated_string):
#     start = generated_string.find('### Summary:')
#     if start == -1:
#         return generated_string.strip()
#     start += len('### Summary:')
#     end = generated_string.find('"""', start)
#     if end == -1:
#         return generated_string[start:].strip()
#     else:
#         return generated_string[start:end].strip()

# def generate_module_docstring(file_path, repo_with_underscore, tokenizer, llm_model):
#     full_path = f"decoupled_top_files/{repo_with_underscore}/{file_path}"
#     with open(full_path, "r", encoding="utf-8") as f:
#         source_code = f.read()
#     prompt = (
#         "Below is the complete source code of a Python file.\n\n"
#         "Your task is to read the file and generate a concise and informative docstring that describes:\n"
#         "- The overall purpose of the file\n"
#         "- The main classes and functions it defines\n"
#         "- Key responsibilities or logic handled in this file\n"
#         "- How the classes and functions interact (if applicable)\n\n"
#         "Be concise, but include technical details where useful.\n\n"
#         "### Python File:\n" +
#         source_code +
#         "\n\n### Summary:\n"
#     )
#     print(f"\nPrompt: {prompt}\n")
#     inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
#     outputs = llm_model.generate(
#         **inputs,
#         max_new_tokens=300,
#         temperature=0.2,
#         do_sample=False,
#         eos_token_id=tokenizer.convert_tokens_to_ids('\"\"\"')
#     )
#     generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     print("\nGenerated module docstring: ", generated)
#     extracted = extract_module_docstring(generated)
#     print("\nExtracted module docstring: ", extracted)
#     return extracted
