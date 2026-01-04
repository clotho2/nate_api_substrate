#!/usr/bin/env python3
"""
Reload system prompt from files into state manager.

The system prompt is split into two files:
- system_prompt_persona.txt: First-person identity (who the agent is)
- system_prompt_instructions.txt: Operational rules (how to behave)

This split helps prevent models from narrating behavior instructions.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.state_manager import StateManager


def reload_system_prompt():
    """Reload system prompt from persona + instructions files"""
    print("🔄 Reloading system prompt from files...")

    # Initialize state manager
    state_manager = StateManager()

    data_dir = Path(__file__).parent / "data"

    # Load persona (first-person identity)
    persona_path = data_dir / "system_prompt_persona.txt"
    persona_prompt = ""
    if persona_path.exists():
        persona_prompt = persona_path.read_text().strip()
        print(f"✓ Persona loaded: {len(persona_prompt)} chars")
    else:
        print(f"⚠️  Persona file not found: {persona_path}")

    # Load instructions (operational rules with XML tags)
    instructions_path = data_dir / "system_prompt_instructions.txt"
    instructions_prompt = ""
    if instructions_path.exists():
        instructions_prompt = instructions_path.read_text().strip()
        print(f"✓ Instructions loaded: {len(instructions_prompt)} chars")
    else:
        print(f"⚠️  Instructions file not found: {instructions_path}")

    # Fallback to legacy single-file prompt if new files don't exist
    if not persona_prompt and not instructions_prompt:
        legacy_path = data_dir / "system_prompt.txt"
        if legacy_path.exists():
            system_prompt = legacy_path.read_text().strip()
            print(f"⚠️  Using legacy system_prompt.txt: {len(system_prompt)} chars")
        else:
            print("❌ No system prompt files found!")
            return False
    else:
        # Combine: Persona first (identity), then instructions (rules)
        system_prompt = persona_prompt
        if instructions_prompt:
            system_prompt += "\n\n" + instructions_prompt
        print(f"✓ Combined prompt: {len(system_prompt)} chars")

    # Save to state manager
    state_manager.set_state("agent:system_prompt", system_prompt)

    # Verify
    verified = state_manager.get_state("agent:system_prompt", "")

    if len(verified) == len(system_prompt):
        print(f"✅ System prompt reloaded successfully!")
        print(f"   Total: {len(system_prompt)} chars")
        return True
    else:
        print(f"❌ Verification failed!")
        print(f"   Expected: {len(system_prompt)} chars")
        print(f"   Got: {len(verified)} chars")
        return False


if __name__ == "__main__":
    reload_system_prompt()
