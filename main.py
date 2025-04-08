import os
import re
import ast
import json
import time
import nltk
import datetime
import defaultdict
from pathlib import Path
import subprocess
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForCausalLM

nltk.download('punkt')

with open('swe_bench_test_1.json') as f:
    data = json.load(f)

with open('swe_bench_lite_test.json') as f:
    data_lite = json.load(f)

######## Repo setup functions ########

def clone_repo_checkout_commit(repo, base_commit):
    repo_path = repo.replace("/", "_")
    repo_local_path = "swe_bench_repos" + "/" + repo_path

    if os.path.exists(repo_local_path):
        print(f"Repository {repo} already exists. Skipping clone...")
        subprocess.run(["git", "reset", "--hard"], cwd=repo_local_path)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_local_path)  # Removes untracked files
    else:
        print(f"Cloning repo: {repo}")
        subprocess.run(["git", "clone", f"https://github.com/{repo}.git", repo_local_path])

    print(f" Checking out commit {base_commit} for {repo}...")
    subprocess.run(["git", "fetch", "--all"], cwd=repo_local_path)  # Fetching all commits
    result = subprocess.run(["git", "checkout", base_commit], cwd=repo_local_path)  # Checking out to the base commit
    if result.returncode != 0:
        print(f" Error checking out commit {base_commit} for {repo}:\n{result.stderr}")
        return False

    subprocess.run(["git", "reset", "--hard", base_commit], cwd=repo_local_path)  # Tree is at base commit 
    print("Successfully checked out repo at base_commit")
    return True




def create_file_structure(repo_path):
    print("Repo path is: ", repo_path)
    file_list = []

    exclude_dirs = {".git", ".github", ".vscode", "__pycache__", "node_modules", "dist", "build", ".pyinstaller"}
    exclude_extensions = {".yml", ".yaml", ".md", ".rst", ".toml", ".config", ".cfg", ".ini", ".txt", ".tex", ".dat", ".gz", ".cfg", ".in", ".csv", ".ecsv", ".css", ".png", ".csv", "", ".fits", ".hdf5", ".xsd", ".xml", ".bz2", ".hdr", }
    include_extensions = {".py"}
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]  
        for file in files:

            if file.startswith("."): #Hidden files can't have bugs
                continue
            
            file_ext = os.path.splitext(file)[1]  #Gets file extension
            # if file_ext not in exclude_extensions:
            if file_ext in include_extensions:
                full_path = os.path.join(root, file)  # Construct full file path
                file_list.append(full_path[16:]) #No point passing "swe_bench_repos/xyz" to the LLM
    
    return file_list




def initial_file_localization(file_structure_list, issue_description):
    prompt = f"""
    Given the following bug description:\n{issue_description}\n\n"
        "From this list of files:\n{file_structure_list}\n\n"
        "Identify the 10 most relevant files for debugging.
    """
    model_name = "Salesforce/codet5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)

    token_counts = len(tokenizer.tokenize(prompt))
    print("Token count: ", token_counts)
    outputs = model.generate(**inputs, max_length=1024)
    predicted_files = tokenizer.decode(outputs[0], skip_special_tokens=True)[0]

    return predicted_files



def rank_top_n_bm25_semantic(file_list, issue_description, n, weightBM25, weightSemantic):
    tokenized_file_list = []
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    # file_list_truncated = [file[16:] for file in file_list] #To remove the initial astropy_astropy/ from every file
    file_list_truncated = [file.split("/", 1)[1] for file in file_list] #Remove everything till and including the 1st slash (To remove the astropy_astropy and django_django

    for file in file_list_truncated:
        tokens = file.replace("/", " ").split()
        tokenized_file_list.append(nltk.word_tokenize(" ".join(tokens).lower()))

    #BM25 score
    bm25 = BM25Okapi(tokenized_file_list)
    query_tokens = nltk.word_tokenize(issue_description.lower())
    bm25_scores = np.array(bm25.get_scores(query_tokens))

    #Semantic Similarity score
    issue_embedding = semantic_model.encode(issue_description, convert_to_tensor=True)
    file_embeddings = semantic_model.encode(file_list_truncated, convert_to_tensor=True)

    semantic_scores = util.pytorch_cos_sim(issue_embedding, file_embeddings)[0].cpu().numpy()

    # Normalizing BM25 & Semantic Scores
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)  # Scale BM25 to [0,1]
    if np.max(semantic_scores) > 0:
        semantic_scores = semantic_scores / np.max(semantic_scores)  # Scale similarity to [0,1]

    # Combining both scores
    combined_scores = weightBM25 * bm25_scores + weightSemantic * semantic_scores  # Adjust weight if needed

    ranked_files = sorted(zip(file_list_truncated, combined_scores), key=lambda x: x[1], reverse=True)

    return [file for file, _ in ranked_files[:n]]


