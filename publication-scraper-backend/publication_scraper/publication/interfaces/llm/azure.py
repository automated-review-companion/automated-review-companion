import environ
from langchain_openai import AzureChatOpenAI

env = environ.Env()
environ.Env.read_env()


class AzureLLM:
  
    def __init__(self):
        self.llm: AzureChatOpenAI = None

        self.BASE_URL = f"https://{env('AZURE_RESOURCE_NAME')}.openai.azure.com/"
        self.API_KEY = env('AZURE_API_KEY')
        self.DEPLOYMENT_NAME = env('AZURE_DEPLOYMENT_NAME')

        self.init_llm()


    def init_llm(
      self, 
      max_tokens: int = 2000, 
      model_name: str = "gpt-4"
    ):
        self.llm = AzureChatOpenAI(
                azure_endpoint      = self.BASE_URL,
                openai_api_version  = "2023-05-15",
                deployment_name     = self.DEPLOYMENT_NAME,
                openai_api_key      = self.API_KEY,
                openai_api_type     = "azure",
                max_tokens          = max_tokens,
                model_name          = model_name
            )