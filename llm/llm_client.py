from openai import AsyncOpenAI
from utils.logger import logger
import time

class LLMClient:
    def __init__(self, api_base_url, api_key, model):
        logger.debug(f"初始化LLM客户端: 模型={model}, API基础URL={api_base_url or '默认OpenAI URL'}")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base_url if api_base_url else None  # Use default OpenAI URL if not specified
        )
        self.model = model

    async def generate(self, prompt):
        logger.debug(f"发送请求到LLM: 模型={self.model}, 提示长度={len(prompt)}")
        logger.api(f"开始请求LLM: 模型={self.model}")
        start_time = time.time()
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            total_tokens = 0
            progress_marks = [25, 50, 75, 100]  # 用于记录进度的标记点（token数）
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    total_tokens += 1
                    
                    # 仅在开发环境或到达标记点时记录进度
                    if total_tokens in progress_marks:
                        logger.data(f"LLM响应进度: 已生成 {total_tokens} tokens")
                        
                    yield content
            
            elapsed_time = time.time() - start_time
            logger.debug(f"LLM响应完成: 耗时={elapsed_time:.2f}秒, 生成tokens={total_tokens}")
            logger.success(f"LLM响应完成: 共生成 {total_tokens} tokens, 耗时 {elapsed_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"LLM调用错误: {str(e)}")
            raise