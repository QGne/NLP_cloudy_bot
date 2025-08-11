#!/usr/bin/env python3
"""
CLI interface for ChatBot SaaS prototype
"""

import requests
import json
import sys
import uuid
from config import API_GATEWAY_URL, TIMEOUT

class ChatBotCLI:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.api_url = f"{API_GATEWAY_URL}/chat"
        
    def send_message(self, message):
        """Send message to chatbot API"""
        try:
            payload = {
                'message': message,
                'session_id': self.session_id
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'No response received')
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Connection error. Please check your internet connection."
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def run(self):
        """Main CLI loop"""
        print("🤖 ChatBot SaaS Prototype")
        print("=" * 40)
        print("Type 'exit' to quit, 'help' for commands")
        print(f"Session ID: {self.session_id[:8]}...")
        print()
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if user_input.lower() == 'exit':
                    print("Goodbye! 👋")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                elif user_input.lower() == 'new':
                    self.new_session()
                elif not user_input:
                    print("Please enter a message.")
                else:
                    print("🤔 Thinking...")
                    response = self.send_message(user_input)
                    print(f"🤖 Bot: {response}")
                    print()
                    
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def show_help(self):
        """Show help information"""
        print("\nAvailable commands:")
        print("  help  - Show this help message")
        print("  clear - Clear the screen")
        print("  new   - Start a new session")
        print("  exit  - Exit the application")
        print()
    
    def clear_screen(self):
        """Clear the screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def new_session(self):
        """Start a new session"""
        self.session_id = str(uuid.uuid4())
        print(f"Started new session: {self.session_id[:8]}...")
        print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test-mode':
        # Test mode for CI/CD
        cli = ChatBotCLI()
        test_response = cli.send_message("Hello, this is a test message")
        if "Error" not in test_response:
            print("✅ CLI test passed")
            sys.exit(0)
        else:
            print(f"❌ CLI test failed: {test_response}")
            sys.exit(1)
    else:
        # Interactive mode
        cli = ChatBotCLI()
        cli.run()

if __name__ == "__main__":
    main()