def extract_changed_file_from_patch(patch):
    matches = re.findall(r'diff --git a/(\S+)', patch)
    modified_files = [file for file in matches]
    return modified_files


def find_missing_strings(subset_list, main_list):
    return [item for item in subset_list if item not in main_list]



def iterate_main(data_lite, n, weightBM25, weightSemantic):

    no_of_files_present_in_top_n = 0
    row_indexes_files_present_in_top_n = []
    row_indexes_files_not_present_in_top_n = []
    dict_of_top_n_file_structure_lists = {}
    list_of_file_structure_lists = []
    
    for row_idx, entry in enumerate(data_lite):
        repo = entry.get("repo", "N/A")
        repo_with_underscore = repo.replace("/", "_")
        base_commit = entry.get("base_commit", "N/A")
        issue_description = entry.get("problem_statement", "N/A")
        patch = entry.get("patch", "N/A")
    
    
        print("----------------------------------")
        print("Row Index is: ", row_idx)

        #---------------------------------------------------------------
        checkout_status = clone_repo_checkout_commit(repo, base_commit)

        #---------------------------------------------------------------
    
        file_structure_list = create_file_structure(f"swe_bench_repos/{repo_with_underscore}")
        list_of_file_structure_lists.append(file_structure_list)
        print("Number of files in repo: ", len(file_structure_list))
        # print("File Structure List: ", file_structure_list)
    
        top_n_files = rank_top_n_bm25_semantic(file_structure_list, issue_description, n, weightBM25, weightSemantic)

        main_file_path = f"decoupled_top_files_without_summaries/{row_idx}/{repo_with_underscore}"
        os.makedirs(main_file_path, exist_ok=True)
        
        for file in top_n_files:
            file_path = Path(main_file_path+f"/{file}")
            
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_content = Path(f"swe_bench_repos/{repo_with_underscore}/{file}").read_text()

            file_path.write_text(file_content)
            print("Writing file:",file_path)
        
        # Add function which will take top n files as input, determine the files without docstrings and then find the function without docstrings. Then create docstrings for such functions and attach it as docstrings to the function.

        #----------------------------
        # dict_of_top_n_file_structure_lists[row_idx] = (top_n_files)
        dict_of_top_n_file_structure_lists[row_idx] = { "repo_with_underscore": repo_with_underscore, "top_n_files": top_n_files, "repo":repo, "base_commit": base_commit, "patch": patch, "issue_description":issue_description }

        #----------------------------
        
        # print("Top N Files: ", top_n_files)
        
        ground_truth_modified_files = extract_changed_file_from_patch(patch)
        print("\nGround Truth modified Files: ", ground_truth_modified_files)
    
        # if ground_truth_modified_files in top_n_files:
        if set(ground_truth_modified_files).issubset(set(top_n_files)):
            print("\nFile Present")
            no_of_files_present_in_top_n += 1
            row_indexes_files_present_in_top_n.append(row_idx)
        else:
            print("\nFile Absent")
            row_indexes_files_not_present_in_top_n.append(row_idx)
    
        print("\nMissing Files are: ", find_missing_strings(ground_truth_modified_files, top_n_files))

    with open(f"top_{n}_files.json", "w") as f:
        json.dump(dict_of_top_n_file_structure_lists, f, indent=4)
    
    return no_of_files_present_in_top_n


# file_hit_ratios = {}
# for i in range(1,11):
#     print("-- "*100)
#     score = iterate_main(data_lite, i,0.2,0.8)
#     file_hit_ratios[i] = score

#     print(score)

