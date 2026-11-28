# HJY Week2 Utilities

## 1. Scripts

| Script | Purpose |
|---|---|
| `hjy_blueprint_adapter.py` | Filter frozen 408 questions and build a standard `ExamBlueprint`. |
| `search_rag.py` | Search the week2 TF-IDF baseline corpus. |

## 2. Blueprint Adapter

```bash
python utils/hjy-week2/hjy_blueprint_adapter.py \
  --input "data/frozen/408/seed_questions/408_seed_questions_v1_enriched.jsonl" \
  --subject "数据结构" \
  --year 2024 \
  --output "blueprint_ds_2024.json"
```

## 3. RAG Search

```bash
python utils/hjy-week2/search_rag.py "进程调度算法" --top 5
```

The search index is loaded from:

```text
data/frozen/408/rag/rag_tfidf_index_v1.joblib
```
