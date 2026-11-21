from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ========== 通用枚举 ==========
class QuestionType(str, Enum):
    """题型枚举"""
    MULTIPLE_CHOICE = "multiple_choice"
    PROGRAMMING = "programming"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class BloomLevel(str, Enum):
    """Bloom认知层级枚举"""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ========== 1. 试卷蓝图（解析Agent输出 / 出题Agent输入） ==========
class ExamBlueprint(BaseModel):
    """试卷结构蓝图：从样例卷中学习到的约束条件"""
    exam_title: str = Field(description="试卷名称")
    total_score: int = Field(gt=0, description="试卷总分")
    total_question_count: int = Field(gt=0, description="总题量")
    question_type_ratio: Dict[QuestionType, float] = Field(description="各题型分值占比")
    knowledge_scope: List[str] = Field(description="知识点覆盖范围")
    difficulty_distribution: Dict[DifficultyLevel, float] = Field(description="难度分布占比")
    bloom_distribution: Dict[BloomLevel, float] = Field(default_factory=dict, description="Bloom层级分布")
    time_limit: Optional[int] = Field(default=None, description="考试时长（分钟）")

    @field_validator("question_type_ratio", "difficulty_distribution")
    @classmethod
    def check_ratio_sum(cls, v: Dict):
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"占比之和必须约等于1.0，当前为{total}")
        return v


# ========== 2. 选择题结构（核心题目数据模型，全项目唯一） ==========
class MCQuestion(BaseModel):
    """标准化选择题数据结构"""
    question_id: Optional[str] = Field(default=None, description="题目唯一ID")
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE, description="题型")
    stem: str = Field(min_length=5, description="题干")
    options: Dict[str, str] = Field(description="选项字典，key为选项编号A/B/C/D")
    answer: str = Field(description="正确选项编号")
    knowledge_point: str = Field(description="对应知识点")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="难度等级")
    bloom_level: BloomLevel = Field(default=BloomLevel.UNDERSTAND, description="Bloom认知层级")
    misconception_tag: Optional[str] = Field(default=None, description="对应误解标签（干扰项设计依据）")
    analysis: Optional[str] = Field(default=None, description="答案解析")
    source: Optional[str] = Field(default="ai_generated", description="题目来源")

    @field_validator("options")
    @classmethod
    def check_options_count(cls, v: Dict):
        if len(v) < 2:
            raise ValueError("选项数量不能少于2个")
        return v

    @field_validator("answer")
    @classmethod
    def check_answer_in_options(cls, v: str, info):
        options = info.data.get("options", {})
        if v not in options:
            raise ValueError(f"正确答案{v}不在选项列表中")
        return v


# ========== 3. 验证报告（验证Agent输出） ==========
class ValidationReport(BaseModel):
    """题目自动验证结果"""
    question_id: str
    is_valid: bool = Field(description="是否通过验证")
    schema_valid: bool = Field(description="结构合规性校验结果")
    answer_unique: bool = Field(description="答案唯一性校验结果")
    semantic_duplicate: bool = Field(description="语义重复检测结果")
    knowledge_match: bool = Field(description="知识点匹配校验结果")
    fail_reasons: List[str] = Field(default_factory=list, description="失败原因清单")
    confidence_score: float = Field(ge=0, le=1, description="整体置信度得分")
    validate_time: Optional[str] = Field(default=None, description="验证时间")


# ========== 4. 难度参数（校准Agent输出） ==========
class DifficultyParams(BaseModel):
    """IRT难度校准结果"""
    question_id: str
    difficulty_value: float = Field(ge=-3, le=3, description="IRT难度参数b值")
    discrimination: float = Field(ge=0, le=2, description="区分度参数a值")
    guess_prob: float = Field(ge=0, le=1, default=0.25, description="猜测概率c值")
    predict_accuracy: float = Field(ge=0, le=1, description="预测正确率")
    calibrate_method: str = Field(default="simulated_student_irt", description="校准方法")


# ========== 5. 成套试卷（组卷Agent输出） ==========
class ExamPaper(BaseModel):
    """最终生成的成套试卷"""
    paper_id: Optional[str] = None
    paper_title: str
    total_score: int
    total_questions: int
    average_difficulty: float = Field(ge=0, le=1, description="整卷平均难度")
    questions: List[MCQuestion] = Field(description="题目列表")
    knowledge_coverage: List[str] = Field(description="覆盖知识点清单")
    coverage_rate: float = Field(ge=0, le=1, description="知识点覆盖率")
    generate_time: Optional[str] = None


# ========== 6. 统一接口返回格式（全项目通用） ==========
class BaseResponse(BaseModel):
    """所有模块/接口统一返回结构"""
    success: bool
    data: Optional[Any] = None
    msg: str = "ok"
    confidence: Optional[float] = None
