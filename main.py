# integrated_pipeline.py
import json
import os
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
from src.iteration import iterate_main
from src.model_utils import get_qwen_model, get_summary_model
from src.docstring_utils import generate_and_insert_docstrings, narrow_top_files
from src.bug_localization import localize_and_generate_patches

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the complete pipeline for bug localization and patch generation")
    parser.add_argument("--k", type=int, default=60, help="Number of top files to initially consider")
    parser.add_argument("--p", type=int, default=10, help="Number of top files to narrow down to")
    parser.add_argument("--n", type=int, default=5, help="Number of top functions to consider for bug fixing")
    parser.add_argument("--bm25", type=float, default=0.8, help="Weight for BM25 ranking in initial file selection")
    parser.add_argument("--semantic", type=float, default=0.2, help="Weight for semantic ranking in initial file selection")
    parser.add_argument("--sem-weight", type=float, default=0.7, help="Weight for semantic ranking in narrowing files")
    parser.add_argument("--output", type=str, default=None, help="Output directory for patches")
    parser.add_argument("--enable-logging", action="store_true", help="Enable logging of LLM inputs and outputs")
    parser.add_argument("--skip-docstrings", action="store_true", help="Skip generating docstrings (use with caution)")
    parser.add_argument("--dataset", type=str, default="data/swe_bench_lite_test.json", help="Path to the dataset")
    
    args = parser.parse_args()
    
    # Configuration
    k = args.k  # Number of top files to initially consider
    p = args.p  # Number of files to narrow down to
    n = args.n  # Number of top functions to consider for bug fixing
    weightBM25 = args.bm25
    weightSemantic = args.semantic
    sem_weight = args.sem_weight
    
    # Set output directory
    if args.output is None:
        output_dir = f"patches/{k}_{p}_{n}/{weightBM25}_{weightSemantic}"
    else:
        output_dir = args.output
    
    # Print configuration
    print("Running pipeline with the following parameters:")
    print(f"Number of initial files (k): {k}")
    print(f"Number of narrowed files (p): {p}")
    print(f"Number of top functions for bug analysis (n): {n}")
    print(f"BM25 weight for initial selection: {weightBM25}")
    print(f"Semantic weight for initial selection: {weightSemantic}")
    print(f"Semantic weight for narrowing files: {sem_weight}")
    print(f"Output directory: {output_dir}")
    print(f"Enable logging: {args.enable_logging}")
    print(f"Skip docstrings: {args.skip_docstrings}")
    print(f"Dataset: {args.dataset}")
    
    # Load the dataset
    try:
        with open(args.dataset) as f:
            data_lite = json.load(f)
        print(f"Loaded dataset with {len(data_lite)} entries")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return
    
    # Step 1: Run initial file ranking to get top k files (By default, k=60)
    top_files_path = f"top_files/{k}/{weightBM25}_{weightSemantic}.json"
    
    try:
        with open(top_files_path, "r") as f:
            top_files_data = json.load(f)
            print(f"Loaded existing top files data from {top_files_path}")
    except FileNotFoundError:
        # If top files haven't been identified yet, run the first phase
        print("Top files data not found. Running file ranking phase...")
        file_hits = iterate_main(data_lite, k, weightBM25, weightSemantic)
        
        # Load the results that were saved by iterate_main
        with open(top_files_path, "r") as f:
            top_files_data = json.load(f)
    
    # Step 2: Generate and insert docstrings for functions and modules
    if not args.skip_docstrings:
        print("\nGenerating docstrings for functions and modules...")
        enhanced_data = generate_and_insert_docstrings(
            top_files_data, 
            k, 
            weightBM25, 
            weightSemantic, 
            enable_logging=args.enable_logging
        )
        
        # Save enhanced data
        enhanced_data_path = f"enhanced_data/{k}/{weightBM25}_{weightSemantic}.json"
        os.makedirs(os.path.dirname(enhanced_data_path), exist_ok=True)
        with open(enhanced_data_path, "w") as f:
            json.dump(enhanced_data, f, indent=4)
        print(f"Saved enhanced data to {enhanced_data_path}")
    else:
        print("\nSkipping docstring generation...")
        # Check if enhanced data already exists
        enhanced_data_path = f"enhanced_data/{k}/{weightBM25}_{weightSemantic}.json"
        try:
            with open(enhanced_data_path, "r") as f:
                enhanced_data = json.load(f)
                print(f"Loaded existing enhanced data from {enhanced_data_path}")
        except FileNotFoundError:
            print("Warning: Enhanced data not found. Using top files data without docstrings.")
            enhanced_data = top_files_data
    
    # Step 3: Narrow down top k files to top p files using docstrings
    print(f"\nNarrowing down top {k} files to top {p} files...")
    narrowed_data = narrow_top_files(
        enhanced_data,
        k,
        p,
        data_lite[0]["problem_statement"],  # Use first issue description as example
        weightBM25=1-sem_weight,
        weightSemantic=sem_weight
    )
    
    # Save narrowed data
    narrowed_data_path = f"narrowed_data/{k}_{p}/{weightBM25}_{weightSemantic}.json"
    os.makedirs(os.path.dirname(narrowed_data_path), exist_ok=True)
    with open(narrowed_data_path, "w") as f:
        json.dump(narrowed_data, f, indent=4)
    print(f"Saved narrowed data to {narrowed_data_path}")
    
    # Step 4: Update the top files in narrowed data
    for row_idx, entry in narrowed_data.items():
        if "top_p_files" in entry:
            narrowed_data[row_idx]["top_n_files"] = entry["top_p_files"]
    
    # Step 5: Run bug localization and patch generation
    print("\nRunning bug localization and patch generation...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    patch_results = localize_and_generate_patches(
        narrowed_data, 
        n, 
        output_dir, 
        enable_logging=args.enable_logging
    )
    
    # Save patch results
    with open(f"{output_dir}/patch_results.json", "w") as f:
        json.dump(patch_results, f, indent=4)
    
    # Create a SWEBench-compatible evaluation file
    swe_bench_patches = []
    for row_idx, result in patch_results.items():
        # Check if a SWEBench patch file has been created
        if "swe_bench_patch_file" in result:
            with open(result["swe_bench_patch_file"], "r") as f:
                swe_bench_patch = json.load(f)
                swe_bench_patches.append(swe_bench_patch)
    
    # Save the SWEBench-compatible evaluation file
    swe_bench_eval_file = os.path.join(output_dir, "swe_bench_evaluation.json")
    with open(swe_bench_eval_file, "w") as f:
        json.dump(swe_bench_patches, f, indent=4)
    
    print(f"\nComplete pipeline finished. Results saved to {output_dir}")
    print(f"Generated SWEBench-compatible evaluation file: {swe_bench_eval_file}")
    print(f"You can now run the SWEBench-lite evaluation pipeline using this file.")

if __name__ == "__main__":
    main()