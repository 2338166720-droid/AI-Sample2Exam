import argparse
import json
import sys
from pathlib import Path

import joblib


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX = REPO_ROOT / "data" / "frozen" / "408" / "rag" / "rag_tfidf_index_v1.joblib"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    bundle = joblib.load(INDEX)
    vectorizer = bundle["vectorizer"]
    matrix = bundle["matrix"]
    records = bundle["records"]
    vec = vectorizer.transform([args.query])
    scores = (matrix @ vec.T).toarray().ravel()
    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)[: args.top]

    results = []
    for i in ranked:
        record = records[i]
        results.append(
            {
                "score": float(scores[i]),
                "chunk_id": record["chunk_id"],
                "question_id": record["question_id"],
                "subject": record["subject"],
                "primary_kp_name": record["primary_kp_name"],
                "difficulty": record.get("difficulty_level", ""),
                "bloom_level": record.get("bloom_level", ""),
                "misconception_tag": record.get("misconception_tag", ""),
                "stem_text": record["stem_text"],
                "answer": record["answer"],
            }
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
