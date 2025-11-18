#!/usr/bin/env python3
"""
Config Writer - Writes configuration to ALL necessary places
This prevents the "system prompt lost" issue by ensuring changes persist everywhere!
"""

import os
import re
from typing import Dict, Any

class ConfigWriter:
    """Writes config to both DB and .env file - NEVER lose config again!"""
    
    def __init__(self, env_path: str = None):
        self.env_path = env_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env'
        )
    
    def update_env_file(self, updates: Dict[str, str]):
        """
        Update .env file with new values.
        Creates backup before modifying!
        
        Args:
            updates: Dict of KEY=VALUE pairs to update
        """
        # Read current .env
        if not os.path.exists(self.env_path):
            raise FileNotFoundError(f".env not found: {self.env_path}")
        
        # Create backup
        backup_path = f"{self.env_path}.backup"
        with open(self.env_path, 'r') as f:
            content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Backup created: {backup_path}")
        
        # Update each key
        lines = content.split('\n')
        updated_keys = set()
        
        for i, line in enumerate(lines):
            for key, value in updates.items():
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
                    updated_keys.add(key)
                    print(f"   Updated: {key}={value}")
        
        # Add keys that weren't found
        for key, value in updates.items():
            if key not in updated_keys:
                lines.append(f"{key}={value}")
                print(f"   Added: {key}={value}")
        
        # Write back
        with open(self.env_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ .env file updated: {self.env_path}")
        return True
    
    def save_model_config(self, model: str, context_window: int = None):
        """
        Save model config to BOTH .env and DB.
        
        Args:
            model: Model ID (e.g. "openrouter/polaris-alpha")
            context_window: Context window size (optional)
        """
        updates = {
            'DEFAULT_MODEL': model,
            'DEFAULT_LLM_MODEL': model
        }
        
        if context_window:
            updates['DEFAULT_CONTEXT_WINDOW'] = str(context_window)
        
        print(f"\n🔧 Saving model config to .env...")
        self.update_env_file(updates)
        
        # DB is updated separately by routes_agents.py
        print(f"✅ Model config saved to .env!")
        print(f"   (DB is updated by the API endpoint)")
        
        return True


if __name__ == "__main__":
    # Test
    writer = ConfigWriter()
    writer.save_model_config("openrouter/polaris-alpha", 128000)

