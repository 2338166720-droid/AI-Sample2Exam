# 后端接口契约对接说明

更新日期：2026-11-22  
上游来源：`feature/dyh-llm` 分支  
第一周冻结标签：`week1`  
上游最新分支提交：`78c39ef7 fix: 屏蔽基线输出目录，移除已跟踪的数据文件`

## 1. 已接入的接口契约

| 方法 | 路径 | 请求模型 | 响应数据 |
|---|---|---|---|
| GET | `/health` | 无 | 运行状态对象 |
| POST | `/api/exam/parse` | `ParseExamRequest` | `ExamBlueprint` |
| POST | `/api/question/generate` | `GenerateQuestionRequest` | `List[MCQuestion]` |
| POST | `/api/question/validate` | `ValidateQuestionRequest` | `ValidationReport` |
| POST | `/api/question/calibrate` | `CalibrateDifficultyRequest` | `List[DifficultyParams]` |
| POST | `/api/paper/compose` | `ComposePaperRequest` | `ExamPaper` |

所有响应统一采用：

```json
{
  "success": true,
  "data": {},
  "msg": "ok",
  "confidence": 0.92
}
```

前端状态处理以 `success` 为唯一成功判断，以 `msg` 显示业务状态，以 `confidence` 显示可选置信度。不能用非空 `data` 自行推断成功，因为契约桩当前会返回 `success=false, data=null`。

## 2. 原型与契约的字段调整

### 2.1 题目

原型中的三道学生模考题已改为 `MCQuestion` 的最小字段集合：

```text
question_id
question_type
stem
options
answer
knowledge_point
difficulty
bloom_level
misconception_tag
analysis
source
```

`options` 从字符串数组改为 `{"A": "...", "B": "..."}` 映射。科目名称、分值和审核状态不属于 `MCQuestion`，因此在原型中作为独立的展示元数据处理，不向题目对象私增字段。

`data/question_bank/api_mcquestion.seed.json` 保存了 7 道可直接作为当前 `List[MCQuestion]` 演示输入的题目。

### 2.2 难度

后端 `DifficultyLevel` 只有 `easy / medium / hard`。内部种子题库保留 0—1 连续难度估计，当前按以下临时规则映射：

- `0.00—0.30`：`easy`
- `0.30—0.65`：`medium`
- `0.65—1.00`：`hard`

连续难度值和映射后的等级必须同时保留来源，后续以 `DifficultyParams` 的 IRT 参数为准。

### 2.3 知识点和误解标签

当前 `MCQuestion` 只允许一个 `knowledge_point` 和一个 `misconception_tag`。本地种子题库允许多个标签，API 兼容版本暂时选取第一个主标签：

- 主知识点写入 `knowledge_point`；
- 主误解写入 `misconception_tag`；
- 其余关联标签继续保存在内部种子题库，不擅自加入 `MCQuestion`。

### 2.4 综合题

`Q-DS-0003` 是带 0/2/4/6/8/10 分评分量规的综合应用题，不能无损转换成当前 `MCQuestion`，因此暂不进入 `api_mcquestion.seed.json`。

当前 Schema 将 `QuestionType.PROGRAMMING`、`SHORT_ANSWER` 与 `MCQuestion` 共用 `options` 和字符串 `answer`，无法表达代码、测试用例、开放答案和评分量规。建议在下一版 Schema 评审中新增独立题目类型或统一联合模型。

## 3. 当前后端对接阻塞

1. `app/main.py` 中 5 个业务接口仍全部是预留桩，返回 `success=false`。
2. FastAPI 尚未配置 CORS 或静态文件托管。原型直接以文件打开时不能调用 `127.0.0.1:8000`，需要后端增加 `CORSMiddleware` 或由 FastAPI 同时托管前端。
3. `docs/api_spec.md` 定义了错误码 1001—5001，但 `BaseResponse` 没有 `code` 字段，前端目前无法稳定读取错误码，只能显示 `msg`。
4. `ExamBlueprint` 没有 408 四科题目分布、各题型分值或必需章节字段，当前只能把题型分值和知识点范围放入已有字段，不能完整表达整卷结构。
5. 后端尚无人工审核、题目列表、导出和学生学习记录接口。原型中的这些页面继续使用演示状态。

## 4. 前端处理原则

- 不修改 `core/schemas.py` 的字段名。
- 不向 `MCQuestion` 私加 `subject_code`、`score`、`review_status` 等字段。
- API 返回失败时显示后端 `msg`，保留页面当前状态，不伪造成功结果。
- 接口返回题目列表时，先做本地展示映射，再进行作答和审核。
- 后端接口实现后，将原型 mock 函数替换为真实请求，不改变页面主流程。

## 5. 建议下一轮评审事项

1. 在 `BaseResponse` 中增加错误码，或明确由 HTTP 状态码代替。
2. 为 408 综合/算法题建立专用模型。
3. 为蓝图增加 `subject_distribution`、题型分值和必选知识点。
4. 增加 CORS/静态文件托管配置。
5. 冻结前端需要的题目列表、审核记录和导出接口。

