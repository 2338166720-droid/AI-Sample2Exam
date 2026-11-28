import argparse
import json
import sys
from collections import Counter
from pathlib import Path


TYPE_MAP = {
    "单选题": "multiple_choice",
    "综合应用题": "short_answer",
}

DIFFICULTY_MAP = {
    1: "easy",
    2: "easy",
    3: "medium",
    4: "hard",
    5: "hard",
}

BLOOM_MAP = {
    "记忆": "remember",
    "理解": "understand",
    "应用": "apply",
    "分析": "analyze",
    "评价": "evaluate",
    "创造": "create",
}


def load_questions(path):
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def normalize_ratio(counter):
    total = sum(counter.values())
    if total == 0:
        return {}
    return {key: value / total for key, value in counter.items()}


def build_blueprint(questions, subject=None, year=None):
    if subject:
        questions = [q for q in questions if q.get("subject") == subject]
    if year:
        questions = [q for q in questions if q.get("year") == year]

    if not questions:
        raise ValueError("筛选后没有题目，无法生成蓝图。")

    type_counter = Counter(q.get("question_type", "") for q in questions)
    type_ratio = {
        TYPE_MAP.get(raw_type, raw_type): count
        for raw_type, count in type_counter.items()
    }
    type_ratio = normalize_ratio(type_ratio)

    knowledge_scope = sorted(
        {
            point.get("kp_name", "")
            for question in questions
            for point in question.get("knowledge_points", [])
            if point.get("kp_name")
        }
    )

    difficulty_counter = Counter(
        DIFFICULTY_MAP.get(q.get("difficulty", 3), "medium")
        for q in questions
    )
    bloom_counter = Counter(
        BLOOM_MAP.get(q.get("bloom_level", "理解"), "understand")
        for q in questions
    )

    if subject and year:
        title = f"408 {subject} {year}年真题蓝图"
    elif subject:
        title = f"408 {subject}真题蓝图"
    elif year:
        title = f"408 {year}年真题蓝图"
    else:
        title = "408 真题蓝图"

    return {
        "exam_title": title,
        "total_score": 100,
        "total_question_count": len(questions),
        "question_type_ratio": type_ratio,
        "knowledge_scope": knowledge_scope,
        "difficulty_distribution": normalize_ratio(difficulty_counter),
        "bloom_distribution": normalize_ratio(bloom_counter),
        "time_limit": None,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="冻结主数据 JSONL 路径")
    parser.add_argument("--subject", default=None)
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--output", default=None, help="可选，输出 JSON 文件")
    args = parser.parse_args()

    questions = load_questions(args.input)
    blueprint = build_blueprint(questions, subject=args.subject, year=args.year)
    text = json.dumps(blueprint, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
