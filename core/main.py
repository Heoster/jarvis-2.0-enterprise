"""Main entry point for the On-Device Assistant."""

import asyncio
import argparse
import sys

from core.assistant import Assistant
from core.config import load_config
from server.api import LocalServer
from core.logger import get_logger

logger = get_logger(__name__)


async def run_interactive_mode(assistant: Assistant):
    """Run assistant in interactive CLI mode."""
    print("On-Device Assistant - Interactive Mode")
    print("Type 'exit' or 'quit' to stop\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            # Process query
            response = await assistant.process_query(user_input, source="cli")
            
            # Display response
            print(f"\nAssistant: {response.text}")
            
            if response.suggestions:
                print(f"\nSuggestions: {', '.join(response.suggestions)}")
            
            print(f"\n(Confidence: {response.confidence:.2f}, Time: {response.execution_time:.2f}s)\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"\nError: {e}\n")


async def run_server_mode(assistant: Assistant, host: str, port: int):
    """Run assistant in server mode."""
    server = LocalServer(host=host, port=port)
    
    print(f"Starting server at http://{host}:{port}")
    print("Press Ctrl+C to stop\n")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        await server.stop()


async def run_query_mode(assistant: Assistant, query: str):
    """Run a single query and exit."""
    response = await assistant.process_query(query, source="cli")
    
    print(f"Query: {query}")
    print(f"Response: {response.text}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Time: {response.execution_time:.2f}s")


async def show_status(assistant: Assistant):
    """Show assistant status."""
    status = assistant.get_status()
    
    print("Assistant Status:")
    print(f"  Status: {status['status']}")
    print(f"  Uptime: {status['uptime_seconds']:.1f}s")
    print(f"  Personality: {status['config']['personality']}")
    print(f"  Language: {status['config']['language']}")
    print("\nComponents:")
    for component, state in status['components'].items():
        print(f"  {component}: {state}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="On-Device Assistant")
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['start', 'server', 'query', 'status'],
        default='start',
        help='Command to run'
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Query to process (for query command)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Server host (for server command)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Server port (for server command)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize assistant
        assistant = Assistant(config)
        
        # Run command
        if args.command == 'start':
            asyncio.run(run_interactive_mode(assistant))
        
        elif args.command == 'server':
            asyncio.run(run_server_mode(assistant, args.host, args.port))
        
        elif args.command == 'query':
            if not args.query:
                print("Error: --query required for query command")
                sys.exit(1)
            asyncio.run(run_query_mode(assistant, args.query))
        
        elif args.command == 'status':
            asyncio.run(show_status(assistant))
        
        # Shutdown
        asyncio.run(assistant.shutdown())
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
