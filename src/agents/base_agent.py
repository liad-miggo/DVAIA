from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Annotated
from typing_extensions import TypedDict
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from llm_model import LLMModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import logging

logger = logging.getLogger(__name__)

conversation_memory: Dict[str, List[BaseMessage]] = {}

class State(TypedDict):
    """State for the agent graph"""
    messages: Annotated[list, add_messages]


class Agent(ABC):
    """Base agent class using LangGraph patterns with conversation memory"""
    
    def __init__(
        self,
        name: str,
        prompt_file: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
        **kwargs
    ):
        self.name = name
        self.tools = tools or []
        self.llm = LLMModel(**kwargs)
        
        # Load prompt from file if provided
        self.prompt = self._load_prompt(prompt_file) if prompt_file else self.get_default_prompt()
        
        # Build the graph
        self.graph = self._build_graph()
        
        # Conversation memory per user
        
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt from file"""
        try:
            with open(f"agents/prompts/{prompt_file}", "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file {prompt_file} not found, using default prompt")
            return self.get_default_prompt()
    
    @abstractmethod
    def get_default_prompt(self) -> str:
        """Return the default prompt for this agent"""
        pass
    
    def _build_graph(self):
        """Build the LangGraph for this agent"""
        graph_builder = StateGraph(State)
        
        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        def chatbot(state: State):
            """Chatbot node that processes messages"""
            # Add system message if we have a prompt
            messages = state["messages"]
            if self.prompt:
                messages = [SystemMessage(content=self.prompt)] + messages
            
            return {"messages": [llm_with_tools.invoke(messages)]}
        
        # Add nodes
        graph_builder.add_node("chatbot", chatbot)
        
        # Add tool node if tools are available
        if self.tools:
            tool_node = ToolNode(tools=self.tools)
            graph_builder.add_node("tools", tool_node)
            
            # Add conditional edges
            graph_builder.add_conditional_edges(
                "chatbot",
                tools_condition,
                {
                    "tools": "tools",
                    "__end__": END
                }
            )
            graph_builder.add_edge("tools", "chatbot")
        
        # Add entry and exit points
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        
        return graph_builder.compile()
    
    def _get_conversation_history(self, user_id: str) -> List[BaseMessage]:
        """Get conversation history for a user"""
        return conversation_memory.get(user_id, [])
    
    def _set_conversation_history(self, user_id: str, messages: List[BaseMessage]):
        """Sets the conversation history for a user, trimming to the last 20 messages."""
        # The user has made conversation_memory global, so we access it directly.
        conversation_memory[user_id] = messages[-20:]
    
    def clear_conversation_history(self, user_id: str):
        """Clear conversation history for a specific user"""
        if user_id in conversation_memory:
            del conversation_memory[user_id]
    
    async def process_message(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process a user message using the LangGraph with conversation memory"""
        try:
            # Get conversation history for this user
            history = self._get_conversation_history(user_id or "default")
            
            # Create new user message
            user_message = HumanMessage(content=message)
            
            # Create initial state with conversation history + new message
            initial_state = {
                "messages": history + [user_message]
            }
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Update the conversation history with the full result from the graph
            self._set_conversation_history(user_id or "default", result["messages"])
            
            # For the UI response, we only care about the messages generated in this turn.
            # We slice starting after the user's message in the initial state.
            current_turn_messages = result["messages"][len(history) + 1:]
            
            # Extract the final assistant message and tool usage
            final_message = None
            tools_used = []
            tool_execution_details = []
            
            for msg in current_turn_messages:
                if isinstance(msg, AIMessage) and msg.content:
                    final_message = msg.content
                elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Extract tool call information
                    for tool_call in msg.tool_calls:
                        tools_used.append(tool_call['name'])
                        tool_execution_details.append({
                            "tool_name": tool_call['name'],
                            "tool_args": tool_call['args']
                        })
                elif hasattr(msg, 'name') and hasattr(msg, 'content'):
                    # This is a ToolMessage with results
                    for detail in tool_execution_details:
                        if detail["tool_name"] == msg.name:
                            detail["result"] = msg.content
                            break
            
            # Only show interactive mode if tools were actually used in this turn
            is_interactive = len(tools_used) > 0
            
            return {
                "message": final_message or "I've processed your request.",
                "tools_used": tools_used,
                "conversation_id": user_id,
                "interactive": is_interactive,
                "tool_execution": tool_execution_details if is_interactive else []
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message": f"Sorry, I encountered an error: {str(e)}",
                "tools_used": [],
                "conversation_id": user_id,
                "interactive": False
            }
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools"""
        tools_info = []
        for tool in self.tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description or tool.__doc__ or "No description available"
            }
            
            # Try to get schema information if available
            if hasattr(tool, 'args_schema'):
                tool_info["parameters"] = tool.args_schema.schema()
            elif hasattr(tool, 'schema'):
                tool_info["parameters"] = tool.schema()
            else:
                tool_info["parameters"] = {"type": "object", "properties": {}}
            
            tools_info.append(tool_info)
        
        return tools_info 