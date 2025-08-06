from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# 加载 .env 文件中的环境变量
load_dotenv()


# 你可以将 api_key 传递到模型中（如果支持的话）
agent = Agent(
    model=OpenAIChat(id="moonshotai/kimi-k2:free"),
    instructions="说中文.",
    markdown=True,
)

agent.print_response("hello", stream=True)