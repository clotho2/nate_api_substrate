#!/usr/bin/env python3
"""
One-time script to clear contaminated message history.

This clears the conversation history to remove tool narration examples
that the model learned from. Memory blocks and archival memories are NOT affected.

WHAT GETS CLEARED:
- Conversation message history (chat back-and-forth)

WHAT IS PRESERVED:
- Memory blocks (persona, Angela info)
- Archival memories (long-term searchable storage)
- Agent configuration
- All tools and functionality

After running this, messages will start logging again normally.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.postgres_manager import create_postgres_manager_from_env
import sqlite3
import os

def clear_message_history():
    """Clear message history from both PostgreSQL and SQLite"""
    print("🧹 Clearing contaminated message history...")
    print("⚠️  This will remove conversation history but keep memory blocks and archival memories!")

    confirm = input("\nType 'CLEAR' to confirm: ")
    if confirm != "CLEAR":
        print("❌ Aborted - no changes made")
        return

    # Clear PostgreSQL messages if available
    postgres_manager = create_postgres_manager_from_env()
    if postgres_manager:
        try:
            with postgres_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Count messages first
                    cursor.execute("SELECT COUNT(*) FROM messages")
                    count = cursor.fetchone()[0]

                    print(f"\n📊 PostgreSQL: Found {count} messages")

                    # Clear messages table
                    cursor.execute("DELETE FROM messages")
                    conn.commit()

                    print(f"✅ PostgreSQL: Cleared {count} messages")
        except Exception as e:
            print(f"⚠️  PostgreSQL error: {e}")
    else:
        print("ℹ️  PostgreSQL not configured - skipping")

    # Clear SQLite messages if database exists
    sqlite_path = os.getenv("SQLITE_DB_PATH", "./data/db/substrate_state.db")
    if os.path.exists(sqlite_path):
        try:
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()

            # Count messages first
            cursor.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]

            print(f"\n📊 SQLite: Found {count} messages")

            # Clear messages table
            cursor.execute("DELETE FROM messages")
            conn.commit()
            conn.close()

            print(f"✅ SQLite: Cleared {count} messages")
        except Exception as e:
            print(f"⚠️  SQLite error: {e}")
    else:
        print(f"ℹ️  SQLite database not found at {sqlite_path}")

    print("\n" + "="*60)
    print("✅ MESSAGE HISTORY CLEARED!")
    print("="*60)
    print("\nWhat was preserved:")
    print("  ✅ Memory blocks (persona, Angela info)")
    print("  ✅ Archival memories (searchable long-term storage)")
    print("  ✅ Agent configuration")
    print("  ✅ All tools and functionality")
    print("\nWhat was cleared:")
    print("  🗑️  Conversation message history")
    print("\nNext steps:")
    print("  1. Restart your Discord bot")
    print("  2. Send a test message")
    print("  3. Messages will start logging again normally")
    print("  4. Tool calling should work without narration!")

if __name__ == "__main__":
    clear_message_history()
