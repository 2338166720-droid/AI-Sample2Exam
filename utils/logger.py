import sys
import os
from loguru import logger
from datetime import datetime

# 日志存放目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 移除默认控制台输出，自定义格式
logger.remove()

# ========== 1. 控制台输出格式 ==========
console_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)
logger.add(
    sys.stdout,
    format=console_format,
    level="INFO",
    enqueue=True
)

# ========== 2. 文件输出格式（按天切割） ==========
file_format = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "{level: <8} | "
    "{name}:{line} | "
    "{message}"
)
log_file = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d')}.log")
logger.add(
    log_file,
    format=file_format,
    level="DEBUG",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
    enqueue=True
)

# ========== 3. 大模型调用专用日志方法 ==========
def log_llm_call(module: str, model: str, input_tokens: int, output_tokens: int,
                prompt_preview: str = "", response_preview: str = "", error: str = None):
    """
    统一记录大模型调用日志
    :param module: 调用模块名，如 "出题Agent" "验证Agent"
    :param model: 调用的模型名称
    :param input_tokens: 输入token数
    :param output_tokens: 输出token数
    :param prompt_preview: 输入片段（前100字即可）
    :param response_preview: 输出片段
    :param error: 异常信息（成功则为None）
    """
    total_tokens = input_tokens + output_tokens
    msg = (f"[LLM调用] 模块:{module} | 模型:{model} | "
           f"输入token:{input_tokens} | 输出token:{output_tokens} | 总计:{total_tokens}")
    if prompt_preview:
        msg += f" | 输入片段:{prompt_preview[:80]}"
    if response_preview:
        msg += f" | 输出片段:{response_preview[:80]}"

    if error:
        logger.error(f"{msg} | 异常:{error}")
    else:
        logger.info(msg)

# ========== 4. 对外导出统一logger ==========
__all__ = ["logger", "log_llm_call"]
