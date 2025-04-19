import json

async def parse_response(response_stream):
    full_response = ""
    async for chunk in response_stream:
        full_response += chunk
        # Publish chunk to subscribers (e.g., UI or logs) if needed
        # print(f"Streamed chunk: {chunk}")  # Placeholder for info publishing
    # Extract JSON from the end of the response (assuming LLM outputs <action>JSON</action>)
    print("_________________________")
    print('full_response',full_response)
    start = full_response.rfind("{")
    end = full_response.rfind("}") + 1
    json_str = full_response[start:end]
    print('json_str',json_str)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {str(e)}"}