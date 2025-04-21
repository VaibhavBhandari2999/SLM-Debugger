# main.py
import json
import os
import numpy as np
from src.iteration import iterate_main, iterate_main_file_hits_with_summary
from src.model_utils import get_qwen_model, get_summary_model
from src.docstring_utils import (summarise_functions, module_summary, get_files_missing_module_docstrings, extract_functions_from_files, 
                                  filter_global_missing_functions_docstrings)
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load input data
with open("data/swe_bench_lite_test.json") as f:
    data_lite = json.load(f)


def get_summary_model():
    # Load the summary model
    summary_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
    summary_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
    return summary_tokenizer, summary_model

get_summary_model()

# # Run the main iteration (for file ranking without summaries)
n = 60
weightBM25 = 1.0
weightSemantic = 0.0
filter_funcs = False
if filter_funcs:
    fil = "Filtered"
else:
    fil = "Unfiltered"
    
# check if the file already exists
for i in np.arange(0.0, 1.0, 0.2):
    weightBM25 = round(i,1)
    weightSemantic = round(1 - i, 1)
    # print(weightBM25, weightSemantic)
    print("WeightBM25:", weightBM25)
    print("WeightSemantic:", weightSemantic)
    print("n:", n)

    ## Module-1
    try:
        with open(f"top_files/{n}/{weightBM25}_{weightSemantic}.json", "r") as f:
            tn = json.load(f)
            print("File already exists, skipping iteration.")
    except FileNotFoundError:
        # If the file doesn't exist, run the iteration
        print("File not found, running iteration.")
        file_hits = iterate_main(data_lite, n, weightBM25, weightSemantic)
        with open(f"top_files/{n}/{weightBM25}_{weightSemantic}.json", "r") as f:
            tn = json.load(f)

    ## Module-2
    try:
        with open(f"miss_doc/{n}/{fil}/{weightBM25}_{weightSemantic}.json", "r") as f:
            filtered_funcs = json.load(f)
            # print("File already exists, skipping iteration.")
            print("File already exists, skipping iteration.")
    except FileNotFoundError:
        # If the file doesn't exist, run the iteration
        print("File not found, running iteration.")
        # Iterate over the top N files
        print("Iterating over top N files...")
        global_missing_func_docstring_list = []
        for key, entry in tn.items():
            repo_with_underscore = entry["repo_with_underscore"]
            file_list = entry["top_n_files"]
            print("- " * 40)
            print("Processing Row:", key)

            files_missing_module = get_files_missing_module_docstrings(file_list, repo_with_underscore, key, n, weightBM25, weightSemantic)
            print("Files missing module-level docstrings:", files_missing_module)

            functions_missing = extract_functions_from_files(files_missing_module, repo_with_underscore, key, n, weightBM25, weightSemantic)
            global_missing_func_docstring_list.extend(functions_missing)

            print(f"Number of functions missing docstrings: {len(functions_missing)}")

            new_path = f"miss_doc/{n}/{fil}"
            os.makedirs(new_path, exist_ok=True)

            if filter_funcs:
                filtered_funcs = filter_global_missing_functions_docstrings(global_missing_func_docstring_list)
               
                # Create the directory if it doesn't exist
                with open(f"miss_doc/{n}/{fil}/{weightBM25}_{weightSemantic}.json", "w") as f:
                    json.dump(filtered_funcs, f, indent=4)
            else:
                filtered_funcs = global_missing_func_docstring_list
                # Create the directory if it doesn't exist
                with open(f"miss_doc/{n}/{fil}/{weightBM25}_{weightSemantic}.json", "w") as f:
                    json.dump(filtered_funcs, f, indent=4)
        print("Filtered functions missing docstrings:", len(filtered_funcs))
   

    ## Module-3
    ## Generate and insert function-level docstrings
    try:
        with open(f"decoupled/{n}/{weightBM25}_{weightSemantic}/{fil}/docstrings.json", "r") as f:
            docstrings = json.load(f)
            print("File already exists, skipping iteration.")
    except FileNotFoundError:
        summarise_functions(filtered_funcs, n, weightBM25, weightSemantic)

    ## Module-4
    ## Generate module-level docstrings for files missing them
    # try:
    #     with open(f"module_summary/{n}/{weightBM25}_{weightSemantic}/{fil}/module_docstrings.json", "r") as f:
    #         module_docstrings = json.load(f)
    #         print("File already exists, skipping iteration.")
    # except FileNotFoundError:
    #     with open(f"top_files/{n}/{weightBM25}_{weightSemantic}.json", "r") as f:
    #         topk = json.load(f)
    #     module_summary(topk, n, weightBM25, weightSemantic)
    #     print("Module-level docstrings generated.")



# file_hit_ratios = {}
# for i in range(1,11):
#     print("-- "*100)
#     score = iterate_main(data_lite, i,0.2,0.8)
#     file_hit_ratios[i] = score

#     print(score)

# with open("FileHits/file_hits_no_summary.json", "w") as f:
#     json.dump(file_hit_ratios, f, indent=4)

# file_hit_ratios = {}
# for i in range(1,11):
#     print("-- "*100)
#     print("Considering top-",i)
#     with_summary = iterate_main_file_hits_with_summary(i, "decoupled_top_files")

#     file_hit_ratios[i] = with_summary

# with open("FileHits/file_hit_with_summary.json", "w") as f:
#     json.dump(file_hit_ratios, f, indent=4)