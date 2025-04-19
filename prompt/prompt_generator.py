def generate_prompt(system_prompt, user_input, tools, context):
    tools_desc = "\n".join([f"<tool name='{t.name}'>{t.description}</tool>" for t in tools])
    context_str = "\n".join([f"<entry timestamp='{c['timestamp']}'>{c['data']}</entry>" for c in context])
    prompt = f"""
<system>{system_prompt}</system>
<user>{user_input}</user>
<tools>{tools_desc}</tools>
<context>{context_str}</context>
<thought>Determine the next action based on the input and context. If the request has been fully addressed or the desired result has been obtained, return a "stop" action and the result.</thought>
<action>Return a JSON object: {{"tool": "tool_name", "input": "input_data"}} or {{"tool": "stop"，"result": "result_data"}}</action>
"""
    return prompt