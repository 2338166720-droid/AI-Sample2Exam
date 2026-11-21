import os
import time
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from openai import (
    APIError, APITimeoutError, APIConnectionError, RateLimitError
)
import yaml
from dotenv import load_dotenv

from utils.logger import logger, log_llm_call

# ========== 路径与配置加载 ==========
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config.yaml")
ENV_PATH = os.path.join(ROOT_DIR, ".env")

# 加载YAML参数配置
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    _cfg = yaml.safe_load(f)
LLM_CFG = _cfg["llm"]

# 加载环境变量密钥
load_dotenv(ENV_PATH)


class LLMClient:
    """大模型统一调用客户端：重试、Token统计、JSON校验、日志全接入（懒加载版）"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", LLM_CFG.get("api_key", ""))
        self.base_url = os.getenv("OPENAI_BASE_URL", LLM_CFG.get("base_url"))
        self.default_model = LLM_CFG["default_model"]
        self.timeout = LLM_CFG["timeout"]
        self.max_retry = LLM_CFG["max_retry"]
        self.default_temperature = LLM_CFG["temperature"]

        # 客户端懒加载：第一次调用时再创建，导入不初始化
        self._client = None

        # 全局累计Token统计
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def _get_client(self):
        """延迟创建OpenAI客户端，第一次调用时才实例化"""
        if self._client is None:
            if not self.api_key or self.api_key.strip() == "":
                raise RuntimeError("未配置API密钥，请在.env中填写OPENAI_API_KEY")
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client

    def call(
        self,
        prompt: str,
        system_prompt: str = "你是专业的计算机学科出题助手",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        统一调用入口
        :param prompt: 用户提示词
        :param system_prompt: 系统提示词
        :param model: 指定模型，None则用默认
        :param temperature: 温度，None则用默认
        :param json_mode: 是否强制返回JSON
        :return: 统一返回结构
            {
                "success": bool,
                "content": str,
                "input_tokens": int,
                "output_tokens": int,
                "msg": str
            }
        """
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 无密钥直接返回失败，不抛异常
        if not self.api_key or self.api_key.strip() == "":
            log_llm_call(
                module="llm_client",
                model=model,
                input_tokens=0,
                output_tokens=0,
                prompt_preview=prompt[:80],
                response_preview="",
                error="未配置API密钥"
            )
            return {
                "success": False,
                "content": "",
                "input_tokens": 0,
                "output_tokens": 0,
                "msg": "未配置API密钥，请在.env中填写OPENAI_API_KEY"
            }

        retry_count = 0
        while retry_count < self.max_retry:
            try:
                client = self._get_client()

                # 构造请求参数
                req_kwargs = dict(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                if json_mode:
                    req_kwargs["response_format"] = {"type": "json_object"}

                # 发起请求
                resp = client.chat.completions.create(**req_kwargs)
                input_tokens = resp.usage.prompt_tokens
                output_tokens = resp.usage.completion_tokens
                content = resp.choices[0].message.content.strip()

                # 累计全局Token
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens

                # ========== JSON模式强校验 ==========
                if json_mode:
                    try:
                        json.loads(content)
                    except json.JSONDecodeError as e:
                        log_llm_call(
                            module="llm_client",
                            model=model,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            prompt_preview=prompt[:80],
                            response_preview=content[:80],
                            error=f"JSON解析失败: {str(e)}"
                        )
                        return {
                            "success": False,
                            "content": content,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "msg": f"返回内容非合法JSON: {str(e)}"
                        }

                # ========== 正常返回，记录日志 ==========
                log_llm_call(
                    module="llm_client",
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    prompt_preview=prompt[:80],
                    response_preview=content[:80],
                    error=None
                )
                return {
                    "success": True,
                    "content": content,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "msg": "ok"
                }

            # ========== 可重试异常 ==========
            except (APITimeoutError, APIConnectionError, RateLimitError, APIError) as e:
                retry_count += 1
                wait_sec = 1.5 * retry_count
                logger.warning(
                    f"LLM调用异常（第{retry_count}次重试）: {type(e).__name__}，{wait_sec}s后重试"
                )
                time.sleep(wait_sec)

                if retry_count >= self.max_retry:
                    log_llm_call(
                        module="llm_client",
                        model=model,
                        input_tokens=0,
                        output_tokens=0,
                        prompt_preview=prompt[:80],
                        response_preview="",
                        error=f"重试耗尽: {str(e)}"
                    )
                    return {
                        "success": False,
                        "content": "",
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "msg": f"重试{self.max_retry}次后调用失败: {str(e)}"
                    }

            # ========== 不可重试异常 ==========
            except Exception as e:
                logger.exception("LLM客户端未知异常")
                log_llm_call(
                    module="llm_client",
                    model=model,
                    input_tokens=0,
                    output_tokens=0,
                    prompt_preview=prompt[:80],
                    response_preview="",
                    error=str(e)
                )
                return {
                    "success": False,
                    "content": "",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "msg": f"未知异常: {str(e)}"
                }


# 全局单例，项目内直接导入使用（现在导入不会报错了）
llm_client = LLMClient()
