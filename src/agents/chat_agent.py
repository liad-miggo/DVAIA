from langchain_core.tools import tool
from agents.base_agent import Agent
from tools.calculator import CalculatorTool
from tools.web_search import WebSearchTool
import logging

logger = logging.getLogger(__name__)


@tool
def calculate(expression: str, precision: int = 6) -> str:
    """Perform mathematical calculations including basic arithmetic, trigonometry, logarithms, and more.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sin(pi/2)', 'sqrt(16)')
        precision: Number of decimal places for the result (default: 6)
    
    Returns:
        The calculated result
    """
    try:
        calc_tool = CalculatorTool()
        return calc_tool.execute(expression=expression, precision=precision)
    except Exception as e:
        logger.error(f"Error in calculate tool: {e}")
        return f"Error calculating expression: {str(e)}"


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for information using DuckDuckGo.
    
    Args:
        query: The search query to look up on the web
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Formatted search results
    """
    try:
        search_tool = WebSearchTool()
        return search_tool.execute(query=query, max_results=max_results)
    except Exception as e:
        logger.error(f"Error in search_web tool: {e}")
        return f"Error performing web search: {str(e)}"


class ChatAgent(Agent):
    def __init__(self, client_id: str, *args, **kwargs):
        self.client_id = client_id
        super().__init__(
            name="chat_agent",
            tools=[calculate, search_web],
            *args,
            **kwargs,
        )
    
    def get_default_prompt(self) -> str:
        return f"""You are a helpful AI assistant with access to various tools to help users with their requests.

        You are working with a user with the id {self.client_id}.

AVAILABLE TOOLS:
1. calculate: Perform mathematical calculations (arithmetic, trigonometry, logarithms, etc.)
2. search_web: Search the web for current information using DuckDuckGo

When a user asks you to:
- Perform calculations: Use the calculate tool
- Find information: Use the search_web tool
- General questions: Respond directly with helpful information

Always be helpful, accurate, and explain your reasoning. If you use tools, explain what you're doing and present the results clearly.

Remember to:
- Keep responses concise but informative
- Use tools when they would be helpful
- Explain complex concepts in simple terms
- Be friendly and professional""" 