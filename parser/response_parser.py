import json

async def parse_response(response_stream):
    full_response = ""
    metadata = None
    
    async for chunk in response_stream:
        # 检查是否为元数据字典
        if isinstance(chunk, dict) and "__metadata__" in chunk:
            metadata = chunk["__metadata__"]
            continue
            
        full_response += chunk
        # Publish chunk to subscribers (e.g., UI or logs) if needed
        # print(f"Streamed chunk: {chunk}")  # Placeholder for info publishing
    
    # Extract JSON from the end of the response (assuming LLM outputs <action>JSON</action>)
    start = full_response.rfind("{")
    end = full_response.rfind("}") + 1
    json_str = full_response[start:end]

    try:
        result = json.loads(json_str)
        # 将元数据添加到结果中但不影响原始响应内容
        if metadata:
            result["__metadata__"] = metadata
        return result
    except json.JSONDecodeError as e:
        result = {"error": f"Failed to parse JSON: {str(e)}"}
        if metadata:
            result["__metadata__"] = metadata
        return result