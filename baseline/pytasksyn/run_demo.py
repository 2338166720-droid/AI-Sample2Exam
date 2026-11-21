"""
PyTaskSyn 最小Demo 主运行脚本
正确导入类并实例化，兼容Windows终端无emoji
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
from baseline.pytasksyn.pytasksyn_minimal import PyTaskSynMinimal

def main():
    print("="*60)
    print("PyTaskSyn 基线最小复现 Demo")
    print("="*60)
    runner = PyTaskSynMinimal()
    topics = ["数组反转","链表遍历","栈的括号匹配","二分查找","冒泡排序"]
    output_list = []
    for idx, topic in enumerate(topics):
        task = runner.generate_programming_task(topic=topic, difficulty="medium")
        validate_res = runner.validate_task(task)
        status = "通过" if validate_res["is_valid"] else "未通过"
        output_list.append(task)
        print(f"{idx+1}. {task['title']} | 难度: {task['difficulty']} | 验证: {status}")
    out_dir = os.path.join("baseline","pytasksyn","output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "week1_samples.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_list, f, ensure_ascii=False, indent=2)
    print(f"\n批量生成完成，共 {len(output_list)} 题，已保存至 {out_path}")

if __name__ == "__main__":
    main()
