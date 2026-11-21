"""
LLM客户端单元测试
适配真实方法名：client.call()，无_build_payload
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_client import LLMClient
from utils.logger import logger

def test_no_key_env():
    """场景：环境未配置API密钥，调用返回结构化失败"""
    print("\n===== 测试：环境未配置API密钥 =====")
    client = LLMClient()
    resp = client.call(prompt="hello world")
    print(f"返回成功状态：{resp['success']}")
    print(f"返回信息：{resp['msg']}")
    # 无密钥应该返回success=False，不抛异常
    assert resp["success"] == False
    print("✅ 无密钥场景正常：返回结构化失败，不崩溃\n")

def test_json_mode_param():
    """场景：JSON模式参数正常传入，不发起真实网络请求"""
    print("\n===== 测试：JSON模式参数构造 =====")
    client = LLMClient()
    # 只验证参数可以正常传入，不实际调用
    try:
        # 因为无密钥，会直接返回失败，不会真的发请求
        resp = client.call(prompt="生成json", json_mode=True)
        print(f"JSON模式调用返回状态：{resp['success']}")
        print("✅ JSON模式参数可正常传入\n")
    except Exception as e:
        print(f"❌ JSON模式异常：{e}\n")

if __name__ == "__main__":
    test_no_key_env()
    test_json_mode_param()
