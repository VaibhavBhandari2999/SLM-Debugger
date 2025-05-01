# visualize_results.py
import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path

def load_data(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def plot_file_distribution(patch_results, output_dir):
    """Plot distribution of files for each issue."""
    issue_file_counts = {}
    for row_idx, result in patch_results.items():
        if "patches" in result:
            # Count unique files
            unique_files = set(patch["file_path"] for patch in result["patches"])
            issue_file_counts[row_idx] = len(unique_files)
    
    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(list(issue_file_counts.values()), bins=10, alpha=0.7)
    plt.xlabel('Number of Files')
    plt.ylabel('Number of Issues')
    plt.title('Distribution of Files per Issue')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'file_distribution.png'))
    plt.close()
    
    return issue_file_counts

def plot_function_distribution(patch_results, output_dir):
    """Plot distribution of functions for each issue."""
    issue_function_counts = {}
    for row_idx, result in patch_results.items():
        if "patches" in result:
            issue_function_counts[row_idx] = len(result["patches"])
    
    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(list(issue_function_counts.values()), bins=10, alpha=0.7)
    plt.xlabel('Number of Functions')
    plt.ylabel('Number of Issues')
    plt.title('Distribution of Functions per Issue')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'function_distribution.png'))
    plt.close()
    
    return issue_function_counts

def plot_relevance_scores(patch_results, output_dir):
    """Plot distribution of relevance scores."""
    all_scores = []
    for row_idx, result in patch_results.items():
        if "patches" in result:
            scores = [patch["relevance_score"] for patch in result["patches"]]
            all_scores.extend(scores)
    
    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(all_scores, bins=20, alpha=0.7)
    plt.xlabel('Relevance Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Relevance Scores')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'relevance_scores.png'))
    plt.close()
    
    return all_scores

def analyze_file_extensions(patch_results, output_dir):
    """Analyze file extensions."""
    file_extensions = []
    for row_idx, result in patch_results.items():
        if "patches" in result:
            for patch in result["patches"]:
                file_path = patch["file_path"]
                _, ext = os.path.splitext(file_path)
                if ext:
                    file_extensions.append(ext)
    
    # Count extensions
    ext_counts = Counter(file_extensions)
    
    # Plot bar chart
    plt.figure(figsize=(10, 6))
    ext_df = pd.DataFrame.from_dict(ext_counts, orient='index', columns=['Count']).sort_values('Count', ascending=False)
    ext_df.plot(kind='bar', legend=False)
    plt.xlabel('File Extension')
    plt.ylabel('Count')
    plt.title('Distribution of File Extensions')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'file_extensions.png'))
    plt.close()
    
    return ext_counts

def analyze_common_function_names(patch_results, output_dir):
    """Analyze common function names."""
    function_names = []
    for row_idx, result in patch_results.items():
        if "patches" in result:
            for patch in result["patches"]:
                function_names.append(patch["function_name"])
    
    # Count function names
    name_counts = Counter(function_names)
    
    # Plot top 20 function names
    plt.figure(figsize=(12, 6))
    top_names = dict(name_counts.most_common(20))
    names_df = pd.DataFrame.from_dict(top_names, orient='index', columns=['Count'])
    names_df.plot(kind='bar', legend=False)
    plt.xlabel('Function Name')
    plt.ylabel('Count')
    plt.title('Top 20 Common Function Names')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'common_function_names.png'))
    plt.close()
    
    return name_counts

def analyze_class_distribution(patch_results, output_dir):
    """Analyze distribution of class vs. non-class functions."""
    class_functions = 0
    non_class_functions = 0
    
    for row_idx, result in patch_results.items():
        if "patches" in result:
            for patch in result["patches"]:
                if patch["class_name"]:
                    class_functions += 1
                else:
                    non_class_functions += 1
    
    # Plot pie chart
    plt.figure(figsize=(10, 6))
    plt.pie(
        [class_functions, non_class_functions],
        labels=['Class Methods', 'Standalone Functions'],
        autopct='%1.1f%%',
        startangle=90,
        explode=(0.1, 0),
        shadow=True
    )
    plt.axis('equal')
    plt.title('Distribution of Class Methods vs. Standalone Functions')
    plt.savefig(os.path.join(output_dir, 'class_distribution.png'))
    plt.close()
    
    return class_functions, non_class_functions

def create_summary_report(patch_results, issue_file_counts, issue_function_counts, all_scores, ext_counts, name_counts, class_stats, output_dir):
    """Create a summary report of the results."""
    num_issues = len(patch_results)
    num_functions = sum(issue_function_counts.values())
    avg_functions_per_issue = num_functions / num_issues if num_issues > 0 else 0
    avg_relevance = np.mean(all_scores) if all_scores else 0
    
    # Create report
    report = f"""# Pipeline Results Summary

## Overview
- Total issues processed: {num_issues}
- Total functions patched: {num_functions}
- Average functions per issue: {avg_functions_per_issue:.2f}
- Average relevance score: {avg_relevance:.4f}

## File Statistics
- Total unique file types: {len(ext_counts)}
- Most common file type: {max(ext_counts.items(), key=lambda x: x[1])[0]}
- Issues with multiple files: {sum(1 for count in issue_file_counts.values() if count > 1)}

## Function Statistics
- Class methods: {class_stats[0]} ({class_stats[0]/num_functions*100:.1f}%)
- Standalone functions: {class_stats[1]} ({class_stats[1]/num_functions*100:.1f}%)
- Most common function name: {max(name_counts.items(), key=lambda x: x[1])[0]}

## Distribution of Relevance Scores
- Minimum score: {min(all_scores) if all_scores else 0:.4f}
- Maximum score: {max(all_scores) if all_scores else 0:.4f}
- Median score: {np.median(all_scores) if all_scores else 0:.4f}

## Top 5 File Extensions
{pd.DataFrame.from_dict(dict(Counter(ext_counts).most_common(5)), orient='index', columns=['Count']).to_markdown()}

## Top 10 Function Names
{pd.DataFrame.from_dict(dict(Counter(name_counts).most_common(10)), orient='index', columns=['Count']).to_markdown()}
"""
    
    # Write report
    with open(os.path.join(output_dir, 'summary_report.md'), 'w') as f:
        f.write(report)
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Visualize pipeline results')
    parser.add_argument('--results', type=str, required=True, help='Path to patch results JSON')
    parser.add_argument('--output', type=str, default=None, help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    # Set output directory if not specified
    if args.output is None:
        args.output = os.path.join(os.path.dirname(args.results), 'visualizations')
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Load patch results
    patch_results = load_data(args.results)
    
    # Run visualizations
    print("Generating visualizations...")
    issue_file_counts = plot_file_distribution(patch_results, args.output)
    issue_function_counts = plot_function_distribution(patch_results, args.output)
    all_scores = plot_relevance_scores(patch_results, args.output)
    ext_counts = analyze_file_extensions(patch_results, args.output)
    name_counts = analyze_common_function_names(patch_results, args.output)
    class_stats = analyze_class_distribution(patch_results, args.output)
    
    # Create summary report
    print("Creating summary report...")
    create_summary_report(
        patch_results,
        issue_file_counts,
        issue_function_counts,
        all_scores,
        ext_counts,
        name_counts,
        class_stats,
        args.output
    )
    
    print(f"Visualizations and report saved to {args.output}")

if __name__ == "__main__":
    main()