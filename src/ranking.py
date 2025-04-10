# src/ranking.py
import os
import nltk
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util
# from src.model_utils import get_codet5_model

nltk.download('punkt', quiet=True)

def rank_files_by_name(file_list, issue_description, n, weightBM25, weightSemantic):
    tokenized_file_list = []
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    file_list_truncated = [file.split("/", 1)[1] for file in file_list]

    for file in file_list_truncated:
        tokens = file.replace("/", " ").split()
        tokenized_file_list.append(nltk.word_tokenize(" ".join(tokens).lower()))

    # BM25 scoring on file names
    bm25 = BM25Okapi(tokenized_file_list)
    query_tokens = nltk.word_tokenize(issue_description.lower())
    bm25_scores = np.array(bm25.get_scores(query_tokens))

    # Semantic similarity scoring
    issue_embedding = semantic_model.encode(issue_description, convert_to_tensor=True)
    file_embeddings = semantic_model.encode(file_list_truncated, convert_to_tensor=True)
    semantic_scores = util.pytorch_cos_sim(issue_embedding, file_embeddings)[0].cpu().numpy()

    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)
    if np.max(semantic_scores) > 0:
        semantic_scores = semantic_scores / np.max(semantic_scores)

    combined_scores = weightBM25 * bm25_scores + weightSemantic * semantic_scores
    ranked_files = sorted(zip(file_list_truncated, combined_scores), key=lambda x: x[1], reverse=True)
    return [file for file, _ in ranked_files[:n]]

def rank_files_by_content(row_index, repo_with_underscore, file_list, issue_description, n, weightBM25, weightSemantic, main_folder):
    tokenized_file_list = []
    file_content_list = []
    for file in file_list:
        file_path = f"{main_folder}/{row_index}/{repo_with_underscore}/{file}"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        file_path_string = f"{repo_with_underscore}/{file}"
        file_path_with_content = file_path_string + "\n" + content
        file_content_list.append(content)
        tokenized_file_list.append(nltk.word_tokenize(file_path_with_content))
    
    bm25 = BM25Okapi(tokenized_file_list)
    query_tokens = nltk.word_tokenize(issue_description.lower())
    bm25_scores = np.array(bm25.get_scores(query_tokens))

    from sentence_transformers import SentenceTransformer, util
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    issue_embedding = semantic_model.encode(issue_description, convert_to_tensor=True)
    file_embeddings = semantic_model.encode(file_content_list, convert_to_tensor=True)
    semantic_scores = util.pytorch_cos_sim(issue_embedding, file_embeddings)[0].cpu().numpy()

    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)
    if np.max(semantic_scores) > 0:
        semantic_scores = semantic_scores / np.max(semantic_scores)

    combined_scores = weightBM25 * bm25_scores + weightSemantic * semantic_scores
    processed_paths = [s.replace(' ', '/').split('/', 1)[1] for s in [f"{repo_with_underscore}/{file}" for file in file_list]]
    ranked_files = sorted(zip(processed_paths, combined_scores), key=lambda x: x[1], reverse=True)
    return [file for file, _ in ranked_files[:n]]
