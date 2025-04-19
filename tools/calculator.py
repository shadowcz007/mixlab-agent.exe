from .tool_base import Tool

class CalculatorTool(Tool):
    @property
    def name(self):
        return "calculator"

    @property
    def description(self):
        return "Performs mathematical calculations (e.g., '2 + 2')."

    def execute(self, input_data):
        try:
            result = eval(input_data)  # Simple eval for demo; use a safer parser in production
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}