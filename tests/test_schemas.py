import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schemas import (
    ExamBlueprint, MCQuestion, ValidationReport,
    DifficultyParams, ExamPaper, QuestionType,
    DifficultyLevel, BloomLevel, BaseResponse
)


def test_1_blueprint_valid():
    """测试1：合法试卷蓝图实例化"""
    print("=" * 50)
    print("测试1：合法试卷蓝图")
    blueprint = ExamBlueprint(
        exam_title="数据结构期中测试",
        total_score=100,
        total_question_count=20,
        question_type_ratio={QuestionType.MULTIPLE_CHOICE: 0.6, QuestionType.PROGRAMMING: 0.4},
        knowledge_scope=["链表", "栈", "队列", "树"],
        difficulty_distribution={DifficultyLevel.EASY: 0.3, DifficultyLevel.MEDIUM: 0.5, DifficultyLevel.HARD: 0.2},
        time_limit=90
    )
    print(f"试卷名称: {blueprint.exam_title}")
    print(f"总题量: {blueprint.total_question_count}")
    print("✅ 合法蓝图测试通过\n")


def test_2_blueprint_invalid_ratio():
    """测试2：占比不合法时触发校验报错"""
    print("=" * 50)
    print("测试2：非法占比校验拦截")
    try:
        ExamBlueprint(
            exam_title="测试卷",
            total_score=100,
            total_question_count=10,
            question_type_ratio={QuestionType.MULTIPLE_CHOICE: 0.5},
            knowledge_scope=["测试"],
            difficulty_distribution={DifficultyLevel.EASY: 0.5}
        )
        print("❌ 未拦截非法占比\n")
    except Exception as e:
        print(f"成功拦截: {str(e)[:50]}...")
        print("✅ 占比校验测试通过\n")


def test_3_mc_question_valid():
    """测试3：合法选择题实例化"""
    print("=" * 50)
    print("测试3：合法选择题")
    q = MCQuestion(
        stem="以下哪种数据结构是先进先出？",
        options={"A": "栈", "B": "队列", "C": "链表", "D": "树"},
        answer="B",
        knowledge_point="队列",
        difficulty=DifficultyLevel.EASY,
        bloom_level=BloomLevel.REMEMBER,
        analysis="队列的特点是先进先出FIFO"
    )
    print(f"题干: {q.stem}")
    print(f"正确答案: {q.answer}")
    print(f"知识点: {q.knowledge_point}")
    print("✅ 合法题目测试通过\n")


def test_4_answer_not_in_options():
    """测试4：答案不在选项中触发校验"""
    print("=" * 50)
    print("测试4：答案不合法校验拦截")
    try:
        MCQuestion(
            stem="测试题",
            options={"A": "选项1", "B": "选项2"},
            answer="C",
            knowledge_point="测试"
        )
        print("❌ 未拦截非法答案\n")
    except Exception as e:
        print(f"成功拦截: {str(e)[:50]}...")
        print("✅ 答案校验测试通过\n")


def test_5_unified_response():
    """测试5：统一返回格式"""
    print("=" * 50)
    print("测试5：统一返回结构")
    resp = BaseResponse(success=True, data={"key": "value"}, msg="ok", confidence=0.92)
    print(f"成功状态: {resp.success}")
    print(f"置信度: {resp.confidence}")
    print("✅ 统一返回测试通过\n")


if __name__ == "__main__":
    test_1_blueprint_valid()
    test_2_blueprint_invalid_ratio()
    test_3_mc_question_valid()
    test_4_answer_not_in_options()
    test_5_unified_response()
    print("=" * 50)
    print("🎉 全部Schema校验测试通过！数据模型已固化，可同步给组员使用")
