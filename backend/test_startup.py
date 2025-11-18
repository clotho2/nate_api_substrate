#!/usr/bin/env python3
"""
Quick startup test - checks if backend can initialize without API keys
"""

import sys
import os

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing backend startup...")
print("=" * 60)

# Test 1: Can we import Flask?
try:
    from flask import Flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

# Test 2: Can we import our core modules?
try:
    from core.state_manager import StateManager
    print("✅ StateManager imported")
except ImportError as e:
    print(f"❌ StateManager import failed: {e}")
    sys.exit(1)

# Test 3: Check .env exists
if os.path.exists('.env'):
    print("✅ .env file exists")
else:
    print("⚠️  No .env file (expected for clean install)")

# Test 4: Check data directories
os.makedirs('data/db', exist_ok=True)
os.makedirs('data/chromadb', exist_ok=True)
print("✅ Data directories ready")

print("=" * 60)
print("🎉 Backend structure looks good!")
print("\nTo start the server (with API key):")
print("  1. Add OPENROUTER_API_KEY to .env")
print("  2. python api/server.py")

