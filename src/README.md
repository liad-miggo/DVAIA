# AI Chat Application

A modern, AI-powered chat application built with Google Vertex AI, React agents, and FastAPI. This application features a beautiful web interface and integrates multiple tools including code execution, mathematical calculations, and web search capabilities.

## Features

- **Real-time Chat**: WebSocket-based real-time messaging
- **AI Integration**: Powered by Google Vertex AI Gemini models
- **React Agent Pattern**: Single agent with tool integration for enhanced functionality
- **Tool Integration**: Multiple tools available for enhanced functionality
  - **Code Executor**: Safely execute Python code in a sandboxed environment
  - **Calculator**: Perform mathematical calculations and expressions
  - **Web Search**: Search the internet for information
- **Modern UI**: Responsive, beautiful web interface with smooth animations
- **Conversation History**: Persistent conversation management
- **Tool Usage Tracking**: Monitor which tools are used in conversations

## Architecture

The application uses a modular architecture with the following components:

- **FastAPI Backend**: RESTful API and WebSocket endpoints
- **React Agent Pattern**: Single agent with conversation management and tool integration
- **Google Vertex AI**: LLM integration with Gemini models
- **WebSocket Communication**: Real-time bidirectional communication
- **Tool System**: Extensible tool framework for adding new capabilities
- **Frontend**: Modern HTML/CSS/JavaScript interface

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with Vertex AI enabled
- Google Cloud service account with appropriate permissions
- Internet connection for API calls

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-chat-app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud credentials**:
   ```bash
   cp config.env.example .env
   ```
   
   Edit `.env` and add your Google Vertex AI credentials:
   ```
   GOOGLE_VERTEX_API_KEY=your_base64_encoded_service_account_json_here
   LLM_MODEL=gemini-1.5-flash
   ```
   
   To get your service account JSON and encode it:
   ```bash
   # Download service account JSON from Google Cloud Console
   # Then encode it to base64
   cat your-service-account.json | base64
   ```

## Usage

1. **Start the application**:
   ```bash
   python run.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **Start chatting**! The AI will automatically use the appropriate tools based on your requests.

## Tool Examples

### Mathematical Calculations
```
User: "What is the square root of 144?"
AI: [Uses calculate tool]
Result: 12
```

### Web Search
```
User: "What's the current weather in New York?"
AI: [Uses search_web tool]
Result: [Search results with weather information]
```

## Project Structure

```
ai-chat-app/
├── app.py                 # Main FastAPI application
├── llm_model.py           # Google Vertex AI LLM integration
├── run.py                 # Easy startup script
├── test_tools.py          # Tool and agent testing script
├── requirements.txt       # Python dependencies
├── config.env.example     # Environment configuration template
├── README.md             # This file
├── agents/               # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py     # Base agent class with React pattern
│   ├── chat_agent.py     # Main chat agent with tools
│   └── prompts/          # Agent prompts
│       ├── __init__.py
│       └── chat_agent_prompt.txt
├── tools/                # Tool implementations
│   ├── __init__.py
│   ├── base_tool.py      # Base tool class
│   ├── calculator.py     # Mathematical calculator tool
│   └── web_search.py     # Web search tool
└── static/               # Frontend assets
    ├── index.html        # Main HTML page
    ├── styles.css        # CSS styles
    └── script.js         # JavaScript functionality
```

## React Agent Pattern

The application uses a single React agent that:

1. **Receives user input** and adds it to conversation history
2. **Processes the message** using Google Vertex AI with tool calling capability
3. **Executes tools** when the AI determines they're needed
4. **Maintains conversation context** for coherent multi-turn conversations
5. **Returns responses** with information about which tools were used

This approach is simpler and more efficient than complex workflow management while still providing powerful tool integration.

## Adding New Tools

To add a new tool, follow these steps:

1. **Create a new tool class** in the `tools/` directory:
   ```python
   from .base_tool import BaseTool
   
   class MyNewTool(BaseTool):
       def get_description(self) -> str:
           return "Description of what this tool does"
       
       def get_parameters_schema(self) -> Dict[str, Any]:
           return {
               "type": "object",
               "properties": {
                   "parameter_name": {
                       "type": "string",
                       "description": "Parameter description"
                   }
               },
               "required": ["parameter_name"]
           }
       
       def execute(self, **kwargs) -> str:
           # Tool implementation
           return "Tool result"
   ```

2. **Create a tool function** in `agents/chat_agent.py`:
   ```python
   @tool
   def my_new_tool(parameter_name: str) -> str:
       """Description of what this tool does.
       
       Args:
           parameter_name: Parameter description
       
       Returns:
           Tool result
       """
       try:
           tool_instance = MyNewTool()
           return tool_instance.execute(parameter_name=parameter_name)
       except Exception as e:
           return f"Error: {str(e)}"
   ```

3. **Register the tool** in the ChatAgent class:
   ```python
   class ChatAgent(Agent):
       def __init__(self, *args, **kwargs):
           super().__init__(
               name="chat_agent",
               prompt_file="chat_agent_prompt.txt",
               tools=[execute_code, calculate, search_web, my_new_tool],  # Add here
               response_format=None,
               *args,
               **kwargs,
           )
   ```

## Configuration

The application can be configured through environment variables:

- `GOOGLE_VERTEX_API_KEY`: Your base64-encoded Google Cloud service account JSON (required)
- `LLM_MODEL`: Google Vertex AI model name (default: gemini-1.5-flash)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Security Features

- **Code Execution Sandbox**: Safe Python code execution with restricted modules
- **Input Validation**: All inputs are validated before processing
- **Error Handling**: Comprehensive error handling and logging
- **WebSocket Security**: Secure WebSocket connections with proper error handling
- **Google Cloud Security**: Secure authentication using service accounts

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test individual tools
python test_tools.py

# Test with Google Vertex AI (requires credentials)
# Uncomment the agent test in test_tools.py
```

### Code Style

The project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

## Troubleshooting

### Common Issues

1. **Google Vertex AI Authentication Error**:
   - Ensure your service account JSON is correctly base64-encoded
   - Verify the service account has Vertex AI permissions
   - Check that Vertex AI API is enabled in your Google Cloud project

2. **WebSocket Connection Issues**:
   - Check if the server is running on the correct port
   - Ensure no firewall is blocking the connection

3. **Tool Execution Errors**:
   - Check the logs for detailed error messages
   - Verify tool dependencies are installed

### Logs

The application logs important events and errors. Check the console output for debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.

## Acknowledgments

- Built with [Google Vertex AI](https://cloud.google.com/vertex-ai)
- Powered by [Gemini models](https://ai.google.dev/gemini)
- Web framework: [FastAPI](https://fastapi.tiangolo.com/)
- Frontend: Modern HTML/CSS/JavaScript 