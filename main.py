import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from tools.calculator import CalculatorTool
from llm.llm_client import LLMClient
from context.context_manager import ContextManager
from controller.agent_controller import AgentController
from config.config_loader import ConfigLoader

# Load environment variables from local/.env
env_path = Path("local") / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"Warning: {env_path} not found. Using system environment variables or defaults.")

async def main():
    config = ConfigLoader(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),  # Fallback for testing
        api_base_url=os.getenv("OPENAI_API_BASE_URL", None),  # None uses OpenAI default
        collaboration=os.getenv("COLLABORATION", "False").lower() == "true",
        context_db_path=os.getenv("CONTEXT_DB_PATH", "context.db")
    ).get()

    tools = [CalculatorTool()]
    llm_client = LLMClient(config["api_base_url"], config["api_key"], config["model"])
    context_manager = ContextManager(db_path=config["context_db_path"])
    agent = AgentController(tools, llm_client, context_manager, config)

    # 第一次启动 agent
    print("\n=== 开始第一个会话 ===")
    await agent.start("Calculate 3 + 2")
    print(f"当前会话 ID: {agent.get_current_session_id()}" )

    # # 第二次启动 agent（新会话）
    # print("\n=== 开始第二个会话 ===")
    # await agent.start("Calculate 10 * 5")
    # print(f"当前会话 ID: {agent.get_current_session_id()}")

    # # 打印所有会话
    # print("\n=== 所有会话列表 ===")
    # sessions = context_manager.get_sessions()
    # for idx, session_id in enumerate(sessions, 1):
    #     print(f"{idx}. {session_id}")

    # # 回放所有会话的上下文历史
    # print("\n=== 回放所有会话上下文历史 ===")
    # context_manager.replay()

 
if __name__ == "__main__":
    asyncio.run(main())