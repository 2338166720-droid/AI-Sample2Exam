import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data" / "frozen" / "408"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_enriched_seed_questions_are_complete():
    path = DATA_ROOT / "seed_questions" / "408_seed_questions_v1_enriched.jsonl"
    rows = load_jsonl(path)

    assert len(rows) == 100
    required = {
        "id",
        "question_type",
        "stem_text",
        "options",
        "answer",
        "primary_kp_id",
        "difficulty",
        "difficulty_level",
        "bloom_level",
        "misconception_tag_id",
        "misconception_tag",
    }
    assert all(required <= row.keys() for row in rows)
    assert len({row["id"] for row in rows}) == len(rows)


def test_misconception_tags_are_unique_and_aligned():
    path = DATA_ROOT / "misconception_tags" / "misconception_tags_v1.jsonl"
    rows = load_jsonl(path)

    assert len(rows) == 110
    assert len({row["tag_id"] for row in rows}) == len(rows)
    assert len({row["kp_id"] for row in rows}) == len(rows)
    assert all(row["status"] == "draft" for row in rows)


def test_rag_corpus_matches_seed_questions():
    seed_path = DATA_ROOT / "seed_questions" / "408_seed_questions_v1_enriched.jsonl"
    rag_path = DATA_ROOT / "rag" / "rag_corpus_v1.jsonl"
    seed_ids = {row["id"] for row in load_jsonl(seed_path)}
    rag_rows = load_jsonl(rag_path)

    assert len(rag_rows) == 100
    assert {row["question_id"] for row in rag_rows} == seed_ids
    assert all({"difficulty_level", "bloom_level", "misconception_tag"} <= row.keys() for row in rag_rows)


def test_frontend_examples_have_render_fields():
    path = DATA_ROOT / "frontend_examples" / "mc_question_examples_v1.json"
    rows = json.loads(path.read_text(encoding="utf-8"))

    assert len(rows) == 10
    required = {
        "question_id",
        "question_type",
        "stem",
        "options",
        "answer",
        "knowledge_point",
        "difficulty",
        "bloom_level",
        "misconception_tag",
        "analysis",
    }
    assert all(required <= row.keys() for row in rows)
    assert len({row["question_id"] for row in rows}) == len(rows)


def test_blueprints_are_unique():
    path = DATA_ROOT / "blueprints" / "408_paper_blueprints_v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["blueprints"]
    duplicated = [key for key, value in Counter(row["blueprint_id"] for row in rows).items() if value > 1]

    assert len(rows) == 89
    assert duplicated == []
