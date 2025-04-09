# src/docstring_utils.py
import ast
import os
from collections import defaultdict

def has_module_docstring(file_path, repo_with_underscore, row_idx):
    full_path = os.path.join(f"decoupled_top_files/{row_idx}/{repo_with_underscore}/", file_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=full_path)
            return ast.get_docstring(tree) is not None
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def get_files_missing_module_docstrings(file_list, repo_with_underscore, row_idx=None):
    missing_docstring_files = []
    for file in file_list:
        if file.endswith(".py") and not has_module_docstring(file, repo_with_underscore, row_idx):
            missing_docstring_files.append(file)
    return missing_docstring_files

def add_ast_parents(node, parent=None):
    node.parent = parent
    for child in ast.iter_child_nodes(node):
        add_ast_parents(child, node)
    return node

def extract_functions_without_docstrings(file_path, repo_with_underscore, row_idx):
    full_path = os.path.join(f"decoupled_top_files/{row_idx}/{repo_with_underscore}/", file_path)
    functions_data = []
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=full_path)
        add_ast_parents(tree)
        lines = source.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and ast.get_docstring(node) is None:
                start = node.lineno - 1
                end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
                func_source = "\n".join(lines[start:end])
                class_name = None
                parent = getattr(node, "parent", None)
                while parent is not None:
                    if isinstance(parent, ast.ClassDef):
                        class_name = parent.name
                        break
                    parent = getattr(parent, "parent", None)
                functions_data.append({
                    "name": node.name,
                    "source": func_source,
                    "start_lineno": start + 1,
                    "end_lineno": end,
                    "file": full_path,
                    "class_name": class_name
                })
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return functions_data

def extract_functions_from_files(file_list, repo_with_underscore, row_idx):
    all_functions = []
    for file in file_list:
        if file.endswith(".py"):
            funcs = extract_functions_without_docstrings(file, repo_with_underscore, row_idx)
            all_functions.extend(funcs)
    return all_functions

def extract_docstring_block(llm_output):
    if '"""' not in llm_output:
        return llm_output.strip()
    parts = llm_output.split('"""', 2)
    if len(parts) == 1:
        return llm_output.strip()
    elif len(parts) == 2:
        return parts[1].strip()
    else:
        return parts[1].strip()

def generate_function_summary(func, summary_tokenizer, summary_model, tokenizer):
    prompt = f"""# Original function:
{func['source']}

# Generate a Python docstring for the provided function. The summary should include key parameters, keywords, and indicate input/output details.
\"\"\""""
    inputs = summary_tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = summary_model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.2,
        do_sample=False,
        eos_token_id=tokenizer.convert_tokens_to_ids('\"\"\"')
    )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Generated: ", generated)
    extracted = extract_docstring_block(generated)
    print("Extracted docstring: ", extracted)
    return extracted

def add_ast_parents_module_level(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree

def insert_docstring_by_class_and_name(file_path, class_name, function_name, generated_docstring):
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

def filter_global_missing_functions_docstrings(global_missing_func_docstring_list):
    filtered_functions = [
        func for func in global_missing_func_docstring_list
        if (func["end_lineno"] - func["start_lineno"]) >= 3 and (func["end_lineno"] - func["start_lineno"]) <= 100
    ]
    func_count = {}
    print("Length of Filtered Functions: ", len(filtered_functions))
    for func in filtered_functions:
        diff = func["file"]
        func_count[diff] = func_count.get(diff, 0) + 1
    function_file_count = defaultdict(list)
    for file_name, count in func_count.items():
        function_file_count[count].append(file_name)
    files_to_remove = set()
    for key, files in function_file_count.items():
        if key > 40:
            files_to_remove.update(files)
    final_filtered_list = [func for func in filtered_functions if func["file"] not in files_to_remove]
    print("After filtering files with too many functions: ", len(final_filtered_list))
    return final_filtered_list

def extract_module_docstring(generated_string):
    start = generated_string.find('### Summary:')
    if start == -1:
        return generated_string.strip()
    start += len('### Summary:')
    end = generated_string.find('"""', start)
    if end == -1:
        return generated_string[start:].strip()
    else:
        return generated_string[start:end].strip()

def generate_module_docstring(file_path, repo_with_underscore, tokenizer, llm_model):
    full_path = f"decoupled_top_files/{repo_with_underscore}/{file_path}"
    with open(full_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    prompt = (
        "Below is the complete source code of a Python file.\n\n"
        "Your task is to read the file and generate a concise and informative docstring that describes:\n"
        "- The overall purpose of the file\n"
        "- The main classes and functions it defines\n"
        "- Key responsibilities or logic handled in this file\n"
        "- How the classes and functions interact (if applicable)\n\n"
        "Be concise, but include technical details where useful.\n\n"
        "### Python File:\n" +
        source_code +
        "\n\n### Summary:\n"
    )
    print(f"\nPrompt: {prompt}\n")
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = llm_model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.2,
        do_sample=False,
        eos_token_id=tokenizer.convert_tokens_to_ids('\"\"\"')
    )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\nGenerated module docstring: ", generated)
    extracted = extract_module_docstring(generated)
    print("\nExtracted module docstring: ", extracted)
    return extracted
