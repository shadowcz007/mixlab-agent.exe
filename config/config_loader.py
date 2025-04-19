class ConfigLoader:
    def __init__(self, model="gpt-3.5-turbo", 
                 api_key="your-api-key", 
                 api_base_url="https://api.example.com", 
                 collaboration=False,
                 context_db_path="context.db"):
        self.config = {
            "model": model,
            "api_key": api_key,
            "api_base_url": api_base_url,
            "collaboration": collaboration,
            "context_db_path": context_db_path
        }

    def update(self, **kwargs):
        self.config.update(kwargs)

    def get(self):
        return self.config