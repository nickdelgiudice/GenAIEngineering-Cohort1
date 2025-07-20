from phi.agent import Agent
from phi.tools.serpapi_tools import SerpApiTools
from dotenv import load_dotenv
import os

load_dotenv()

serp_key = os.getenv("SERPAPI_API_KEY")
serp_tool = SerpApiTools(api_key=serp_key)

agent = Agent(tools=[serp_tool])
agent.print_response("Please Find all Dell Precision 7560 configurations and create a table for comparison", markdown=True)
