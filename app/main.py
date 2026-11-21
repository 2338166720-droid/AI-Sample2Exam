import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from core.api_models import (
    ParseExamRequest, ParseExamResponse,
    GenerateQuestionRequest, GenerateQuestionResponse,
    ValidateQuestionRequest, ValidateQuestionResponse,
    CalibrateDifficultyRequest, CalibrateDifficultyResponse,
    ComposePaperRequest, ComposePaperResponse,
    BaseResponse
)
from utils.logger import logger

app = FastAPI(
    title="AI-Sample2Exam 自动出题系统 API",
    description="样例卷驱动的可验证自动出题与个性化模考系统接口契约",
    version="0.1.0"
)


# ========== 健康检查 ==========
@app.get("/health", response_model=BaseResponse, summary="服务健康检查")
def health_check():
    logger.info("健康检查请求")
    return BaseResponse(success=True, data={"status": "running"}, msg="ok")


# ========== 1. 样例卷解析 ==========
@app.post("/api/exam/parse", response_model=ParseExamResponse, summary="解析样例卷生成蓝图")
def parse_exam(req: ParseExamRequest):
    logger.info(f"收到样例卷解析请求，学科: {req.subject}")
    return ParseExamResponse(
        success=False,
        data=None,
        msg="接口预留中，解析Agent开发完成后上线",
        confidence=0.0
    )


# ========== 2. 题目生成 ==========
@app.post("/api/question/generate", response_model=GenerateQuestionResponse, summary="批量生成题目")
def generate_questions(req: GenerateQuestionRequest):
    logger.info(f"收到题目生成请求，知识点: {req.knowledge_points}, 数量: {req.count}")
    return GenerateQuestionResponse(
        success=False,
        data=None,
        msg="接口预留中，出题Agent开发完成后上线",
        confidence=0.0
    )


# ========== 3. 题目验证 ==========
@app.post("/api/question/validate", response_model=ValidateQuestionResponse, summary="自动验证题目质量")
def validate_question(req: ValidateQuestionRequest):
    logger.info(f"收到题目验证请求，题干: {req.question.stem[:30]}...")
    return ValidateQuestionResponse(
        success=False,
        data=None,
        msg="接口预留中，验证Agent开发完成后上线",
        confidence=0.0
    )


# ========== 4. 难度校准 ==========
@app.post("/api/question/calibrate", response_model=CalibrateDifficultyResponse, summary="IRT难度校准")
def calibrate_difficulty(req: CalibrateDifficultyRequest):
    logger.info(f"收到难度校准请求，题目数: {len(req.questions)}")
    return CalibrateDifficultyResponse(
        success=False,
        data=None,
        msg="接口预留中，难度校准Agent开发完成后上线",
        confidence=0.0
    )


# ========== 5. 约束组卷 ==========
@app.post("/api/paper/compose", response_model=ComposePaperResponse, summary="按约束生成成套试卷")
def compose_paper(req: ComposePaperRequest):
    logger.info(f"收到组卷请求，题目池数量: {len(req.question_pool)}")
    return ComposePaperResponse(
        success=False,
        data=None,
        msg="接口预留中，组卷Agent开发完成后上线",
        confidence=0.0
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
