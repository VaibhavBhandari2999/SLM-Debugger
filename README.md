# Automated Debugging using Small Language Models (SLM)

This repository contains the codebase of the project 'Automated Debugging using Small Language Models (SLM)' developed for CS598-LMZ.

We introduce a robust framework that aims to solve the task of Automated Program Repair using SLMs. Our approach performs significantly better in terms of Fault Localization as compared to the baseline SLM.

We propose a framework to populate function and file summaries to enrich the code repository with Natural Language description of the code and enable semantic similarity to be applied between the code repository and issue description.

## Dataset Used:
SWE-Bench-Lite

## SLM:
Qwen2.5-7B-Instruct

## Embedding Model for Semantic Similarity: 
all-MiniLM-L6-v2

## Metric used for Evaluation:
File Hit Ratio

# Result:

Our approach achieves a file hit ratio of 48.7% for Top-10 files and 29% for Top-1 file.
