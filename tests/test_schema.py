"""
Schema数据模型校验测试，对齐当前core/schemas.py真实规则
options: dict；knowledge_point: str；answer必须存在于options的key；stem长度≥5
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.schemas import MCQuestion, DifficultyLevel
from pydantic import ValidationError

def test_schema_valid():
    print("\n===== 测试：合法样例数据 =====")
    good_data = {
        "knowledge_point": "数组反转",
        "difficulty": DifficultyLevel.MEDIUM,
        "stem": "写出Python实现数组反转的代码",
        "options": {"A":"a = arr[::-1]","B":"for循环","C":"reverse()"},
        "answer": "A",
        "misconception_tags": ["不会切片"]
    }
    try:
        q = MCQuestion(**good_data)
        print("✅ 合法Schema通过校验")
    except Exception as e:
        print(f"❌ 合法数据校验失败：{e}")

def test_schema_invalid():
    print("\n===== 测试：非法数据传入Schema，预期校验失败 =====")
    bad_data = {
        "knowledge_point": "数组反转",
        "difficulty": "super-hard",
        "stem": "短",
        "options": [],
        "answer": "Z"
    }
    try:
        q = MCQuestion(**bad_data)
        print("❌ 校验BUG：非法数据居然通过了")
    except ValidationError as e:
        print(f"✅ 校验正常，捕获异常：{e}")

if __name__ == "__main__":
    test_schema_valid()
    test_schema_invalid()
