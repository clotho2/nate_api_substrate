# API Compatibility Guide

Substrate AI is designed to work with **any OpenAI-compatible API**, not just OpenRouter!

## Supported API Providers

The system uses the OpenAI Python client, which means it works with:

### ✅ Officially Supported

1. **OpenRouter** (recommended)
   - Access to 200+ models
   - Automatic fallback
   - Competitive pricing
   - Setup: Get key from https://openrouter.ai/

2. **OpenAI**
   - GPT-4, GPT-3.5, etc.
   - Setup: Get key from https://platform.openai.com/

3. **Azure OpenAI**
   - Enterprise-grade
   - Setup: Configure Azure endpoint

4. **Local Models via OpenAI-compatible servers:**
   - **LM Studio** (local inference)
   - **Ollama** with OpenAI compatibility layer
   - **vLLM** server
   - **Text Generation WebUI** (OpenAI extension)
   - **LocalAI**

### Configuration

Edit your `.env` file:

#### OpenRouter (Default)
```bash
OPENROUTER_API_KEY=sk-or-v1-...
# The code already uses OpenRouter's base URL
```

#### OpenAI
```bash
OPENROUTER_API_KEY=sk-...
```
Then in `core/openrouter_client.py`, change:
```python
base_url="https://openrouter.ai/api/v1"
```
to:
```python
base_url="https://api.openai.com/v1"
```

#### Azure OpenAI
```bash
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```
Then modify `core/openrouter_client.py` to use Azure configuration.

#### Local Models (LM Studio, etc.)
```bash
OPENROUTER_API_KEY=dummy_key  # Can be anything for local
```
Then in `core/openrouter_client.py`, change:
```python
base_url="http://localhost:1234/v1"  # LM Studio default
# OR
base_url="http://localhost:11434/v1"  # Ollama with openai-compatible
```

## Model Selection

When using different providers, update the model name in your requests:

### OpenRouter
```
openrouter/polaris-alpha
openrouter/anthropic/claude-3.5-sonnet
openrouter/openai/gpt-4
```

### OpenAI
```
gpt-4-turbo-preview
gpt-3.5-turbo
```

### Local Models
```
local-model-name  # Whatever you named it in LM Studio/Ollama
```

## Code Changes for Different Providers

All API client code is in `backend/core/openrouter_client.py`. To switch providers:

1. Update `base_url` in the `OpenAI` client initialization
2. Update default model name in `DEFAULT_MODEL` config
3. Update API key environment variable name if needed

Example for pure OpenAI:

```python
# In core/openrouter_client.py
self.client = OpenAI(
    api_key=self.api_key,
    base_url="https://api.openai.com/v1",  # Changed from OpenRouter
    timeout=120.0
)
```

## Testing Compatibility

```bash
# Test with curl
curl http://localhost:8284/api/health

# Test model list
curl http://localhost:8284/api/models

# Test chat (requires API key)
curl -X POST http://localhost:8284/api/agents/default/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Rate Limits & Costs

Different providers have different limits:

- **OpenRouter**: Depends on model, usually generous
- **OpenAI**: Tiered based on usage
- **Local**: No limits! (but slower)

Track your usage in the UI's cost counter (top right).

## Troubleshooting

### "Invalid API Key"
- Check your key is correct in `.env`
- Verify the `base_url` matches your provider
- For local models, ensure the server is running

### "Model not found"
- Check model name matches provider's format
- For OpenRouter: use `openrouter/provider/model`
- For OpenAI: use `gpt-4`, `gpt-3.5-turbo`, etc.
- For local: use exact model name from your server

### "Connection refused"
- For local: ensure inference server is running
- Check port number in `base_url`
- Try `curl http://localhost:PORT/v1/models` to test

---

**The beauty of OpenAI-compatible APIs**: One codebase, infinite model choices! 🚀

