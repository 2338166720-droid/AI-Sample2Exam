# 05 BlueprintAdapter 映射说明

## 1. 目标

把 408 冻结题库中的原始解析结果，转换成后端已经定义好的标准 `ExamBlueprint`。

目标模型字段：

```python
class ExamBlueprint(BaseModel):
    exam_title: str
    total_score: int
    total_question_count: int
    question_type_ratio: dict[str, float]
    knowledge_scope: list[str]
    difficulty_distribution: dict[str, float]
    bloom_distribution: dict[str, float] = {}
    time_limit: int | None = None
```

## 2. 字段映射

| 原始数据 | `ExamBlueprint` 字段 | 处理方式 |
|---|---|---|
| `subject` + `year` | `exam_title` | 生成 `408 2024年真题蓝图` |
| 题目数量 | `total_question_count` | 统计筛选后的题目数 |
| `question_type` | `question_type_ratio` | 统计比例 |
| `knowledge_points[].kp_name` | `knowledge_scope` | 去重后的知识点名称 |
| Gold 标注 `difficulty` | `difficulty_distribution` | 1/2 映射 `easy`，3 映射 `medium`，4/5 映射 `hard` |
| Gold 标注 `bloom_level` | `bloom_distribution` | 映射到六个 Bloom 层级 |

## 3. 题型映射

| 原始题型 | 标准题型 |
|---|---|
| `单选题` | `multiple_choice` |
| `综合应用题` | `short_answer` |

一期建议：

1. 优先只用 `单选题`。
2. `综合应用题` 先保留为参考样本。
3. 编程题由生成模块后续单独扩展。

## 4. 难度映射

| 原始难度 | 标准难度 |
|---|---|
| 1 | `easy` |
| 2 | `easy` |
| 3 | `medium` |
| 4 | `hard` |
| 5 | `hard` |

## 5. Bloom 映射

| 原始中文 | 标准英文 |
|---|---|
| `记忆` | `remember` |
| `理解` | `understand` |
| `应用` | `apply` |
| `分析` | `analyze` |
| `评价` | `evaluate` |
| `创造` | `create` |

## 6. 最小适配函数

```python
from collections import Counter

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

def normalize_ratio(counter: Counter) -> dict[str, float]:
    total = sum(counter.values())
    if total == 0:
        return {}
    return {key: value / total for key, value in counter.items()}

def build_blueprint(questions: list[dict], subject: str, year: int | None = None):
    if year is not None:
        questions = [q for q in questions if q["year"] == year]
    questions = [q for q in questions if q["subject"] == subject and q["question_type"] == "单选题"]

    type_counter = Counter(q["question_type"] for q in questions)
    type_ratio = {
        {"单选题": "multiple_choice", "综合应用题": "short_answer"}.get(key, key): value
        for key, value in normalize_ratio(type_counter).items()
    }

    knowledge_scope = sorted({
        point["kp_name"]
        for question in questions
        for point in question.get("knowledge_points", [])
    })

    difficulty_counter = Counter(DIFFICULTY_MAP.get(q.get("difficulty", 3), "medium") for q in questions)
    bloom_counter = Counter(BLOOM_MAP.get(q.get("bloom_level", "理解"), "understand") for q in questions)

    return {
        "exam_title": f"408 {subject}真题蓝图",
        "total_score": 100,
        "total_question_count": len(questions),
        "question_type_ratio": type_ratio,
        "knowledge_scope": knowledge_scope,
        "difficulty_distribution": normalize_ratio(difficulty_counter),
        "bloom_distribution": normalize_ratio(bloom_counter),
        "time_limit": None,
    }
```

## 7. 蓝图示例

```json
{
  "exam_title": "408 数据结构真题蓝图",
  "total_score": 100,
  "total_question_count": 50,
  "question_type_ratio": {
    "multiple_choice": 1.0
  },
  "knowledge_scope": [
    "单链表基本操作",
    "时间复杂度分析",
    "栈与队列",
    "树与二叉树",
    "排序算法"
  ],
  "difficulty_distribution": {
    "easy": 0.2,
    "medium": 0.5,
    "hard": 0.3
  },
  "bloom_distribution": {
    "understand": 0.3,
    "apply": 0.5,
    "analyze": 0.2
  },
  "time_limit": null
}
```

## 8. 接入建议

1. `BlueprintAdapter` 不要直接依赖网页标签，只依赖 `knowledge_points`。
2. `knowledge_scope` 建议保留 `kp_name`，因为前端和 LLM 更好处理。
3. 如果需要唯一匹配，再转成 `kp_id`。
4. 2026 年数据不参与蓝图统计。

## 9. 可运行脚本

已提供 `hjy_blueprint_adapter.py`，可按学科、年份筛选冻结题库并输出标准 `ExamBlueprint`。

示例：

```bash
python hjy_blueprint_adapter.py \
  --input "408_questions_v2_4_1.jsonl" \
  --subject "数据结构" \
  --year 2024
```
