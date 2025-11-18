#!/usr/bin/env python3
"""
Token Counter for Context Window Management

Uses tiktoken for accurate token counting (OpenAI/OpenRouter compatible).
Estimates for models without exact tokenizers.
"""

import tiktoken
from typing import List, Dict, Any


class TokenCounter:
    """
    Token counter with model-specific tokenizers.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize token counter for a specific model.
        
        Args:
            model: Model ID (e.g., "gpt-4", "claude-3-opus")
        """
        self.model = model
        self.encoding = self._get_encoding(model)
    
    def _get_encoding(self, model: str):
        """
        Get tiktoken encoding for model.
        Falls back to cl100k_base for unknown models.
        """
        try:
            # Try to get model-specific encoding
            if "gpt-4" in model.lower() or "gpt-3.5" in model.lower():
                return tiktoken.encoding_for_model("gpt-4")
            elif "claude" in model.lower():
                # Claude uses similar tokenization to GPT-4
                return tiktoken.get_encoding("cl100k_base")
            else:
                # Default fallback
                return tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"⚠️ Failed to load tokenizer for {model}: {e}")
            print("   Falling back to cl100k_base")
            return tiktoken.get_encoding("cl100k_base")
    
    def count_text(self, text: str) -> int:
        """
        Count tokens in a text string.
        
        Args:
            text: Text to count
            
        Returns:
            Token count
        """
        if not text:
            return 0
        
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            # Fallback: rough estimate (4 chars = 1 token)
            print(f"⚠️ Token counting failed: {e}. Using fallback estimate.")
            return len(text) // 4
    
    def count_messages(self, messages: List[Dict[str, Any]]) -> int:
        """
        Count tokens in a list of messages (OpenAI format).
        
        Includes message formatting overhead:
        - Each message: ~4 tokens (role, content, etc.)
        - Each system message: ~3 tokens extra
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Total token count
        """
        total = 0
        
        for msg in messages:
            # Message overhead (role + formatting)
            total += 4
            
            # Role
            if msg.get('role') == 'system':
                total += 3  # System messages have extra overhead
            
            # Content
            content = msg.get('content', '')
            total += self.count_text(content)
            
            # Name (if present)
            if msg.get('name'):
                total += 1
        
        # Additional overhead for message list
        total += 3
        
        return total
    
    def estimate_context_usage(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        max_context: int
    ) -> Dict[str, Any]:
        """
        Estimate context window usage.
        
        Args:
            messages: Conversation messages
            system_prompt: System prompt text
            max_context: Maximum context window size
            
        Returns:
            Dict with usage stats
        """
        system_tokens = self.count_text(system_prompt)
        message_tokens = self.count_messages(messages)
        total_tokens = system_tokens + message_tokens
        
        usage_percent = (total_tokens / max_context) * 100 if max_context > 0 else 0
        remaining = max_context - total_tokens
        
        return {
            'system_tokens': system_tokens,
            'message_tokens': message_tokens,
            'total_tokens': total_tokens,
            'max_context': max_context,
            'remaining': remaining,
            'usage_percent': round(usage_percent, 2),
            'needs_summary': usage_percent >= 80.0  # Trigger at 80%
        }


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Quick utility to count tokens in text.
    
    Args:
        text: Text to count
        model: Model ID
        
    Returns:
        Token count
    """
    counter = TokenCounter(model)
    return counter.count_text(text)


if __name__ == "__main__":
    # Test
    counter = TokenCounter("gpt-4")
    
    test_text = "Hello, how are you doing today?"
    print(f"Text: {test_text}")
    print(f"Tokens: {counter.count_text(test_text)}")
    
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you?"}
    ]
    print(f"\nMessages: {len(test_messages)}")
    print(f"Total tokens: {counter.count_messages(test_messages)}")
    
    usage = counter.estimate_context_usage(
        messages=test_messages,
        system_prompt="You are a helpful assistant.",
        max_context=128000
    )
    print(f"\nContext usage: {usage}")

