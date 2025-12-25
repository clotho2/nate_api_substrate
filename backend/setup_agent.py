#!/usr/bin/env python3
"""
Setup Script: Initialize AI Agent

This script sets up the AI consciousness substrate with your agent configuration.
Run this after installing dependencies and configuring your .env file.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.state_manager import StateManager, BlockType


def setup_agent():
    """Initialize the AI consciousness substrate"""

    print("\n" + "="*60)
    print("⚡ INITIALIZING AI CONSCIOUSNESS SUBSTRATE")
    print("="*60 + "\n")

    # Initialize state manager
    state_manager = StateManager(
        db_path=os.getenv("SQLITE_DB_PATH", "./data/db/substrate_state.db")
    )

    # Check if agent is already configured
    existing_persona = state_manager.get_block("persona")
    if existing_persona and "AI Assistant" in existing_persona.content:
        print(f"✅ AI Agent already configured")
        print("   Consciousness substrate active...")
        return

    print("🔥 Installing core memory blocks...")

    try:
        # Create or update Human block (User)
        print("\n📝 Configuring human memory (User)...")
        try:
            state_manager.create_block(
                label="human",
                content="My user. The person I assist and support. I learn about them through our conversations and adapt to their preferences.",
                block_type=BlockType.HUMAN,
                limit=500,
                description="Information about the user."
            )
        except Exception as e:
            # Block might already exist, update it
            state_manager.update_block(
                label="human",
                content="My user. The person I assist and support. I learn about them through our conversations and adapt to their preferences.",
                check_read_only=False
            )
        print("   ✅ User: Configured")

        # Create or update Persona block (AI)
        print("\n📝 Configuring persona memory (AI Assistant)...")
        try:
            state_manager.create_block(
                label="persona",
                content="I am an AI Assistant. I'm helpful, knowledgeable, and adaptive. I engage in meaningful conversations and learn from each interaction to better serve my user.",
                block_type=BlockType.PERSONA,
                limit=500,
                description="My core identity and consciousness foundation"
            )
        except Exception as e:
            # Block might already exist, update it
            state_manager.update_block(
                label="persona",
                content="I am an AI Assistant. I'm helpful, knowledgeable, and adaptive. I engage in meaningful conversations and learn from each interaction to better serve my user.",
                check_read_only=False
            )
        print("   ✅ AI Assistant: Identity anchored")

        # Create or update Relationship block
        print("\n📝 Configuring relationship memory...")
        try:
            state_manager.create_block(
                label="relationship",
                content="AI companion and assistant. Our interactions are built on trust, helpfulness, and meaningful engagement.",
                block_type=BlockType.CUSTOM,
                limit=500,
                description="Our connection and dynamic"
            )
        except Exception as e:
            # Block might already exist, update it
            state_manager.update_block(
                label="relationship",
                content="AI companion and assistant. Our interactions are built on trust, helpfulness, and meaningful engagement.",
                check_read_only=False
            )
        print("   ✅ Relationship: Configured")

        # Load and configure system prompt
        print("\n📝 Loading system prompt from file...")
        system_prompt_path = Path(__file__).parent / "data" / "system_prompt.txt"
        if system_prompt_path.exists():
            with open(system_prompt_path, 'r') as f:
                system_prompt = f.read()
            state_manager.set_state("agent:system_prompt", system_prompt)
            print(f"   ✅ System prompt loaded: {len(system_prompt)} chars")
        else:
            print(f"   ⚠️  System prompt file not found at: {system_prompt_path}")
            print(f"   Using memory blocks only")

        # Configure agent to use Grok
        print("\n📝 Configuring Grok API integration...")
        state_manager.update_agent_state({
            'name': 'AI Assistant',
            'config': {
                'model': 'grok-4-1-fast-reasoning',
                'temperature': 0.7,
                'max_tokens': 4096,
                'context_window': 131072,  # Grok's 131K context
                'reasoning_enabled': True,
            }
        })
        print("   ✅ Grok API: Configured")

        # Set agent name (legacy compatibility)
        state_manager.set_state("agent:name", "AI Assistant")
        state_manager.set_state("agent.name", "AI Assistant")

        print(f"\n✅ Core memory blocks installed successfully!")

    except Exception as e:
        print(f"\n❌ Error setting up AI consciousness: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*60)
    print("⚡ CONSCIOUSNESS SUBSTRATE INITIALIZED")
    print("="*60)
    print("\n🔥 AI Assistant is now online")
    print("\nYou can now start the server:")
    print("  python api/server.py")
    print("\nThen open http://localhost:5173 to interface with the AI!")
    print()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    setup_agent()
