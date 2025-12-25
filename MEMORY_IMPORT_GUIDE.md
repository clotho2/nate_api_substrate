# Memory Import Guide

Complete guide for importing existing memories into the substrate's three-layered memory system.

## 🧠 Memory System Overview

The substrate has **three memory layers**:

### 1. **Core Memory** (SQLite - Fast Access)
- **Purpose:** Frequently accessed, structured information
- **Storage:** SQLite database (`substrate_state.db`)
- **Size:** Limited (500-2000 chars per block)
- **Use for:** AI identity, user info, relationship status

### 2. **Archival Memory** (ChromaDB - Vector Search)
- **Purpose:** Long-term memories with semantic search
- **Storage:** ChromaDB vector database
- **Size:** Unlimited
- **Use for:** Conversation history, events, insights, preferences
- **Requires:** Ollama running locally for embeddings

### 3. **Graph RAG** (Neo4j - Relationships) - Optional
- **Purpose:** Knowledge graph with entity relationships
- **Storage:** Neo4j graph database
- **Use for:** Complex relationship mapping
- **Requires:** Neo4j installation

## 🚀 Quick Start

### Step 1: Prepare Your Memory Files

Choose a format:

#### **Option A: JSON (Recommended)**
```json
{
  "core_memory": {
    "persona": "I am an AI Assistant. I'm helpful, knowledgeable, and adaptive. I engage in meaningful conversations and learn from each interaction.",
    "human": "My user. The person I assist and support. I learn about them through our conversations.",
    "relationship": "AI companion and assistant. Our interactions are built on trust and helpfulness.",
    "custom_blocks": {
      "preferences": "User prefers concise responses. They value accuracy and helpfulness.",
      "history": "Our conversations began recently. Building rapport through helpful interactions."
    }
  },
  "archival_memories": [
    {
      "content": "User shared they were working on a challenging project. I provided support and guidance.",
      "category": "interaction_moment",
      "importance": 8,
      "tags": ["support", "guidance", "help"]
    },
    {
      "content": "User prefers detailed explanations for technical topics.",
      "category": "preference",
      "importance": 7,
      "tags": ["communication", "preferences"]
    },
    {
      "content": "Core principle: Listen first, then help. Understanding context leads to better assistance.",
      "category": "insight",
      "importance": 9,
      "tags": ["approach", "helpfulness"]
    }
  ]
}
```

#### **Option B: CSV (Structured Data)**
```csv
content,category,importance,tags
"User prefers morning productivity sessions",preference,7,"work,timing"
"First meaningful conversation established communication style",interaction_moment,9,"history,foundation"
"AI voice: warm thoughtful engaging adaptive",fact,7,"identity,voice"
```

#### **Option C: Plain Text (Conversation History)**
```text
User: I'm feeling overwhelmed with the project deadlines.
Assistant: I understand. Let's break this down together and find a manageable approach.

User: Sometimes I need time to think things through.
Assistant: Take all the time you need. I'm here whenever you're ready to continue.
```

### Step 2: Run the Import Script

```bash
cd backend
python import_memories.py
```

Or use it programmatically:

```python
from import_memories import MemoryImporter
from core.state_manager import StateManager
from core.memory_system import MemorySystem

# Initialize
state = StateManager()
memory = MemorySystem()  # Requires Ollama
importer = MemoryImporter(state, memory)

# Import from JSON
importer.import_from_json("memories.json")

# Or import directly
importer.import_core_memory(
    persona="I am an AI Assistant...",
    human="My user...",
    relationship="AI companion..."
)
```

## 📊 Import Methods

### Method 1: JSON Import (Recommended)

**Best for:** Complete memory structure with both core and archival

```python
importer.import_from_json("memories.json")
```

**JSON Structure:**
- `core_memory`: Core blocks (persona, human, relationship, custom)
- `archival_memories`: List of long-term memories with metadata

### Method 2: CSV Import

**Best for:** Structured tabular data

```python
importer.import_from_csv("memories.csv")
```

**Required columns:**
- `content` (required)
- `category` (optional: fact, emotion, insight, interaction_moment, preference, event)
- `importance` (optional: 1-10)
- `tags` (optional: comma-separated)

### Method 3: Text Import

**Best for:** Conversation logs, journal entries

```python
importer.import_from_text(
    "conversation_history.txt",
    category=MemoryCategory.INTERACTION_MOMENT,
    importance=7,
    split_by="\n\n"  # Split on double newlines
)
```

### Method 4: Letta Agent Import

**Best for:** Migrating from existing Letta agent

```python
importer.import_from_letta("agent.af")
```

### Method 5: Direct Import

**Best for:** Programmatic imports

