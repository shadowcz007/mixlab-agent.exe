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
├── main.py                 # Entry point