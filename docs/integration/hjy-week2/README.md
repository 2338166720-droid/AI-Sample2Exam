# HJY Week2 Data Integration Package

负责人：胡金燕 / S1  
日期：2026-11-28  
用途：支撑生成 Agent、验证模块、组卷模块和前端页面联调。

## 1. 目录职责

```text
data/frozen/408/
  blueprints/                 试卷蓝图
  seed_questions/             种子题与增强种子题
  misconception_tags/         误解标签库
  rag/                        RAG 语料和 TF-IDF 索引
  frontend_examples/          前端可直接使用的 MC 示例

docs/integration/hjy-week2/    接口契约、数据说明和校验报告
utils/hjy-week2/               可运行 Adapter 与检索脚本
tests/hjy-week2/               数据规模与字段一致性测试
```

## 2. 本周交付内容

| 内容 | 数量 | 说明 |
|---|---:|---|
| 锁定知识点 | 110 | 上周冻结，本周继续作为统一口径 |
| 误解标签 | 110 | 与知识点一一对应，状态为 `draft` |
| 种子题 | 100 | 四门课各 25 题，全部为无图单选题 |
| 增强种子题 | 100 | 补齐难度、Bloom 层级和误解标签 |
| 试卷蓝图 | 89 | 按课程和年份抽取，2026 年不参与统计 |
| RAG 语料 | 100 | 来自种子题，带课程、知识点、难度、Bloom、误解标签 |
| 前端示例 | 10 | 用于第一轮页面联调 |

## 3. 对接需求覆盖

| 需求 | 覆盖文件 |
|---|---|
| 样例卷解析后的实际输出字段清单 | `01_样例卷解析字段清单.md` |
| 知识点库的命名规范与示例 | `02_知识点命名规范与示例.md` |
| 误解标签库的结构与示例 | `03_误解标签库结构与示例.md` |
| 解析模块的调用方式与入参出参 | `04_解析模块调用契约.md` |

## 4. 快速使用

### 4.1 生成试卷蓝图

```bash
python utils/hjy-week2/hjy_blueprint_adapter.py \
  --input "data/frozen/408/seed_questions/408_seed_questions_v1_enriched.jsonl" \
  --subject "数据结构" \
  --year 2024 \
  --output "blueprint_ds_2024.json"
```

### 4.2 检索种子题语料

```bash
python utils/hjy-week2/search_rag.py "进程调度算法" --top 5
```

## 5. 字段约定

### 知识点

锁定知识点词表顶层使用：

```json
{
  "kp_id": "KP-001",
  "name": "时间复杂度分析"
}
```

题目和生成记录里常用 `kp_name`。  
`kp_name` 必须等于锁定词表里的 `name`。

### 误解标签

出题请求建议使用 `tag_id`：

```json
{
  "knowledge_points": ["KP-006"],
  "misconception_tags": ["MIS-DS-006"],
  "count": 5
}
```

没有精确误解标签时传空数组，不要编造标签 ID。

## 6. 当前限制

1. 本周种子题只包含单选题，还没有编程题。
2. 部分难度默认为 `medium`，后续需要教师评审或 IRT 校准。
3. 误解标签偏模板化，后续要结合生成失败案例细化。
4. RAG 仍是 TF-IDF 基线，不是最终语义检索方案。
