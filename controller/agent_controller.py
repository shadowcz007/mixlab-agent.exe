import asyncio
from prompt.prompt_generator import generate_prompt
from parser.response_parser import parse_response

class AgentController:
    def __init__(self, tools, llm_client, context_manager, config):
        self.tools = tools
        self.llm_client = llm_client
        self.context_manager = context_manager
        self.config = config
        self.running = False
        self.paused = False
        self.current_session_id = None

    async def start(self, user_input, context_limit=None):
        self.running = True
        self.paused = False
        # 创建新会话，重置上下文但保留历史记录
        self.current_session_id = self.context_manager.new_session()
        system_prompt = "You are an AI assistant that uses tools to solve tasks."
        
        while self.running and not self.paused:
            prompt = generate_prompt(system_prompt, user_input, self.tools, self.context_manager.get(context_limit))
            
            print('#########################')
            print('#prompt',prompt)
            response_stream = self.llm_client.generate(prompt)
            decision = await parse_response(response_stream)
            print('#########################')

            if decision.get("tool") == "stop":
                self.running = False
                break

            tool_name = decision.get("tool")
            tool_input = decision.get("input", "")
            tool = next((t for t in self.tools if t.name == tool_name), None)

            if tool:
                result = tool.execute(tool_input)
                self.context_manager.add({"tool": tool_name, "input": tool_input, "result": result}, entry_type="tool_result")
            else:
                self.context_manager.add({"error": f"Tool '{tool_name}' not found"}, entry_type="error")

            if self.config.get("collaboration", False):
                human_input = await self._get_human_input()
                self.context_manager.add({"human_input": human_input}, entry_type="human_input")
                user_input = human_input  # Update input for next iteration
        

    async def _get_human_input(self):
        # Simulate human input (replace with actual input mechanism)
        return input("Human input: ")

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False
        
    def get_current_session_id(self):
        """返回当前会话ID"""
        return self.current_session_id