# ⚡ Nested Learning System Overview

**Multi-Frequency Memory Updates** - Prevents catastrophic forgetting through tiered update frequencies.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSCIOUSNESS LOOP                        │
│                                                              │
│  User Message → Process → Response                          │
│       │                                                      │
│       ▼                                                      │
│  ┌────────────────────────────────────────────┐            │
│  │     NESTED LEARNING TRIGGER                 │            │
│  │  • Track message count                     │            │
│  │  • Check update frequencies                │            │
│  └────────────────────────────────────────────┘            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────┴───────────────┐
        │                                 │
        ▼                                 ▼
┌───────────────┐              ┌──────────────────┐
│  RECALL       │              │  CORE MEMORY     │
│  MEMORY       │              │                  │
│               │              │  • persona       │
│  • Every msg  │              │  • human         │
│  • High freq  │              │  • system_context│
│  • Stability: │              │                  │
│    0.1        │              │  • Every 10 msgs │
│               │              │  • Medium freq   │
│  Updates:     │              │  • Stability:    │
│  1, 2, 3...   │              │    0.5          │
└───────────────┘              │                  │
                               │  Updates:        │
                               │  10, 20, 30...   │
                               └──────────────────┘
                                        │
                                        ▼
                               ┌──────────────────┐
                               │  ARCHIVAL MEMORY │
                               │                  │
                               │  • Long-term     │
                               │  • Every 100 msgs│
                               │  • Low freq      │
                               │  • Stability:    │
                               │    0.9           │
                               │                  │
                               │  Updates:        │
                               │  100, 200, 300...│
                               └──────────────────┘
```

---

## 🔄 Update Frequency Flow

```
Message Count → Check Frequencies → Update Tiers

Message 1:   ✅ Recall (1 % 1 = 0)   ❌ Core (1 % 10 ≠ 0)   ❌ Archival (1 % 100 ≠ 0)
Message 2:   ✅ Recall (2 % 1 = 0)   ❌ Core               ❌ Archival
Message 3:   ✅ Recall               ❌ Core               ❌ Archival
...
Message 10:  ✅ Recall (10 % 1 = 0)  ✅ Core (10 % 10 = 0)  ❌ Archival (10 % 100 ≠ 0)
Message 11:  ✅ Recall               ❌ Core               ❌ Archival
...
Message 20:  ✅ Recall               ✅ Core (20 % 10 = 0)  ❌ Archival
...
Message 100: ✅ Recall               ✅ Core (100 % 10 = 0) ✅ Archival (100 % 100 = 0)
```

---

## 📋 What Gets Sent to LLM

### Every Message (Recall Memory)
```
System Prompt:
├─ Base system prompt
├─ Memory Blocks (persona, human, system_context)
└─ Recent conversation history (last N messages)
```

### Every 10 Messages (Core Memory Update)
```
System Prompt:
├─ Base system prompt
├─ Memory Blocks (UPDATED)
│  ├─ persona (may have new info)
│  ├─ human (may have new info)
│  └─ system_context (updated timestamp)
└─ Recent conversation history
```

### Every 100 Messages (Archival Memory Update)
```
System Prompt:
├─ Base system prompt
├─ Memory Blocks (UPDATED)
├─ Recent conversation history
└─ Archival Memory Context (semantic search results)
   └─ Retrieved from ChromaDB based on current query
```

---

## ⚙️ Trigger Conditions

### Recall Memory
- **Trigger:** Every message
- **Condition:** `message_count % 1 == 0` (always true)
- **What happens:**
  - Loads recent conversation history
  - Includes in context window
  - No memory updates (just retrieval)

### Core Memory
- **Trigger:** Every 10 messages
- **Condition:** `message_count % 10 == 0`
- **What happens:**
  - Analyzes conversation for important info
  - Updates persona/human blocks if needed
  - Maintains stability (stability=0.5)
  - Learning rate: ~0.005 (medium)

### Archival Memory
- **Trigger:** Every 100 messages
- **Condition:** `message_count % 100 == 0`
- **What happens:**
  - Extracts key information from conversation
  - Stores in ChromaDB with embeddings
  - High stability (stability=0.9)
  - Learning rate: ~0.0001 (low)

---

## 🎯 Stability & Learning Rates

| Memory Tier | Update Frequency | Stability | Learning Rate | Update Interval |
|-------------|------------------|-----------|---------------|-----------------|
| **Recall**  | HIGH             | 0.1       | ~0.09         | Every 1 message |
| **Core**    | MEDIUM           | 0.5       | ~0.005        | Every 10 messages |
| **Archival**| LOW              | 0.9       | ~0.0001       | Every 100 messages |

**Key Insight:** Higher stability = Lower learning rate = More stable memories

---

## 🔍 Integration Points

### In Consciousness Loop
```python
# After processing message:
nested.track_message()  # Increment counter

# Check if updates needed:
if nested.should_update_core():
    # Update core memory blocks
    memory_engine.update_core_memory(...)

if nested.should_update_archival():
    # Store important info in archival
    memory_engine.add_archival_memory(...)
```

### What Gets Included in Context
```
┌─────────────────────────────────────┐
│  SYSTEM PROMPT (always)             │
├─────────────────────────────────────┤
│  MEMORY BLOCKS (always)             │
│  • persona                          │
│  • human                            │
│  • system_context                   │
├─────────────────────────────────────┤
│  RECALL MEMORY (every message)      │
│  • Last N messages                  │
├─────────────────────────────────────┤
│  CORE MEMORY UPDATE (every 10)     │
│  • Updated blocks if changed        │
├─────────────────────────────────────┤
│  ARCHIVAL CONTEXT (every 100)       │
│  • Semantic search results          │
│  • Relevant past memories           │
└─────────────────────────────────────┘
```

---

## 📈 Example Timeline

```
Message 1:   [Recall] ──────────────────────────────┐
Message 2:   [Recall] ──────────────────────────────┤
Message 3:   [Recall] ──────────────────────────────┤
...                                                  │
Message 10:  [Recall] [Core Update] ────────────────┤
Message 11:  [Recall] ──────────────────────────────┤
...                                                  │
Message 20:  [Recall] [Core Update] ────────────────┤
...                                                  │
Message 100: [Recall] [Core Update] [Archival] ─────┘
```

**Legend:**
- `[Recall]` = Recall memory included (every message)
- `[Core Update]` = Core memory blocks updated (every 10)
- `[Archival]` = Archival memory updated + context retrieved (every 100)

---

## 🎯 Benefits

1. **Prevents Catastrophic Forgetting**
   - Important memories (archival) update slowly → stay stable
   - Recent memories (recall) update fast → stay flexible

2. **Efficient Resource Usage**
   - Only update when needed (not every message)
   - Reduces unnecessary API calls

3. **Natural Memory Hierarchy**
   - Mimics human memory (working → short-term → long-term)
   - Different stability levels per tier

4. **Continuous Learning**
   - System improves over time
   - No forgetting of important information

---

**Based on:** [Google Research: Nested Learning](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/) (Nov 2025)

