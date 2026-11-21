"""
PyTaskSyn最小Demo回归测试
不需要大模型密钥，验证降级逻辑、文件输出
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
import json

def test_pytasksyn_demo():
    print("\n===== 启动PyTaskSyn基线Demo回归测试 =====")
    demo_path = "baseline/pytasksyn/run_demo.py"
    result = subprocess.run([sys.executable, demo_path], capture_output=True, text=True)
    print("STDOUT:\n", result.stdout)
    if result.stderr:
        print("STDERR:\n", result.stderr)

    output_file = "baseline/pytasksyn/output/week1_samples.json"
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"\n✅ 文件生成成功，共{len(data)}道题目")
    else:
        print("\n❌ 输出json文件不存在")
        raise FileNotFoundError("基线demo没有输出结果文件")

if __name__ == "__main__":
    test_pytasksyn_demo()