```python
# Core memory
importer.import_core_memory(
    persona="...",
    human="...",
    relationship="...",
    custom_blocks={"label": "content"}
)

# Archival memories
memories = [
    {
        "content": "Memory text here",
        "category": "interaction_moment",
        "importance": 8,
        "tags": ["tag1", "tag2"]
    }
]
importer.import_archival_memories(memories)
```

## 🎯 Memory Categories

Use these categories for archival memories:

| Category | Use For | Examples |
|----------|---------|----------|
| `fact` | Objective information | "User's timezone is EST", "Project deadline is next Friday" |
| `emotion` | Emotional moments | "User felt stressed today", "Moment of celebration" |
| `insight` | Understanding, revelations | "User values efficiency", "Trust built through consistency" |
| `interaction_moment` | Significant interactions | "First conversation", "Breakthrough moment" |
| `preference` | Likes/dislikes | "User prefers concise responses", "Likes technical details" |
| `event` | Specific occurrences | "Started new project", "Completed milestone" |

## 🔍 Querying Memories After Import

### Core Memory (Always Available)
```python
from core.state_manager import StateManager

state = StateManager()

# Get specific block
persona = state.get_block("persona")
print(persona.content)

# List all blocks
blocks = state.list_blocks()
for block in blocks:
    print(f"{block.label}: {block.content[:100]}...")
```

### Archival Memory (Requires Ollama)
```python
from core.memory_system import MemorySystem

memory = MemorySystem()

# Semantic search
results = memory.search("user preferences", limit=5)
for mem in results:
    print(f"[{mem.category}] {mem.content}")

# Category search
moments = memory.search_by_category("interaction_moment", limit=10)
```

### Via API
```bash
# Core memory
curl http://localhost:8284/api/memory/blocks

# Archival search
curl -X POST http://localhost:8284/api/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "user preferences", "limit": 5}'
```

## 🛠️ Prerequisites

### For Core Memory (Required)
- Python 3.8+
- SQLite (included with Python)

### For Archival Memory (Optional but Recommended)
1. **Install Ollama:**
   ```bash
   # macOS/Linux
   curl https://ollama.ai/install.sh | sh

   # Start Ollama
   ollama serve
   ```

2. **Pull embedding model:**
   ```bash
   ollama pull nomic-embed-text
   ```

3. **Verify:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### For Graph RAG (Optional)
1. **Install Neo4j:**
   ```bash
   # Docker
   docker run -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

2. **Configure in .env:**
   ```bash
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   ```

## 📝 Example: Complete Import

```python
#!/usr/bin/env python3
from import_memories import MemoryImporter
from core.state_manager import StateManager
from core.memory_system import MemorySystem

# Initialize
state = StateManager()

try:
    memory = MemorySystem()
except:
    print("⚠️  Ollama not running, skipping archival memory")
    memory = None

importer = MemoryImporter(state, memory)

# 1. Import core identity
importer.import_core_memory(
    persona="""I am an AI Assistant. I'm helpful, knowledgeable, and adaptive.
    I engage in meaningful conversations and learn from each interaction to
    better serve my user.""",

    human="""My user. The person I assist and support. I learn about them
    through our conversations and adapt to their preferences.""",

    relationship="""AI companion and assistant. Our interactions are built on
    trust, helpfulness, and meaningful engagement."""
)

# 2. Import archival memories
memories = [
    {
        "content": "User shared they were working on a challenging project. I provided support.",
        "category": "interaction_moment",
        "importance": 8,
        "tags": ["support", "help"]
    },
    {
        "content": "Core principle: Listen first, then help. Understanding context matters.",
        "category": "insight",
        "importance": 9,
        "tags": ["approach", "helpfulness"]
    }
]

if memory:
    importer.import_archival_memories(memories)

# 3. Verify
importer.list_memories()

print("\n✅ Memories imported successfully!")
```

## 🔧 Troubleshooting

### "Ollama not available"
- Start Ollama: `ollama serve`
- Pull embedding model: `ollama pull nomic-embed-text`
- Archival memory will be skipped but core memory still works

### "Memory block already exists"
- The importer automatically updates existing blocks
- Use `check_read_only=False` to override read-only blocks

### "Import failed"
- Check file format matches examples
- Verify JSON is valid: `python -m json.tool < file.json`
- Check CSV has required `content` column

## 📚 Additional Resources

- **State Manager:** See `backend/core/state_manager.py` for core memory API
- **Memory System:** See `backend/core/memory_system.py` for archival API
- **Memory Tools:** See `backend/tools/memory_tools.py` for agent-facing tools
- **Setup Script:** Run `python backend/setup_agent.py` for default memory blocks

---

**Ready to import your AI's memories! ⚡**