# with open("FileHits/file_hits_no_summary.json", "w") as f:
#     json.dump(file_hit_ratios, f, indent=4)




from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
model_id = "Qwen/Qwen2.5-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
llm_model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.float16)


import ast
import os

def has_module_docstring(file_path, repo_with_underscore, row_idx):
    """Check if a Python file has a module-level docstring at the beginning."""
    full_path = os.path.join(f"decoupled_top_files/{row_idx}/{repo_with_underscore}/", file_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=full_path)
            return ast.get_docstring(tree) is not None
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def get_files_missing_module_docstrings(file_list, repo_with_underscore, row_idx):
    """Return a list of Python files that are missing module-level docstrings."""
    missing_docstring_files = []
    for file in file_list:
        if file.endswith(".py") and not has_module_docstring(file, repo_with_underscore, row_idx):
            missing_docstring_files.append(file)
    return missing_docstring_files


def add_ast_parents(node, parent=None):
    """
    Recursively attach parent pointers to all child nodes.
    """
    node.parent = parent
    for child in ast.iter_child_nodes(node):
        add_ast_parents(child, node)


def extract_functions_without_docstrings(file_path, repo_with_underscore, row_idx):
    """
    Extract function details for functions without docstrings in a file,
    including the enclosing class name (if any).
    """
    full_path = os.path.join(f"decoupled_top_files/{row_idx}/{repo_with_underscore}/", file_path)
    functions_data = []

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=full_path)
        add_ast_parents(tree)  # Attach parent pointers to all nodes
        lines = source.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and ast.get_docstring(node) is None:
                start = node.lineno - 1
                end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
                func_source = "\n".join(lines[start:end])

                # Find the first ancestor that is a ClassDef (if any)
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
    """Extract all functions without docstrings from the given list of files."""
    all_functions = []

    for file in file_list:
        if file.endswith(".py"):
            funcs = extract_functions_without_docstrings(file, repo_with_underscore, row_idx)
            all_functions.extend(funcs)

    return all_functions


def extract_docstring_block(llm_output):
    """
    Extract the docstring content from LLM output that may or may not have a closing triple quote.
    """
    if '"""' not in llm_output:
        return llm_output.strip()  # no triple quotes, just return as-is

    parts = llm_output.split('"""', 2)  # Split into at most 3 parts
    if len(parts) == 1:
        return llm_output.strip()
    elif len(parts) == 2:
        return parts[1].strip()
    else:
        return parts[1].strip()  # between the first and second triple quote

summary_model = "Qwen/Qwen2.5-7B-Instruct"
summary_tokenizer = AutoTokenizer.from_pretrained(summary_model)
summary_model = AutoModelForCausalLM.from_pretrained(summary_model).to("cuda:0")

def generate_function_summary(func):
    prompt = f"""# Original function:
    {func['source']}
    
    # Generate a Python docstring for the provided function. I want the summary to contain the important keywords and functions used in it which affect the input and output variables as well.
    \"\"\""""
    
    inputs = summary_tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = summary_model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.2,
        do_sample=False,
        eos_token_id=tokenizer.convert_tokens_to_ids('\"\"\"')  # Stop at end of docstring
    )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Generated: ",generated)

    extracted = extract_docstring_block(generated)

    print("Extracted docstrings: ", extracted)

    return extracted


