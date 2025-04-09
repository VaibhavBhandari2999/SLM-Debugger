# src/patch_utils.py
import re

def extract_changed_file_from_patch(patch):
    matches = re.findall(r'diff --git a/(\S+)', patch)
    modified_files = [file for file in matches]
    return modified_files

def find_missing_strings(subset_list, main_list):
    return [item for item in subset_list if item not in main_list]
