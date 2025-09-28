#!/usr/bin/env python3
"""
Example script demonstrating how to use the Cerebras SDK with the updated config.

This script shows how to:
1. Import the configuration
2. Create a Cerebras client
3. Make a chat completion request with streaming
4. Handle the response properly

Make sure to set your CEREBRAS_API_KEY environment variable before running.
"""

import os
from typing import Iterator

from config import (
    get_cerebras_client,
    get_cerebras_completion_params,
    validate_config
)


def stream_chat_completion(messages: list[dict[str, str]]) -> Iterator[str]:
    """
    Stream a chat completion using the configured Cerebras client.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Yields:
        str: Content chunks from the streaming response
    """
    try:
        # Get configured Cerebras client
        client = get_cerebras_client()
        
        # Get standard completion parameters
        params = get_cerebras_completion_params()
        
        # Create streaming completion
        stream = client.chat.completions.create(
            messages=messages,
            **params
        )
        
        # Stream the response
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"❌ Error during chat completion: {e}")
        raise


def main() -> None:
    """
    Main function demonstrating Cerebras SDK usage.
    """
    print("🧠 Cerebras SDK Example")
    print("=" * 50)
    
    # Validate configuration
    if not validate_config():
        print("❌ Configuration validation failed!")
        return
    
    print("✅ Configuration validated")
    
    # Check if API key is set
    if not os.getenv("CEREBRAS_API_KEY"):
        print("❌ CEREBRAS_API_KEY environment variable not set!")
        print("   Please set it and try again.")
        return
    
    print("✅ API key found")
    
    # Example messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful coding interview assistant. Provide clear, concise responses."
        },
        {
            "role": "user", 
            "content": "Explain the time complexity of bubble sort algorithm."
        }
    ]
    
    print("\n🤖 Assistant Response:")
    print("-" * 30)
    
    try:
        # Stream the completion
        response_text = ""
        for chunk in stream_chat_completion(messages):
            print(chunk, end="", flush=True)
            response_text += chunk
        
        print("\n" + "-" * 30)
        print(f"✅ Response completed ({len(response_text)} characters)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