def add_ast_parents(tree):
    """Attach parent pointers to all nodes in the AST."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree

def insert_docstring_by_class_and_name(file_path, class_name, function_name, generated_docstring):
    """
    Insert a generated docstring into the specific function identified by its name and parent class.
    This avoids conflicts when multiple functions share the same name.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        lines = source.splitlines()
        tree = ast.parse(source)
        tree = add_ast_parents(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Find the function's parent class (if any)
                actual_class = None
                parent = node
                while hasattr(parent, "parent"):
                    parent = parent.parent
                    if isinstance(parent, ast.ClassDef):
                        actual_class = parent.name
                        break

                # Check if the function belongs to the expected class
                if actual_class != class_name:
                    continue

                if ast.get_docstring(node) is not None:
                    print(f"⚠️ Function '{function_name}' in class '{class_name}' in {file_path} already has a docstring. Skipping.")
                    return

                # Insert the docstring after the function definition line
                start_line = node.lineno - 1
                indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                doc_indent = " " * (indent + 4)

                # Format the docstring block
                doc_lines = [f'{doc_indent}"""']
                for line in generated_docstring.strip().split("\n"):
                    doc_lines.append(f"{doc_indent}{line.strip()}")
                doc_lines.append(f'{doc_indent}"""')
                doc_lines.append("")  # Blank line after docstring

                # Insert after the function definition
                insert_at = start_line + 1
                lines[insert_at:insert_at] = doc_lines

                # Write the updated source back to the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")

                print(f"✅ Inserted docstring for function '{function_name}' in class '{class_name}' in {file_path}")
                return

        print(f"❌ Function '{function_name}' in class '{class_name}' not found in {file_path}")
    except Exception as e:
        print(f"❌ Error inserting docstring for '{function_name}' in class '{class_name}' in {file_path}: {e}")



def filter_global_missing_functions_docstrings(global_missing_func_docstring_list):
    filtered_functions = [
        func for func in global_missing_func_docstring_list
        if (func["end_lineno"] - func["start_lineno"]) >= 3 and (func["end_lineno"] - func["start_lineno"]) <=100
    ]

    func_count={}
    print("Length of Filtered Functions with all sizes greater than 1",len(filtered_functions))

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

    final_filtered_list = [
        func for func in filtered_functions if func["file"] not in files_to_remove
    ]

    print("Length of Filtered Functions with all sizes greater than 1 and removing files with more than 100 functions",len(final_filtered_list))
    return final_filtered_list
    


import time
start = time.time()

with open("top_10_files.json", "r") as f:
    my_dict = json.load(f)

global_missing_func_docstring_list = []

for key, entry in my_dict.items():
    repo_with_underscore = entry["repo_with_underscore"]
    file_list = entry["top_n_files"]

    print("- -"*80)
    print("Row_idx is: ", key)

    files_with_missing_module_level_docstrings = get_files_missing_module_docstrings(file_list, repo_with_underscore, key)

    print("Files with Missing Module Level Docstrings: ")
    for file in files_with_missing_module_level_docstrings:
        print(" -", file)


    functions_with_missing_docstrings = extract_functions_from_files(files_with_missing_module_level_docstrings, repo_with_underscore, key)
    global_missing_func_docstring_list.extend(functions_with_missing_docstrings)
    print(f"\n\nNumber of functions with missing docstrings: {len(functions_with_missing_docstrings)}\n\n")

print("Number of functions with missing docstrings - ", len(global_missing_func_docstring_list))

filtered_global_missing_func_docstring_list = filter_global_missing_functions_docstrings(global_missing_func_docstring_list)

with open(f"filtered_functions_missing_docstrings", "w") as f:
        json.dump(filtered_global_missing_func_docstring_list, f, indent=4)

for func in filtered_global_missing_func_docstring_list:
    generated_docstring = generate_function_summary(func)
    func['generated_docstring'] = generated_docstring

    insert_docstring_by_class_and_name(func["file"], func['class_name'], func["name"], func["generated_docstring"])


print("\n\nAll Generated Docstrings added\n\n")




print("All docstrings for all row indexes added")
end_time = datetime.now()
print("Ended at:", end_time)
duration = end_time - start_time
print("Duration:", duration)

# Write timing info to a file
with open("execution_times.log", "a") as f:
    f.write(f"--- Execution Log ---\n")
    f.write(f"Started at: {start_time}\n")
    f.write(f"Ended at: {end_time}\n")
    f.write(f"Duration: {duration}\n")
    f.write("\n")



def extract_module_docstring(generated_string):
    
    start = generated_string.find('### Summary:')
    if start == -1:
        return generated_string.strip()

    start += 12
    end = llm_output.find('"""', start)
    
    if end == -1:
        # No closing triple quote found; take everything until the end.
        return llm_output[start:].strip()
    else:
        return llm_output[start:end].strip()

def generate_module_docstring(file_path, repo_with_underscore):

    with open(f"decoupled_top_files/{repo_with_underscore}/{file_path}", "r", encoding="utf-8") as f:
        source_code = f.read()
    
    prompt = (
    "Below is the complete source code of a Python file.\n\n"
            "Your task is to read the file and generate a concise and informative docstring that describes:\n"
            "- The overall purpose of the file\n"
            "- The main classes and functions it defines\n"
            "- Key responsibilities or logic handled in this file\n"
            "- How the classes and functions interact (if applicable)\n\n"
            "Be concise, but include technical details where useful.\n\n"
            "### Python File:\n"
            + source_code
            + "\n\n### Summary:\n"
    )

    print(f"\n\nPrompt is: {prompt}\n")
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = llm_model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.2,
        do_sample=False,
        eos_token_id=tokenizer.convert_tokens_to_ids('\"\"\"')  # Stop at end of docstring
    )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n\nGenerated: ",generated)

    extracted = extract_module_docstring(generated)
    print("\n\Extracted: ",extracted)

    return extracted

