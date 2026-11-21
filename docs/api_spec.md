# AI-Sample2Exam 接口规范文档

## 1. 接口分层设计
### 1.1 内部 Python 函数接口（模块间调用）
所有 Agent 模块必须遵循统一的函数签名规范，保证模块间可无缝替换与联调。

#### 统一约定
- 每个 Agent 对外暴露 un() 方法
- 入参：对应 Pydantic 请求模型
- 返回值：BaseResponse 统一结构
- 所有异常必须捕获，包装为 success=False 的返回，禁止抛出未处理异常
- 所有调用必须接入 utils.logger 日志组件

#### 示例规范
`python
class QuestionAgent:
    def run(self, req: GenerateQuestionRequest) -> GenerateQuestionResponse:
        # 业务逻辑
        pass
### 1.2 对外 HTTP 接口（前端对接）

- 基于 FastAPI 实现，RESTful 风格
- 统一前缀：/api/
- 统一返回格式：BaseResponse
- 自动生成 Swagger 文档：http://localhost:8000/docs

## 2. 统一返回格式

所有接口响应结构一致：

`
{
    "success": true,
    "data": {},
    "msg": "ok",
    "confidence": 0.92
}
`

表格

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| success | bool | 请求是否成功 |
| data | object | 返回数据，失败时可为 null |
| msg | string | 状态说明，失败时为错误原因 |
| confidence | float | 结果置信度，0-1，可选 |

## 3. 接口清单

表格

| 接口路径 | 方法 | 功能 | 对应 Agent |
| --- | --- | --- | --- |
| /health | GET | 服务健康检查 | - |
| /api/exam/parse | POST | 解析样例卷，生成试卷蓝图 | 解析 Agent |
| /api/question/generate | POST | 按约束批量生成题目 | 出题 Agent |
| /api/question/validate | POST | 多维度自动验证题目 | 验证 Agent |
| /api/question/calibrate | POST | IRT 难度参数校准 | 校准 Agent |
| /api/paper/compose | POST | 按蓝图约束组卷 | 组卷 Agent |

## 4. 统一错误码规范

表格

| 错误码 | 含义 | 触发场景 |
| --- | --- | --- |
| 1001 | 参数校验失败 | 输入不符合 Pydantic 模型约束 |
| 1002 | 蓝图约束不满足 | 生成结果不符合试卷蓝图要求 |
| 2001 | 大模型调用失败 | LLM 接口异常、重试耗尽 |
| 3001 | 题目验证不通过 | 未通过自动验证，不可进入后续流程 |
| 4001 | 组卷失败 | 题目池不足，无法满足约束条件 |
| 5000 | 系统内部错误 | 未知异常 |

## 5. 开发协作约定

1. 新增 / 修改接口必须先更新本文档与 core/api_models.py，同步评审后再开发
2. 前端开发基于当前接口契约进行，数据结构以 Pydantic 模型为准
3. 业务逻辑实现后，替换接口桩内的占位返回即可，接口签名保持不变
4. 所有接口必须记录请求、响应、耗时日志，便于排查问题
