#!/usr/bin/env python3
"""
LangGraph Chat Application Startup Script
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    """Start the LangGraph Chat Application"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for Google Vertex AI API key
    api_key = os.getenv("GOOGLE_VERTEX_API_KEY")
    if not api_key or api_key == "your_google_vertex_api_key_here":
        print("Error: Google Vertex AI API key not found!")
        print("Please set your Google Vertex AI API key in the .env file:")
        print("1. Copy config.env.example to .env")
        print("2. Edit .env and add your actual Google Vertex AI API key")
        print("3. The API key should be a base64-encoded service account JSON")
        print("4. Run this script again")
        sys.exit(1)
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "443"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    print("Starting LangGraph Chat Application...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"Using model: {model}")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=reload,
            ssl_keyfile="key.pem",
            ssl_certfile="cert.pem",
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 