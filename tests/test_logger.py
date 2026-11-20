# ========== 新增：修复导入路径 ==========
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# =======================================

from utils.logger import logger, log_llm_call

# 普通日志
logger.info("项目初始化成功")
logger.debug("调试信息，只写入文件不打印控制台")
logger.warning("警告信息")

# 大模型调用日志
log_llm_call(
    module="测试模块",
    model="gpt-3.5-turbo",
    input_tokens=120,
    output_tokens=80,
    prompt_preview="请生成一道选择题",
    response_preview="题干：以下哪个是正确选项"
)

# 异常日志（自动带堆栈）
try:
    1 / 0
except Exception as e:
    logger.exception("测试异常捕获")
