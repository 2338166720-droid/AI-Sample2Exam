# AI-Sample2Exam Agent 管线设计文档

## 1. 整体流程
`mermaid
flowchart LR
    A[样例卷输入] --> B[解析Agent]
    B --> C[试卷蓝图 ExamBlueprint]
    C --> D[出题Agent]
    D --> E[候选题目列表 MCQuestion]
    E --> F[验证Agent]
    F --> G[验证报告 ValidationReport]
    G --> H{是否通过}
    H -->|是| I[难度校准Agent]
    H -->|否| D
    I --> J[难度参数 DifficultyParams]
    J --> K[组卷Agent]
    K --> L[成套试卷 ExamPaper]
    L --> M[输出 + 反馈回流]
    M --> C

核心闭环：**样例卷理解 → 蓝图约束生成 → 自动验证 → 难度校准 → 约束组卷 → 反馈迭代**

## 2. 各 Agent 职责与输入输出

表格

| Agent 名称 | 核心职责 | 输入数据结构 | 输出数据结构 |
| --- | --- | --- | --- |
| 解析 Agent | 解析样例卷，提取结构、题型、难度、知识点分布，生成试卷蓝图 | 样例卷原始文本 | ExamBlueprint |
| 出题 Agent | 基于蓝图约束、知识点、误解标签，生成标准化候选题目 | ExamBlueprint + 知识点列表 + 误解标签 | List[MCQuestion] |
| 验证 Agent | 多维度校验题目质量：结构、答案唯一性、语义重复、知识点匹配 | MCQuestion | ValidationReport |
| 校准 Agent | 通过模拟学生作答 + IRT 模型，估算题目难度与区分度 | 验证通过的 MCQuestion | DifficultyParams |
| 组卷 Agent | 按约束条件从题目池中选题，生成符合蓝图的成套试卷 | 题目池 + ExamBlueprint 约束 | ExamPaper |

## 3. 数据模型说明

所有数据结构统一定义在 core/schemas.py，基于 Pydantic 实现，全项目唯一引用。

- 强制类型校验：字段类型错误、缺失必填字段直接抛出异常
- 业务规则校验：占比和为 1、答案在选项内、难度范围合法等
- 统一返回格式：所有模块对外输出均采用 BaseResponse 结构

## 4. 统一错误码规范

表格

| 错误码 | 含义 | 说明 |
| --- | --- | --- |
| 1001 | 参数校验失败 | 输入字段不符合 Schema 要求 |
| 1002 | 蓝图约束不满足 | 生成结果不符合试卷蓝图约束 |
| 2001 | 大模型调用失败 | LLM 接口调用异常、重试耗尽 |
| 3001 | 题目验证不通过 | 未通过自动验证，不可进入后续流程 |
| 4001 | 组卷失败 | 题目池不足，无法满足约束条件 |
| 5001 | 系统内部错误 | 未知异常 |

## 5. 协作约定

1. 所有 Agent 开发必须引用 core.schemas 中的数据类，禁止私自定义同名字段
2. 新增 / 修改字段必须三人共同评审，同步更新 Schema 与文档
3. 所有模块输出必须包含 success 字段，失败必须附带 msg 原因
4. 所有跨模块调用必须接入统一日志组件 utils.logger
