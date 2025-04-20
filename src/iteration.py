# src/iteration.py
import os
import json
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from src.repo_utils import clone_repo_checkout_commit, create_file_structure
from src.ranking import rank_files_by_name
from src.patch_utils import extract_changed_file_from_patch, find_missing_strings

def iterate_main(data_lite, n, weightBM25, weightSemantic):
    no_of_files_present_in_top_n = 0
    dict_of_top_n_file_structure_lists = {}
    
    for row_idx, entry in enumerate(data_lite):
        repo = entry.get("repo", "N/A")
        repo_with_underscore = repo.replace("/", "_")
        base_commit = entry.get("base_commit", "N/A")
        issue_description = entry.get("problem_statement", "N/A")
        patch = entry.get("patch", "N/A")
    
        print("----------------------------------")
        print("Row Index: ", row_idx)
    
        checkout_status = clone_repo_checkout_commit(repo, base_commit)
    
        file_structure_list = create_file_structure(f"swe_bench_repos/{repo_with_underscore}")
        print("Number of files in repo: ", len(file_structure_list))
    
        top_n_files = rank_files_by_name(file_structure_list, issue_description, n, weightBM25, weightSemantic)
    
        main_file_path = Path(f"decoupled/{n}/{weightBM25}_{weightSemantic}/{row_idx}/{repo_with_underscore}")
        os.makedirs(main_file_path, exist_ok=True)
        
        for file in top_n_files:
            file_path = main_file_path / file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            src_path = Path(f"swe_bench_repos/{repo_with_underscore}/{file}")
            file_content = src_path.read_text()
            file_path.write_text(file_content)
            print("Writing file:", file_path)
    
        dict_of_top_n_file_structure_lists[row_idx] = {
            "repo_with_underscore": repo_with_underscore,
            "top_n_files": top_n_files,
            "repo": repo,
            "base_commit": base_commit,
            "patch": patch,
            "issue_description": issue_description
        }
    
        ground_truth_modified_files = extract_changed_file_from_patch(patch)
        print("\nGround Truth Modified Files: ", ground_truth_modified_files)
    
        if set(ground_truth_modified_files).issubset(set(top_n_files)):
            print("\nFile Present")
            no_of_files_present_in_top_n += 1
        else:
            print("\nFile Absent")
            print("Missing Files: ", find_missing_strings(ground_truth_modified_files, top_n_files))
    
    with open(f"top_files/{n}_files_{weightBM25}_{weightSemantic}.json", "w") as f:
        json.dump(dict_of_top_n_file_structure_lists, f, indent=4)
    
    return no_of_files_present_in_top_n



def iterate_main_file_hits_with_summary(n, main_folder, data_lite, t10):
    file_hit_value = 0
    hits = 0
    
    for row_idx, entry in enumerate(data_lite):
        repo = entry.get("repo", "N/A")
        repo_with_underscore = repo.replace("/", "_")
        base_commit = entry.get("base_commit", "N/A")
        issue_description = entry.get("problem_statement", "N/A")
        patch = entry.get("patch", "N/A")
    
        print("-"*100)
        print(f"Row Index: {row_idx}")
        print(f"Repo: {repo}")
        print(f"Base Commit: {base_commit}")
        top_n_files = t10.get(str(row_idx), {}).get("top_n_files", [])
        print(f"Top N Files: {top_n_files}")
        print("-"*100, "\n\n")
    
        from src.ranking import rank_files_by_content
        target_files = rank_files_by_content(row_idx, repo_with_underscore, top_n_files, issue_description, n, 0.8, 0.2, main_folder)
        print("\nTarget Files: ", target_files)
        actual_target = extract_changed_file_from_patch(patch)
        print("\nGround Truth Modified Files: ", actual_target)
    
        if len(actual_target) > 1:
            hits += 1
       
        if all(item in target_files for item in actual_target):
            file_hit_value += 1
            print("File Hit")
    
    print("Number of file hits: ", file_hit_value)
    print("File hit percentage: ", file_hit_value / 300)
    print("Multi-File Patch count: ", hits)
    return file_hit_value
