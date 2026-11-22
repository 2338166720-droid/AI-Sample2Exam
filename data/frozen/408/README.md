# 408 冻结数据交付包

本目录只放当前已经冻结的完成物，供团队入库和后续开发使用。工作过程文件、草稿和未冻结版本不放在这里。

## 目录内容

### 1. 主题库

- `408_questions_v2_4_1.jsonl`：408 主数据冻结版，846 题。
- `408_question_schema_v2_2.json`：题目 JSON Schema。
- `408_v2_4_1_freeze_note.md`：主数据冻结说明。
- `408_v2_4_1_release_manifest.csv`：主数据发布清单。
- `408_v2_4_1_spotcheck_report.md`：主数据抽检报告。

### 2. 知识点词表

- `408_knowledge_points_final_v1_locked.jsonl`：110 个知识点的锁定版。
- `408_knowledge_points_final_v1_locked.csv`：知识点锁定版的可读版。
- `408_knowledge_points_lock_manifest.csv`：知识点锁定清单。

### 3. Gold v2 评测集

- `evaluation/408_gold_samples_v2_frozen_v1.jsonl`：50 题 Gold v2 冻结版。
- `evaluation/408_gold_samples_v2_frozen_v1.csv`：Gold v2 冻结版可读文件。
- `evaluation/408_gold_v2_freeze_manifest.csv`：Gold v2 冻结校验清单。
- `evaluation/408_gold_v2_freeze_note.md`：Gold v2 冻结说明。

## 使用约束

1. 本目录内文件是冻结版，后续不要直接修改。
2. 若后续需要修复或新增，应另建 `v1.1` 或 `v2.0`，并保留变更记录。
3. 2026 年题目仍作为 blind test，不参与本轮开发调优。

## 仓库上传建议

1. 建议将本目录整体上传到仓库，例如放到 `data/frozen/408/` 或 `dataset/408/frozen/`。
2. 若仓库限制单文件大小，可把 `408_questions_v2_4_1.jsonl` 放到 Git LFS 或仓库 Release 附件。
3. README、冻结说明、release manifest、知识点锁定清单必须随数据一起上传。
4. 不要上传临时抽检表、模型输出和生成实验结果；这些等实验完成后再单独入库。

## 队友交付要点

1. S2 / S3 拿到主题库、知识点词表和 Gold v2 后，即可开始检索、生成和评测开发。
2. 使用数据时请引用 `408_questions_v2_4_1.jsonl`、`408_knowledge_points_final_v1_locked.jsonl`、`408_gold_samples_v2_frozen_v1.jsonl` 三个主文件。
3. 若需要查看题目可读版，用 CSV；若需要程序读取，用 JSONL。
