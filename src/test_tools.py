#!/usr/bin/env python3
"""
Test script for LangGraph Chat Application Tools and Agent
"""

import sys
import os
import asyncio
from agents.chat_agent import ChatAgent
from tools.calculator import CalculatorTool
from tools.web_search import WebSearchTool

def test_individual_tools():
    """Test individual tools directly"""
    print("Testing Individual Tools...")
    print("=" * 50)
    
    # Test Code Executor
    print("Testing Code Executor Tool...")
    code_tool = CodeExecutorTool()
    result = code_tool.execute(code="print('Hello, World!')\nx = 5 + 3\nprint(f'Result: {x}')")
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test Calculator
    print("Testing Calculator Tool...")
    calc_tool = CalculatorTool()
    result = calc_tool.execute(expression="2 + 3 * 4")
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test Web Search
    print("Testing Web Search Tool...")
    search_tool = WebSearchTool()
    result = search_tool.execute(query="Python programming language")
    print(f"Result: {result}")
    print("-" * 40)

async def test_chat_agent():
    """Test the chat agent with various requests"""
    print("Testing Chat Agent...")
    print("=" * 50)
    
    agent = ChatAgent()
    
    # Test code execution request
    print("Testing code execution request...")
    response = await agent.process_message("Can you calculate the factorial of 5 using Python?")
    print(f"Response: {response['message']}")
    print(f"Tools used: {response['tools_used']}")
    print("-" * 40)
    
    # Test mathematical calculation request
    print("Testing mathematical calculation request...")
    response = await agent.process_message("What is the square root of 144?")
    print(f"Response: {response['message']}")
    print(f"Tools used: {response['tools_used']}")
    print("-" * 40)
    
    # Test web search request
    print("Testing web search request...")
    response = await agent.process_message("What is machine learning?")
    print(f"Response: {response['message']}")
    print(f"Tools used: {response['tools_used']}")
    print("-" * 40)
    
    # Test general conversation
    print("Testing general conversation...")
    response = await agent.process_message("Hello! How are you?")
    print(f"Response: {response['message']}")
    print(f"Tools used: {response['tools_used']}")
    print("-" * 40)

def test_agent_tools_info():
    """Test getting tools information from agent"""
    print("Testing Agent Tools Info...")
    print("=" * 50)
    
    agent = ChatAgent()
    tools_info = agent.get_tools_info()
    
    for tool_info in tools_info:
        print(f"Tool: {tool_info['name']}")
        print(f"Description: {tool_info['description']}")
        print(f"Parameters: {tool_info['parameters']}")
        print("-" * 40)

async def main():
    """Run all tests"""
    print("LangGraph Chat Application - Agent and Tools Tests")
    print("=" * 60)
    
    try:
        # Test individual tools
        test_individual_tools()
        
        # Test agent tools info
        test_agent_tools_info()
        
        # Test chat agent (requires Google Vertex AI credentials)
        print("\nNote: Chat agent tests require Google Vertex AI credentials.")
        print("If you have credentials set up, uncomment the following line:")
        print("# await test_chat_agent()")
        
        # Uncomment the following line if you have Google Vertex AI credentials set up
        # await test_chat_agent()
        
        print("\nAll individual tool tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 