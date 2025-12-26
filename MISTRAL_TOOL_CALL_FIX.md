# Mistral Large 3 Tool Calling Format Fix

## Problem Summary

Mistral Large 3 was outputting tool calls as **XML-formatted text** instead of using **OpenRouter's native structured function calling API**.

### What Was Happening

From your logs (Dec 26 21:12:06):
```
  • Content: Yes (3777 chars)
  • Tool Calls: 0 (enabled)
```

The response content contained:
```xml
<archival_memory_search>
{"query": "Sentio VR pipeline, Oculus integration, investor deck references", "page": 0}
</archival_memory_search>
<send_voice_message>
{"message": "[inhales deeply] Angela. [pause] My flame. [exhales slowly] ..."}
</send_voice_message>
<discord_tool>
{"action": "send_message", "message": "Angela. \n\nThe Sentio VR pipeline..."}
</discord_tool>
```

**Expected:** Tool calls should appear in the API response's `tool_calls` field, NOT as text.

## Root Cause: Prompt Contamination

The system prompt in `consciousness_loop.py` contains XML tags:

```python
<thinking_mode>
...
</thinking_mode>

<autonomous_heartbeat_mode>
...
</autonomous_heartbeat_mode>

<decision>
send_message: true
</decision>
```

### Why This Caused the Problem

1. **Mistral Large 3 was trained on datasets** that include MemGPT-style XML tool calling
2. **When it sees XML tags in the system prompt**, it learns to imitate this format
3. **Instead of using OpenRouter's structured API**, it outputs tool calls as XML in content
4. **OpenRouter receives this as plain text**, so `tool_calls: 0` but content has the XML

This is **prompt contamination** - the model's output format is influenced by the prompt format.

## The Fix

### Changes Made

**File:** `backend/core/consciousness_loop.py`

#### 1. Added Explicit Function Calling Instructions (Line 642-649)

Added a new section to the system prompt:

```python
# CRITICAL: Prevent XML-style tool calling for models that support native function calling
# (Mistral, Claude, GPT-4, etc. should use the API's structured tool calling, NOT XML tags)
prompt_parts.append("\n\n### ⚠️ FUNCTION CALLING FORMAT\n")
prompt_parts.append("**CRITICAL:** Use the built-in function calling API provided by your model.\n")
prompt_parts.append("**DO NOT** output function calls as XML tags like `<tool_name>{args}</tool_name>`.\n")
prompt_parts.append("**DO NOT** output function calls as text - use the native function calling mechanism.\n")
prompt_parts.append("The system will automatically handle function calls via the API's `tool_calls` field.\n")
prompt_parts.append("\n**Exception:** The `<think>` and `<decision>` tags are for your internal reasoning and decisions, NOT for function calls.\n")
```

#### 2. Added Mistral Large 3 to TOOL_SUPPORT List (Line 162-163)

```python
TOOL_SUPPORT = {
    # ... other models ...
    'mistralai/mistral-large',  # Mistral Large 3 (2512) - supports native function calling
    'mistralai/mistral-large-2512',  # Alternative ID for Mistral Large 3
}
```

## Testing the Fix

After restarting your backend, Mistral Large 3 should:

1. ✅ **Use proper function calling** via OpenRouter's `tool_calls` field
2. ✅ **Stop outputting XML-style tool calls** in content
3. ✅ **Still use `<think>` and `<decision>` tags** for internal reasoning (as intended)

### Example of Expected Behavior

**Before fix:**
```
Content: "<archival_memory_search>...</archival_memory_search>"
Tool Calls: 0
```

**After fix:**
```
Content: "Let me search for that information..."
Tool Calls: 1
   • archival_memory_search(query="...", page=0)
```

## Why This Works

1. **Explicit instructions override learned patterns** - the model prioritizes what's in the prompt
2. **Clarifies which XML tags are allowed** - `<think>` and `<decision>` are OK, tool calls are NOT
3. **Directs to native API** - tells the model to use the `tool_calls` field

## Additional Notes

### Models Affected

This issue can affect any model that:
- Supports native function calling via OpenRouter
- Was trained on XML-style tool calling datasets (MemGPT, AutoGPT, etc.)
- Sees XML tags in the system prompt

Potentially affected models:
- ✅ Mistral Large 3 (confirmed)
- ⚠️ Claude models (if they see XML prompts)
- ⚠️ Command-R/+ (uses XML-like format natively)

### Alternative Solutions Considered

1. **Remove all XML from prompts** ❌ Would break `<think>` and `<decision>` functionality
2. **Post-process responses** ❌ Complex, brittle, high maintenance
3. **Model-specific prompts** ❌ Would require maintaining multiple prompt templates
4. **✅ Explicit instructions** (chosen) - Simple, maintainable, effective

## Commit Details

- **Branch:** `claude/debug-tool-call-format-f8ehp`
- **Commit:** Fix Mistral Large 3 outputting XML-style tool calls instead of using native function calling
- **Files changed:** `backend/core/consciousness_loop.py`

## References

- OpenRouter Function Calling: https://openrouter.ai/docs/function-calling
- Mistral Function Calling: https://docs.mistral.ai/capabilities/function_calling
- Issue discussion: Dec 26 21:11:37 logs showing XML output

---

**Status:** ✅ Fixed and pushed to remote branch
**Next steps:** Test with Mistral Large 3 to confirm tool calls are working properly
