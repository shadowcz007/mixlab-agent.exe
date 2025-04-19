agent/
├── tools/
│   ├── __init__.py
│   ├── tool_base.py       # Tool interface
│   ├── calculator.py      # Example tool
├── prompt/
│   ├── __init__.py
│   ├── prompt_generator.py # Prompt creation logic
├── llm/
│   ├── __init__.py
│   ├── llm_client.py      # LLM API interaction
├── context/
│   ├── __init__.py
│   ├── context_manager.py # Context storage and retrieval
├── controller/
│   ├── __init__.py
│   ├── agent_controller.py # Agent lifecycle management
├── parser/
│   ├── __init__.py
│   ├── response_parser.py # JSON parsing from LLM responses
├── config/
│   ├── __init__.py
│   ├── config_loader.py   # Configuration management
├── utils/
│   ├── __init__.py
│   ├── logger.py          # 日志系统
│   ├── debug_tools.py     # 调试工具
├── main.py                 # Entry point

## 开发与调试模式

项目支持开发模式和生产模式。在开发模式下，会输出更详细的调试信息并记录日志到文件。

### 启用开发模式

在 `local/.env` 文件中设置 `MIXLAB_ENV=development`。

### 调试功能

- 控制台和文件日志
- 函数执行时间分析
- 内存使用跟踪
- 上下文执行时间监控

### 调试工具使用示例

```python
from utils.logger import logger
from utils.debug_tools import profile_function, memory_usage, debug_context, is_dev_mode

# 使用装饰器测量函数执行时间
@profile_function
def my_function():
    # 函数内容
    pass

# 检查内存使用情况
memory_mb = memory_usage()

# 使用上下文管理器调试代码块
with debug_context("处理大量数据"):
    # 代码块内容
    pass

# 条件性调试代码
if is_dev_mode():
    logger.debug("这条信息只在开发模式显示")
```