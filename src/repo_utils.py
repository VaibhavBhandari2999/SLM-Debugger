# src/repo_utils.py
import os
import subprocess
from pathlib import Path

def clone_repo_checkout_commit(repo, base_commit):
    repo_path = repo.replace("/", "_")
    repo_local_path = os.path.join("swe_bench_repos", repo_path)

    if os.path.exists(repo_local_path):
        print(f"Repository {repo} already exists. Skipping clone...")
        subprocess.run(["git", "reset", "--hard"], cwd=repo_local_path)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_local_path)
    else:
        print(f"Cloning repo: {repo}")
        subprocess.run(["git", "clone", f"https://github.com/{repo}.git", repo_local_path])

    print(f"Checking out commit {base_commit} for {repo}...")
    subprocess.run(["git", "fetch", "--all"], cwd=repo_local_path)
    result = subprocess.run(["git", "checkout", base_commit], cwd=repo_local_path)
    if result.returncode != 0:
        print(f"Error checking out commit {base_commit} for {repo}:\n{result.stderr}")
        return False

    subprocess.run(["git", "reset", "--hard", base_commit], cwd=repo_local_path)
    print("Successfully checked out repo at base_commit")
    return True

def create_file_structure(repo_path):
    print("Repo path is: ", repo_path)
    file_list = []
    exclude_dirs = {".git", ".github", ".vscode", "__pycache__", "node_modules", "dist", "build", ".pyinstaller"}
    exclude_extensions = {".yml", ".yaml", ".md", ".rst", ".toml", ".config", ".cfg", ".ini", ".txt", ".tex", ".dat", ".gz", ".in", ".csv", ".ecsv", ".css", ".png", ".fits", ".hdf5", ".xsd", ".xml", ".bz2", ".hdr"}
    include_extensions = {".py"}
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.startswith("."):
                continue
            file_ext = os.path.splitext(file)[1]
            if file_ext in include_extensions:
                full_path = os.path.join(root, file)
                # Remove the common prefix (e.g. "swe_bench_repos/") for downstream processing
                file_list.append(full_path[len("swe_bench_repos/"):])
    
    return file_list
