# main.py
import json
from src.iteration import iterate_main, iterate_main_file_hits_with_summary
from src.model_utils import get_qwen_model, get_summary_model
from src.docstring_utils import (
    get_files_missing_module_docstrings,
    extract_functions_from_files,
    generate_function_summary,
    insert_docstring_by_class_and_name,
    generate_module_docstring,
    filter_global_missing_functions_docstrings
)

# Load input data
with open("data/swe_bench_lite_test.json") as f:
    data_lite = json.load(f)

# Run the main iteration (for file ranking without summaries)
n = 10
weightBM25 = 0.2
weightSemantic = 0.8
file_hits = iterate_main(data_lite, n, weightBM25, weightSemantic)
print("Total file hits (without summary):", file_hits)

# Load the top files JSON produced in the previous step
with open("results/top_10_files.json", "r") as f:
    t10 = json.load(f)

# Get models for docstring generation
summary_tokenizer, summary_model = get_summary_model()
qwen_tokenizer, qwen_model = get_qwen_model()

global_missing_func_docstring_list = []
for key, entry in t10.items():
    repo_with_underscore = entry["repo_with_underscore"]
    file_list = entry["top_n_files"]
    print("- " * 40)
    print("Processing Row:", key)
    files_missing_module = get_files_missing_module_docstrings(file_list, repo_with_underscore, key)
    print("Files missing module-level docstrings:", files_missing_module)
    functions_missing = extract_functions_from_files(files_missing_module, repo_with_underscore, key)
    global_missing_func_docstring_list.extend(functions_missing)
    print(f"Number of functions missing docstrings: {len(functions_missing)}")

print("Total functions missing docstrings:", len(global_missing_func_docstring_list))
filtered_funcs = filter_global_missing_functions_docstrings(global_missing_func_docstring_list)
with open("filtered_functions_missing_docstrings.json", "w") as f:
    json.dump(filtered_funcs, f, indent=4)

# Generate and insert function-level docstrings
for func in filtered_funcs:
    generated_doc = generate_function_summary(func, summary_tokenizer, summary_model, qwen_tokenizer)
    func['generated_docstring'] = generated_doc
    insert_docstring_by_class_and_name(func["file"], func['class_name'], func["name"], generated_doc)

print("All function-level docstrings processed.")

# Generate module-level docstrings for files missing them
for key, entry in t10.items():
    repo_with_underscore = entry["repo_with_underscore"]
    file_list = entry["top_n_files"]
    for file in get_files_missing_module_docstrings(file_list, repo_with_underscore, None):
        print("Generating module-level docstring for:", file)
        generated_mod_doc = generate_module_docstring(file, repo_with_underscore, qwen_tokenizer, qwen_model)

        print("\n\nGenerated Module Docstring: ", generated_mod_doc)
        print("'"*100)
        #attach the generated doc string to the file
        with open(f"decoupled_top_files/{key}/{repo_with_underscore}/{file}", "r+", encoding="utf-8") as f:
            source_code = f.read()
            f.seek(0)
            f.write(generated_mod_doc + "\n" + source_code)


file_hit_ratios = {}
for i in range(1,11):
    print("-- "*100)
    score = iterate_main(data_lite, i,0.2,0.8)
    file_hit_ratios[i] = score

    print(score)

with open("FileHits/file_hits_no_summary.json", "w") as f:
    json.dump(file_hit_ratios, f, indent=4)

file_hit_ratios = {}
for i in range(1,11):
    print("-- "*100)
    print("Considering top-",i)
    with_summary = iterate_main_file_hits_with_summary(i, "decoupled_top_files")

    file_hit_ratios[i] = with_summary

with open("FileHits/file_hit_with_summary.json", "w") as f:
    json.dump(file_hit_ratios, f, indent=4)