with open("top_10_files.json", "r") as f:
    my_dict = json.load(f)

for key, entry in my_dict.items():
    repo_with_underscore = entry["repo_with_underscore"]
    file_list = entry["top_n_files"]
    repo = entry["repo"]
    base_commit = entry["base_commit"]
    issue_description = entry["issue_description"]
    patch = entry["patch"]
    
    print("- -"*80)
    print("Row_idx is: ", key)

    #Cause we only need to add module level docstrings to those that don't already have them
    files_with_missing_module_level_docstrings = get_files_missing_module_docstrings(file_list, repo_with_underscore)
    
    for file in files_with_missing_module_level_docstrings:
        print("'"*100)
        print("\nFile being considered is: ", file)
        generated_module_docstring = generate_module_docstring(file, repo_with_underscore)

  
import nltk
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util

nltk.download('punkt')
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

def rank_top_n_bm25_semantic(row_index,repo_with_underscore, file_list, issue_description, n, weightBM25, weightSemantic, main_folder):
    tokenized_file_list = []
    file_content_list = []


    for file in file_list:

        with open(f"{main_folder}/{row_index}/{repo_with_underscore}/{file}", "r") as f:
            content = f.read()

            file_path_string = f"{repo_with_underscore}/{file}"
            file_path_string_with_space = file_path_string.replace("/", " ")
            file_path_with_content = file_path_string + "\n" + content
            file_content_list.append((content, file_path_string))
            tokenized_file_list.append((nltk.word_tokenize( file_path_with_content), file_path_string))

    content_list = [key for key, _ in file_content_list]
    tokenized_content_list = [key for key,_ in tokenized_file_list]

    #BM25 score
    bm25 = BM25Okapi(tokenized_content_list)
    query_tokens = nltk.word_tokenize(issue_description.lower())
    bm25_scores = np.array(bm25.get_scores(query_tokens))

    #Semantic Similarity score
    issue_embedding = semantic_model.encode(issue_description, convert_to_tensor=True)
    file_embeddings = semantic_model.encode(content_list, convert_to_tensor=True)

    semantic_scores = util.pytorch_cos_sim(issue_embedding, file_embeddings)[0].cpu().numpy()

    # Normalizing BM25 & Semantic Scores
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)  # Scale BM25 to [0,1]
    if np.max(semantic_scores) > 0:
        semantic_scores = semantic_scores / np.max(semantic_scores)  # Scale similarity to [0,1]

    # Combining both scores
    combined_scores = weightBM25 * bm25_scores + weightSemantic * semantic_scores  # Adjust weight if needed

    file_path_list = [val for key, val in file_content_list]
    processed_paths = [s.replace(' ', '/').split('/', 1)[1] for s in file_path_list]

    ranked_files = sorted(zip(processed_paths, combined_scores), key=lambda x: x[1], reverse=True)

    return [file for file, _ in ranked_files[:n]]


import re
def extract_changed_file_from_patch(patch):
    matches = re.findall(r'diff --git a/(\S+)', patch)

    # modified_files = ["astropy_astropy/" + file for file in matches]
    modified_files = [file for file in matches]
    # print("Files Changed are: ", modified_files)
    return modified_files

swe_bench_lite_test = "swe_bench_lite_test.json"
with open(swe_bench_lite_test, "r") as f:
    swe_bench_lite_test = json.load(f)

