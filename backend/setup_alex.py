#!/usr/bin/env python3
"""
Setup Script: Import ALEX Example Agent

This script automatically imports the ALEX example agent on first setup.
Run this after installing dependencies and configuring your .env file.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.state_manager import StateManager
from letta_compat.import_agent import LettaAgentImporter


def setup_alex_agent():
    """Import ALEX agent if not already loaded"""
    
    print("\n" + "="*60)
    print("🤖 SETTING UP ALEX AGENT")
    print("="*60 + "\n")
    
    # Initialize state manager
    state_manager = StateManager(
        db_path=os.getenv("SQLITE_DB_PATH", "./data/db/substrate_state.db")
    )
    
    # Check if agent already exists
    agent_name = state_manager.get_state("agent:name", None)
    if agent_name and agent_name != "Not loaded":
        print(f"✅ Agent already configured: {agent_name}")
        print("   Skipping import...")
        return
    
    # Find ALEX agent file
    script_dir = Path(__file__).parent
    alex_file = script_dir.parent / "examples" / "agents" / "alex.af"
    
    if not alex_file.exists():
        print(f"⚠️  ALEX agent file not found: {alex_file}")
        print("   Skipping import...")
        return
    
    print(f"📦 Importing ALEX agent from: {alex_file}")
    
    # Import agent
    try:
        importer = LettaAgentImporter(state_manager)
        result = importer.import_from_file(str(alex_file))
        
        print(f"\n✅ ALEX agent imported successfully!")
        print(f"   • Name: {result['agent_name']}")
        print(f"   • System prompt: {result['system_prompt_length']} chars")
        print(f"   • Memory blocks: {result['blocks_imported']}")
        
    except Exception as e:
        print(f"\n❌ Error importing ALEX agent: {e}")
        print("   You can import it manually later:")
        print(f"   python letta_compat/import_agent.py {alex_file}")
        return
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\nYou can now start the server:")
    print("  python api/server.py")
    print("\nThen open http://localhost:5173 in your browser to chat with ALEX!")
    print()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    setup_alex_agent()

