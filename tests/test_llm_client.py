import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from utils.llm_client import llm_client


def test_1_normal_text():
    """测试1：普通文本生成"""
    print("=" * 50)
    print("测试1：普通文本调用")
    res = llm_client.call(
        prompt="用一句话解释什么是项目反应理论IRT",
        system_prompt="你是教育测量学专家",
        json_mode=False
    )
    print(f"成功状态：{res['success']}")
    print(f"返回内容：{res['content'][:100]}...")
    print(f"消耗Token：入{res['input_tokens']} / 出{res['output_tokens']}")
    assert res["success"], "文本调用失败"
    print("✅ 普通文本测试通过\n")


def test_2_json_mode():
    """测试2：强制JSON返回与校验"""
    print("=" * 50)
    print("测试2：JSON模式调用")
    res = llm_client.call(
        prompt="输出一道数据结构选择题，包含字段：question, options(数组), answer, knowledge_point",
        system_prompt="你是考研408出题助手，严格输出JSON",
        json_mode=True
    )
    print(f"成功状态：{res['success']}")
    if res["success"]:
        data = json.loads(res["content"])
        print(f"解析结果：题干={data['question'][:50]}...")
        print("✅ JSON模式测试通过\n")
    else:
        print(f"❌ JSON模式失败: {res['msg']}\n")


def test_3_token_stat():
    """测试3：全局Token累计统计"""
    print("=" * 50)
    print("测试3：全局Token统计")
    total = llm_client.total_input_tokens + llm_client.total_output_tokens
    print(f"累计输入Token: {llm_client.total_input_tokens}")
    print(f"累计输出Token: {llm_client.total_output_tokens}")
    print(f"累计总Token: {total}")
    assert total > 0, "Token统计未生效"
    print("✅ Token统计测试通过\n")


if __name__ == "__main__":
    test_1_normal_text()
    test_2_json_mode()
    test_3_token_stat()
    print("=" * 50)
    print("🎉 全部测试完成，日志已自动写入 logs/ 目录")