with open("top_10_files.json", "r") as f:
    my_dict = json.load(f)

def iterate_main_file_hits_with_summary(n, main_folder):
    
    file_hit_value =0
    hits = 0
    
    for row_idx, entry in enumerate(swe_bench_lite_test):
        repo = entry.get("repo", "N/A")
        repo_with_underscore = repo.replace("/", "_")
        base_commit = entry.get("base_commit", "N/A")
        issue_description = entry.get("problem_statement", "N/A")
        patch = entry.get("patch", "N/A")
    
        print("-"*100)
        print(f"Row Index: {row_idx}")
        print(f"Repo: {repo}")
        print(f"Base Commit: {base_commit}")
        # print(f"Issue Description: {issue_description}")
        # print(f"Patch: {patch}")
    
        top_n_files = my_dict.get(str(row_idx), {}).get("top_n_files", [])
        print(f"Top N Files: {top_n_files}")
        print("-"*100)
        print("\n\n")
        target_files = rank_top_n_bm25_semantic(row_idx, repo_with_underscore, top_n_files, issue_description, n, 0.8, 0.2, main_folder)
        print("\n Target Files are: ", target_files)
        actual_target = extract_changed_file_from_patch(patch)
        print("\nGround Truth Modified Files: ", actual_target)
    
        if len(actual_target) > 1:
            hits += 1
       
        is_subset = all(item in target_files for item in actual_target)
        if is_subset:
            file_hit_value += 1
            print("File Hit")

    print("Number of file hits: ",file_hit_value)
    print("File hit Perc: ", file_hit_value/300)
    print("Multi-File Patch:", hits)
    return file_hit_value


file_hit_ratios = {}
for i in range(1,11):
    print("-- "*100)
    print("Considering top-",i)
    with_summary = iterate_main_file_hits_with_summary(i, "decoupled_top_files")

    file_hit_ratios[i] = with_summary

with open("FileHits/file_hit_with_summary.json", "w") as f:
    json.dump(file_hit_ratios, f, indent=4)

import json
import matplotlib.pyplot as plt

# Load both JSON files
with open("FileHits/file_hit_with_summary.json") as f:
    with_summary = json.load(f)

with open("FileHits/file_hits_no_summary.json") as f:
    without_summary = json.load(f)

# Convert keys to int, sort them, and remove the last one (i = 10)
x = sorted(int(k) for k in with_summary.keys())  # from 1 to 9

# Normalize values by 300 and extract in sorted order
y_with = [with_summary[str(i)] / 300 * 100 for i in x]
y_without = [without_summary[str(i)] / 300 * 100 for i in x]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(x, y_with, marker='o', label="With Summary", linewidth=2)
plt.plot(x, y_without, marker='s', label="Without Summary", linewidth=2)

# Annotate percentages on each point
for x_i, y_w, y_wo in zip(x, y_with, y_without):
    dx = -0.15 if x_i == 1 else 0  # minor x-offset for label on "1"
    plt.text(x_i + dx, y_w + 1, f"{y_w:.1f}%", ha='center', fontsize=8)
    plt.text(x_i + dx, y_wo - 3, f"{y_wo:.1f}%", ha='center', fontsize=8)

