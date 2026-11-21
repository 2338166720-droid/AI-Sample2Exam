import os
import sys
import json
from typing import List, Dict

# 项目根目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from utils.llm_client import llm_client
from utils.logger import logger, log_llm_call


class PyTaskSynMinimal:
    """PyTaskSyn 最小复现版本：编程任务生成 + 基础自验证
    适配自研 LLM 客户端与统一日志，空密钥自动降级为模拟样例
    """

    def __init__(self):
        self.module_name = "PyTaskSyn基线"
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_programming_task(self, topic: str = "数据结构", difficulty: str = "medium") -> Dict:
        """生成一道编程任务题
        :param topic: 题目主题，如 链表、栈、动态规划
        :param difficulty: 难度 easy/medium/hard
        :return: 结构化题目数据
        """
        prompt = f"""生成一道Python编程题，主题为{topic}，难度{difficulty}。
严格以JSON格式返回，包含以下字段：
- title: 题目标题
- description: 题目描述
- input_example: 输入示例
- output_example: 输出示例
- test_cases: 2组测试用例，数组格式，每组包含input和output
- difficulty: 难度
- knowledge_point: 对应知识点
"""
        system_prompt = "你是算法出题专家，输出严格合法JSON，不要多余解释。"

        # 调用大模型
        resp = llm_client.call(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True
        )

        if not resp["success"]:
            logger.warning(f"大模型调用失败，使用离线模拟样例: {resp['msg']}")
            return self._get_mock_task(topic, difficulty)

        try:
            task = json.loads(resp["content"])
            task["source"] = "pytasksyn_generated"
            logger.info(f"生成编程任务成功：{task.get('title', '未知标题')}")
            return task
        except json.JSONDecodeError as e:
            logger.error(f"题目JSON解析失败: {e}")
            return self._get_mock_task(topic, difficulty)

    def validate_task(self, task: Dict) -> Dict:
        """基础自验证：字段完整性 + 测试用例格式校验
        对应原基线的验证器最小能力
        """
        required_fields = ["title", "description", "input_example", "output_example", "test_cases"]
        missing = [f for f in required_fields if f not in task]

        is_valid = len(missing) == 0 and isinstance(task.get("test_cases"), list)
        fail_reasons = []
        if missing:
            fail_reasons.append(f"缺失字段: {','.join(missing)}")
        if not isinstance(task.get("test_cases"), list):
            fail_reasons.append("测试用例格式错误")

        confidence = 1.0 if is_valid else 0.5

        result = {
            "is_valid": is_valid,
            "fail_reasons": fail_reasons,
            "confidence": confidence,
            "validate_level": "basic_schema_check"
        }

        logger.info(f"任务验证完成 | 结果: {'通过' if is_valid else '不通过'} | 置信度: {confidence}")
        return result

    def batch_generate(self, topics: List[str], save_file: str = "samples.json") -> List[Dict]:
        """批量生成并保存结果"""
        results = []
        for idx, topic in enumerate(topics):
            logger.info(f"正在生成第 {idx+1}/{len(topics)} 题: {topic}")
            task = self.generate_programming_task(topic=topic)
            validate_res = self.validate_task(task)
            results.append({
                "task": task,
                "validation": validate_res
            })

        save_path = os.path.join(self.output_dir, save_file)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"批量生成完成，共 {len(results)} 题，已保存至 {save_path}")
        return results

    def _get_mock_task(self, topic: str, difficulty: str) -> Dict:
        """离线模拟样例，空密钥环境保证流程可跑通"""
        return {
            "title": f"{topic}基础练习题",
            "description": f"实现一个基础的{topic}操作函数，完成指定功能。",
            "input_example": "[1,2,3,4,5]",
            "output_example": "[5,4,3,2,1]",
            "test_cases": [
                {"input": "[1,2,3]", "output": "[3,2,1]"},
                {"input": "[10,20]", "output": "[20,10]"}
            ],
            "difficulty": difficulty,
            "knowledge_point": topic,
            "source": "offline_mock"
        }
