from typing import List, Optional
from pydantic import BaseModel, Field
from core.schemas import (
    ExamBlueprint, MCQuestion, ValidationReport,
    DifficultyParams, ExamPaper, QuestionType, DifficultyLevel
)


# ========== 通用返回结构（全接口统一） ==========
class BaseResponse(BaseModel):
    success: bool
    data: Optional[object] = None
    msg: str = "ok"
    confidence: Optional[float] = None


# ========== 1. 样例卷解析接口 ==========
class ParseExamRequest(BaseModel):
    exam_text: str = Field(description="样例卷纯文本内容")
    subject: str = Field(default="数据结构", description="学科名称")


class ParseExamResponse(BaseResponse):
    data: Optional[ExamBlueprint] = None


# ========== 2. 题目生成接口 ==========
class GenerateQuestionRequest(BaseModel):
    knowledge_points: List[str] = Field(description="知识点列表")
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE, description="题型")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="难度")
    count: int = Field(default=5, ge=1, le=20, description="生成数量")
    misconception_tags: Optional[List[str]] = Field(default=None, description="误解标签列表")
    blueprint_constraint: Optional[ExamBlueprint] = Field(default=None, description="试卷蓝图约束")


class GenerateQuestionResponse(BaseResponse):
    data: Optional[List[MCQuestion]] = None


# ========== 3. 题目验证接口 ==========
class ValidateQuestionRequest(BaseModel):
    question: MCQuestion = Field(description="待验证题目")


class ValidateQuestionResponse(BaseResponse):
    data: Optional[ValidationReport] = None


# ========== 4. 难度校准接口 ==========
class CalibrateDifficultyRequest(BaseModel):
    questions: List[MCQuestion] = Field(description="待校准题目列表")
    method: str = Field(default="simulated_student_irt", description="校准方法")


class CalibrateDifficultyResponse(BaseResponse):
    data: Optional[List[DifficultyParams]] = None


# ========== 5. 约束组卷接口 ==========
class ComposePaperRequest(BaseModel):
    question_pool: List[MCQuestion] = Field(description="题目池")
    blueprint: ExamBlueprint = Field(description="试卷蓝图约束")


class ComposePaperResponse(BaseResponse):
    data: Optional[ExamPaper] = None