# Labels and title
plt.xlabel("Top-N Files", fontsize=12)
plt.ylabel("File Hit Percentage", fontsize=12)
plt.title("File Hit % With vs Without Summary", fontsize=14)
plt.tick_params(axis='x', pad=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.xticks(x)
plt.gca().invert_xaxis()  # 👈 THIS LINE FLIPS THE X-AXIS (from 9 to 1)
plt.tight_layout()
plt.show()


list_of_file_hit_values = {}
weights = np.linspace(0, 1, 11)
n_values = [30, 60]

results_file = "results.json"
def save_results_to_file():
    with open(results_file, "w") as f:
        json.dump({str(k): v for k, v in list_of_file_hit_values.items()}, f)

for n in n_values:
    for w_base in weights:
        w_semantic = 1 - w_base
        print("-"*100)
        print(f"N: {n}, w_base: {w_base}, w_semantic: {w_semantic}")
        print("-"*100)
        score = iterate_main(swe_bench_lite_test, n, w_base, w_semantic)
        list_of_file_hit_values[(n, w_base, w_semantic)] = score

        print(f"File Hits: {score}, for n: {n}, w_base: {w_base}, w_semantic: {w_semantic}")
        save_results_to_file()

print(list_of_file_hit_values)


######## Plotting ########

import matplotlib.pyplot as plt
import ast
# print(list_of_file_hit_values)

with open("results-Copy1.json", "r") as f:
    raw_data = json.load(f)
    list_of_file_hit_values = {ast.literal_eval(k): v for k, v in raw_data.items()}

print(list_of_file_hit_values)

best_combo = max(list_of_file_hit_values, key=list_of_file_hit_values.get)
print(best_combo)
best_n, best_w_base, best_w_semantic = best_combo
best_score = list_of_file_hit_values[best_combo]

print(f"Best N: {best_n}, Best weight for BM25: {best_w_base}, Best weight for Semantic: {best_w_semantic}")
print("Best Score for the above parameters is: ", best_score)


plt.figure(figsize=(10, 5))
x_labels = []
x_positions = []

n_values = sorted(set(n for (n, _, _) in list_of_file_hit_values.keys()))

for n in n_values:
    x_vals, y_vals, scores = zip(*[(w_base, w_semantic, list_of_file_hit_values[(n, w_base, w_semantic)])
                                    for (n_val, w_base, w_semantic) in list_of_file_hit_values.keys() if n_val == n])
    
    plt.scatter(x_vals, scores, label=f'n={n}', marker='o')
    plt.plot(x_vals, scores, linestyle='-', alpha=0.7)

    for x, y, score in zip(x_vals, scores, scores):
        plt.text(x, y + 2, str(score), fontsize=8, ha='center')
    
    if not x_labels:
        x_labels = [f"{w_base:.1f},{w_semantic:.1f}" for w_base, w_semantic in zip(x_vals, y_vals)]
        x_positions = list(x_vals)

plt.xticks(x_positions, x_labels, rotation=0)
plt.xlabel("BM25 Weight, Semantic Weight")
plt.ylabel("Files in Top N")
plt.title("Performance for Different n Values")
plt.legend(loc='lower left')
plt.show()


import matplotlib.pyplot as plt
import ast
import json

# Load JSON and parse keys
with open("results-Copy1.json", "r") as f:
    raw_data = json.load(f)
    list_of_file_hit_values = {ast.literal_eval(k): v for k, v in raw_data.items()}

# Find the best-performing combo
best_combo = max(list_of_file_hit_values, key=list_of_file_hit_values.get)
best_n, best_w_base, best_w_semantic = best_combo
best_score = list_of_file_hit_values[best_combo]

print(f"Best N: {best_n}, Best BM25 weight: {best_w_base}, Semantic weight: {best_w_semantic}")
print(f"Best Score: {best_score} ({(best_score/300)*100:.2f}%)")

# Plotting
plt.figure(figsize=(10, 5))
x_labels = []
x_positions = []

n_values = sorted(set(n for (n, _, _) in list_of_file_hit_values.keys()))

for n in n_values:
    data_points = [
        (w_base, w_semantic, list_of_file_hit_values[(n, w_base, w_semantic)] / 300 * 100)
        for (n_val, w_base, w_semantic) in list_of_file_hit_values.keys() if n_val == n
    ]
    x_vals, y_vals, percentages = zip(*data_points)

    plt.scatter(x_vals, percentages, label=f'n={n}', marker='o')
    plt.plot(x_vals, percentages, linestyle='-', alpha=0.7)

    for x, y, pct in zip(x_vals, percentages, percentages):
        plt.text(x, y + 1.2, f"{pct:.1f}%", fontsize=8, ha='center')

    if not x_labels:
        x_labels = [f"{w_base:.1f},{w_semantic:.1f}" for w_base, w_semantic in zip(x_vals, y_vals)]
        x_positions = list(x_vals)

plt.xticks(x_positions, x_labels, rotation=0)
plt.xlabel("BM25 Weight, Semantic Weight")
plt.ylabel("Files in Top N (%)")
plt.title("File Hit Percentage for Different n Values")
plt.legend(loc='lower left')
plt.tight_layout()
plt.show()
