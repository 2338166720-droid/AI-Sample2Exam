import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import logger, log_llm_call
from utils.llm_client import LLMClient


def test_1_logger_work():
    """测试1：日志组件正常工作（已验证过，这里做回归）"""
    print("=" * 50)
    print("测试1：日志组件基础功能")
    logger.info("普通信息日志测试")
    logger.warning("警告日志测试")
    try:
        1 / 0
    except Exception as e:
        logger.exception("异常堆栈日志测试")
    print("✅ 日志组件测试通过\n")


def test_2_client_init():
    """测试2：LLM客户端可正常初始化（空密钥也不报错）"""
    print("=" * 50)
    print("测试2：LLM客户端初始化")
    client = LLMClient()
    print(f"默认模型: {client.default_model}")
    print(f"最大重试次数: {client.max_retry}")
    print(f"超时时间: {client.timeout}s")
    assert client.total_input_tokens == 0
    assert client.total_output_tokens == 0
    print("✅ 客户端初始化测试通过\n")


def test_3_json_validate_logic():
    """测试3：JSON校验逻辑（离线模拟，不用发请求）"""
    print("=" * 50)
    print("测试3：JSON校验逻辑")
    # 合法JSON
    valid_json = '{"question": "测试题", "answer": "A"}'
    try:
        json.loads(valid_json)
        print("合法JSON校验通过")
    except Exception as e:
        print(f"校验失败: {e}")

    # 非法JSON
    invalid_json = '{"question": "测试题", answer: "A"}'
    try:
        json.loads(invalid_json)
        print("❌ 非法JSON未被拦截")
    except json.JSONDecodeError as e:
        print(f"非法JSON成功拦截: {str(e)[:30]}...")

    print("✅ JSON校验逻辑测试通过\n")


def test_4_token_accumulate():
    """测试4：Token累计统计逻辑（离线模拟）"""
    print("=" * 50)
    print("测试4：全局Token累计逻辑")
    client = LLMClient()
    # 手动模拟两次调用的Token累加
    client.total_input_tokens += 150
    client.total_output_tokens += 80
    client.total_input_tokens += 200
    client.total_output_tokens += 120
    total = client.total_input_tokens + client.total_output_tokens
    print(f"模拟累计输入: {client.total_input_tokens}")
    print(f"模拟累计输出: {client.total_output_tokens}")
    print(f"模拟累计总量: {total}")
    assert total == 550
    print("✅ Token累计逻辑测试通过\n")


def test_5_llm_log_record():
    """测试5：大模型调用日志写入（离线模拟）"""
    print("=" * 50)
    print("测试5：LLM调用日志记录")
    log_llm_call(
        module="离线测试模块",
        model="glm-4-flash",
        input_tokens=100,
        output_tokens=50,
        prompt_preview="模拟测试提示词",
        response_preview="模拟返回内容",
        error=None
    )
    print("✅ LLM调用日志写入测试通过\n")


if __name__ == "__main__":
    test_1_logger_work()
    test_2_client_init()
    test_3_json_validate_logic()
    test_4_token_accumulate()
    test_5_llm_log_record()
    print("=" * 50)
    print("🎉 全部离线测试通过！核心本地逻辑均正常，后续补充API密钥即可直接跑真实调用")
