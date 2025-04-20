import asyncio
from prompt.prompt_generator import generate_prompt
from parser.response_parser import parse_response
from utils.logger import logger
import time

class AgentController:
    def __init__(self, tools, llm_client, context_manager, config):
        self.tools = tools
        self.llm_client = llm_client
        self.context_manager = context_manager
        self.config = config
        self.running = False
        self.paused = False
        self.current_session_id = None
        logger.debug(f"Agent控制器初始化完成: 工具数量={len(tools)}, 协作模式={config.get('collaboration', False)}")

    async def start(self, user_input, context_limit=None):
        self.running = True
        self.paused = False
        # 创建新会话，重置上下文但保留历史记录
        self.current_session_id = self.context_manager.new_session()
        logger.debug(f"创建新会话: ID={self.current_session_id}")
        
        system_prompt = "You are an AI assistant that uses tools to solve tasks."
        logger.debug(f"用户输入: {user_input}")
        logger.info(f"用户指令: {user_input}")
        
        # 记录用户输入到上下文
        self.context_manager.add({"human_input": user_input}, entry_type="human_input")
        
        while self.running and not self.paused:
            start_time = time.time()
            
            prompt = generate_prompt(system_prompt, user_input, self.tools, self.context_manager.get(context_limit))
            logger.debug(f"生成提示完成: 长度={len(prompt)}")
            
            response_stream = self.llm_client.generate(prompt)
            decision = await parse_response(response_stream)
            logger.debug(f"解析响应: {decision}")
            
            # 提取元数据（如token消耗）
            tokens_used = 0
            if "__metadata__" in decision:
                metadata = decision.pop("__metadata__")  # 从决策中移除元数据
                tokens_used = metadata.get("tokens_used", 0)
                logger.debug(f"本次请求消耗token: {tokens_used}")
            
            if decision.get("tool") == "stop":
                self.running = False
                result = decision.get("result", "")
                logger.debug("收到停止指令，完成会话")
                logger.result(result)
                self.context_manager.add({"result": result}, entry_type="stop", tokens_used=tokens_used)
                break

            tool_name = decision.get("tool")
            tool_input = decision.get("input", "")
            logger.debug(f"尝试执行工具: {tool_name}, 输入={tool_input}")
            logger.info(f"执行工具: {tool_name}")
            
            tool = next((t for t in self.tools if t.name == tool_name), None)

            if tool:
                try:
                    tool_start_time = time.time()
                    result = tool.execute(tool_input)
                    tool_elapsed = time.time() - tool_start_time
                    logger.debug(f"工具执行成功: {tool_name}, 耗时={tool_elapsed:.2f}秒")
                    logger.result(f"{tool_name} 结果: {result}")
                    self.context_manager.add(
                        {"tool": tool_name, "input": tool_input, "result": result},
                        entry_type="tool_result", 
                        tokens_used=tokens_used
                    )
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"工具执行错误: {tool_name}, 错误={error_msg}")
                    logger.info(f"错误: {error_msg}")
                    self.context_manager.add(
                        {"tool": tool_name, "input": tool_input, "error": error_msg},
                        entry_type="error",
                        tokens_used=tokens_used
                    )
            else:
                error_msg = f"工具 '{tool_name}' 未找到"
                logger.warning(error_msg)
                logger.info(f"错误: {error_msg}")
                self.context_manager.add({"error": error_msg}, entry_type="error", tokens_used=tokens_used)

            if self.config.get("collaboration", False):
                logger.debug("进入协作模式，等待人工输入")
                human_input = await self._get_human_input()
                logger.info(f"人工输入: {human_input}")
                self.context_manager.add({"human_input": human_input}, entry_type="human_input")
                user_input = human_input  # Update input for next iteration
            
            elapsed_time = time.time() - start_time
            logger.debug(f"本轮交互完成: 耗时={elapsed_time:.2f}秒, token消耗={tokens_used}")
        

    async def _get_human_input(self):
        # Simulate human input (replace with actual input mechanism)
        return input("Human input: ")

    def pause(self):
        self.paused = True
        logger.debug("会话已暂停")

    def resume(self):
        self.paused = False
        logger.debug("会话已恢复")

    def stop(self):
        self.running = False
        logger.debug("会话已停止")
        
    def get_current_session_id(self):
        """返回当前会话ID"""
        return self.current_session_id