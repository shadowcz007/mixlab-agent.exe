import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from tools.calculator import CalculatorTool
from llm.llm_client import LLMClient
from context.context_manager import ContextManager
from controller.agent_controller import AgentController
from config.config_loader import ConfigLoader
from utils.logger import logger
from utils.debug_tools import is_dev_mode, memory_usage

# Load environment variables from local/.env
env_path = Path("local") / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"已加载环境变量: {env_path}")
else:
    logger.warning(f"未找到 {env_path}，使用系统环境变量或默认值。")

async def main():
    logger.debug("正在初始化配置...")
    config = ConfigLoader(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),  # Fallback for testing
        api_base_url=os.getenv("OPENAI_API_BASE_URL", None),  # None uses OpenAI default
        collaboration=os.getenv("COLLABORATION", "False").lower() == "true",
        context_db_path=os.getenv("CONTEXT_DB_PATH", "context.db")
    ).get()
    
    logger.debug(f"配置已加载: 模型={config['model']}, API基础URL={config['api_base_url']}, " +
                 f"协作模式={config['collaboration']}, 上下文数据库路径={config['context_db_path']}")
    
    # 显示运行环境
    env_mode = "开发模式" if is_dev_mode() else "生产模式"
    logger.info(f"Mixlab Agent 启动 ({env_mode})")
    logger.info(f"使用模型: {config['model']}")
    
    if is_dev_mode():
        # 在开发模式下显示内存使用情况
        memory_mb = memory_usage()
        if memory_mb:
            logger.debug(f"初始内存使用: {memory_mb:.2f} MB")

    tools = [CalculatorTool()]
    logger.debug(f"已加载工具: {[tool.name for tool in tools]}")
    logger.info(f"加载工具: {', '.join([tool.name for tool in tools])}")
    
    logger.debug("初始化LLM客户端...")
    llm_client = LLMClient(config["api_base_url"], config["api_key"], config["model"])
    
    logger.debug(f"初始化上下文管理器: {config['context_db_path']}")
    context_manager = ContextManager(db_path=config["context_db_path"])
    
    logger.debug("初始化Agent控制器...")
    agent = AgentController(tools, llm_client, context_manager, config)

    # 第一次启动 agent
    logger.info("\n=== 开始第一个会话 ===")
    await agent.start("Calculate 3 + 2")
    logger.info(f"当前会话 ID: {agent.get_current_session_id()}")

    # # 第二次启动 agent（新会话）
    # logger.info("\n=== 开始第二个会话 ===")
    # await agent.start("Calculate 10 * 5")
    # logger.info(f"当前会话 ID: {agent.get_current_session_id()}")

    # # 打印所有会话
    logger.info("\n=== 所有会话列表 ===")
    sessions = context_manager.get_sessions()
    for idx, session_id in enumerate(sessions, 1):
        logger.info(f"{idx}. {session_id}")

    # # 回放所有会话的上下文历史
    logger.info("\n=== 回放所有会话上下文历史 ===")
    context_manager.replay()
    
    logger.info("Mixlab Agent 运行完成")

 
if __name__ == "__main__":
    asyncio.run(main())