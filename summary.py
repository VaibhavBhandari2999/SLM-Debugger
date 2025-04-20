from vllm import LLM, SamplingParams
import ast
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

def get_summary_model():
    """Initialize the vLLM model for generating summaries."""
    model_id = "Qwen/Qwen2.5-7B-Instruct"
    # Use vLLM with conservative settings to avoid the socket error
    model = LLM(
        model=model_id,
        tensor_parallel_size=1,  # Set to number of GPUs you want to use
        trust_remote_code=True,  # Required for some models like Qwen
        dtype="half",  # Use half precision for efficiency
        gpu_memory_utilization=0.8,  # Prevent OOM errors
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
    return f"""# Original function:
{func['source']}

# Generate a Python docstring for the provided function. The summary should include key parameters, keywords, and indicate input/output details.
\"\"\""""

def add_ast_parents_module_level(node):
    """Add parent attribute to all AST nodes."""
    for child in ast.iter_child_nodes(node):
        child.parent = node
        add_ast_parents_module_level(child)

def insert_docstring_by_class_and_name(file_path, class_name, function_name, generated_docstring):
    """Insert the generated docstring into the function."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
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
                    print(f"Function '{function_name}' in class '{class_name}' in {file_path} already has a docstring. Skipping.")
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
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
                print(f"Inserted docstring for function '{function_name}' in class '{class_name}' in {file_path}")
                return
        print(f"Function '{function_name}' in class '{class_name}' not found in {file_path}")
    except Exception as e:
        print(f"Error inserting docstring for '{function_name}' in class '{class_name}' in {file_path}: {e}")

def batch_generate_summaries(functions, model):
    """Generate summaries for a batch of functions using vLLM."""
    # Create prompts for all functions in this batch
    prompts = [create_summary_prompt(func) for func in functions]
    
    # Configure sampling parameters
    sampling_params = SamplingParams(
        temperature=0.2,
        max_tokens=100,
        stop=['"""']
    )
    
    # Use vLLM to generate all outputs at once
    outputs = model.generate(prompts, sampling_params)
    
    # Process the results
    results = []
    for i, output in enumerate(outputs):
        generated = output.outputs[0].text
        extracted = extract_docstring_block(generated)
        results.append((functions[i], extracted))
    
    return results

def process_all_functions(filtered_funcs, batch_size=8):
    """Process all functions using batched vLLM inference and parallel file I/O."""
    # Initialize the model
    model = get_summary_model()
    
    # Split functions into batches
    batches = [filtered_funcs[i:i+batch_size] for i in range(0, len(filtered_funcs), batch_size)]
    
    # Process each batch with vLLM
    all_results = []
    for batch in tqdm(batches, desc="Generating docstrings"):
        try:
            batch_results = batch_generate_summaries(batch, model)
            all_results.extend(batch_results)
        except Exception as e:
            print(f"Error processing batch: {e}")
            # Wait a bit and retry with smaller batch
            time.sleep(1)
            try:
                # Split the batch in half and retry
                half = len(batch) // 2
                if half > 0:
                    batch1 = batch[:half]
                    batch2 = batch[half:]
                    batch_results1 = batch_generate_summaries(batch1, model)
                    batch_results2 = batch_generate_summaries(batch2, model)
                    all_results.extend(batch_results1)
                    all_results.extend(batch_results2)
                else:
                    # Process one by one if the batch is already small
                    for func in batch:
                        result = batch_generate_summaries([func], model)
                        all_results.extend(result)
            except Exception as e2:
                print(f"Error even with smaller batch: {e2}")
                # Skip this batch if all attempts fail
                continue
    
    # Now process file insertions in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for func, docstring in all_results:
            futures.append(
                executor.submit(
                    insert_docstring_by_class_and_name,
                    func["file"],
                    func["class_name"],
                    func["name"],
                    docstring
                )
            )
        
        # Wait for all file operations to complete with progress bar
        for _ in tqdm(futures, desc="Inserting docstrings"):
            _.result()  # This will block until the future is done

def main(json_file_path, batch_size=8):
    """Main function to process all functions."""
    # Load functions from JSON file
    with open(json_file_path, 'r') as f:
        filtered_funcs = json.load(f)
    
    print(f"Processing {len(filtered_funcs)} functions with batch size {batch_size}")
    process_all_functions(filtered_funcs, batch_size)

if __name__ == "__main__":
    # Adjust this parameter based on your hardware capabilities
    BATCH_SIZE = 8  # Reduce if you encounter memory issues
    
    main("functions_missing_docstrings_60.json", BATCH_SIZE)


# SLM-Debugger/functions_missing_docstrings_60.json