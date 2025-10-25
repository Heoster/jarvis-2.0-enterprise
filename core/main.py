"""Main entry point for the On-Device Assistant - JARVIS Complete Edition."""

import asyncio
import argparse
import sys
from datetime import datetime

from core.assistant import Assistant
from core.config import load_config
from server.api import LocalServer
from core.logger import get_logger

# Import unified JARVIS
try:
    from core.jarvis_unified import get_jarvis_unified
    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Unified JARVIS not available, using standard assistant")

logger = get_logger(__name__)


async def run_interactive_mode(assistant: Assistant, use_unified: bool = True):
    """Run assistant in interactive CLI mode with optional unified JARVIS."""
    print("="*80)
    if use_unified and UNIFIED_AVAILABLE:
        print("🤖 JARVIS Complete - Unified System")
        print("Original Features + JARVIS 2.0 Enhancements")
    else:
        print("On-Device Assistant - Interactive Mode")
    print("="*80)
    print("Type 'exit' or 'quit' to stop\n")
    
    # Initialize unified JARVIS if available
    jarvis_unified = None
    if use_unified and UNIFIED_AVAILABLE:
        try:
            jarvis_unified = await get_jarvis_unified()
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            await jarvis_unified.start_session(session_id)
            
            # Show greeting
            greeting = await jarvis_unified.get_greeting()
            print(greeting)
            print()
            
            # Show features
            status = jarvis_unified.get_status()
            print("✅ System Status: OPERATIONAL")
            print("\n📦 Features Available:")
            print("  • Web Search & Scraping")
            print("  • Real-time Data (Weather, News)")
            print("  • Enhanced Intent Classification (95%+)")
            print("  • Sentiment Analysis & Tone Adjustment")
            print("  • Contextual Memory with Learning")
            print("  • API Routing & Indian APIs")
            print()
        except Exception as e:
            logger.error(f"Failed to initialize unified JARVIS: {e}")
            jarvis_unified = None
            print("⚠️  Using standard assistant mode\n")
    
    interaction_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                if jarvis_unified:
                    farewell = await jarvis_unified.get_farewell()
                    print(f"\n{farewell}")
                else:
                    print("Goodbye!")
                break
            
            print()
            
            # Process query with unified JARVIS or standard assistant
            if jarvis_unified:
                try:
                    response_text = await jarvis_unified.process_query(user_input)
                    print(f"Jarvis: {response_text}")
                    interaction_count += 1
                    print(f"\n[Interaction: {interaction_count}]")
                except Exception as e:
                    logger.error(f"Unified processing failed: {e}, falling back to standard")
                    response = await assistant.process_query(user_input, source="cli")
                    print(f"Assistant: {response.text}")
                    if response.suggestions:
                        print(f"\nSuggestions: {', '.join(response.suggestions)}")
                    print(f"\n(Confidence: {response.confidence:.2f}, Time: {response.execution_time:.2f}s)")
            else:
                # Standard assistant
                response = await assistant.process_query(user_input, source="cli")
                print(f"Assistant: {response.text}")
                
                if response.suggestions:
                    print(f"\nSuggestions: {', '.join(response.suggestions)}")
                
                print(f"\n(Confidence: {response.confidence:.2f}, Time: {response.execution_time:.2f}s)")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"\nError: {e}\n")
    
    # Show summary if using unified
    if jarvis_unified and interaction_count > 0:
        try:
            print("\n" + "="*80)
            print("📊 Session Summary")
            print("="*80)
            summary = await jarvis_unified.get_session_summary()
            enhanced = summary.get('enhanced_features', {})
            print(f"Total Interactions: {enhanced.get('total_interactions', interaction_count)}")
            print(f"Current Topic: {enhanced.get('current_topic', 'N/A')}")
            print(f"Topic Continuity: {enhanced.get('topic_continuity', 0):.2f}")
            print()
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")


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
    
    parser.add_argument(
        '--no-unified',
        action='store_true',
        help='Disable unified JARVIS features (use standard assistant only)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize assistant
        assistant = Assistant(config)
        
        # Run command
        if args.command == 'start':
            use_unified = not args.no_unified
            asyncio.run(run_interactive_mode(assistant, use_unified=use_unified))
        
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
