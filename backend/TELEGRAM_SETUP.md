# Telegram Bot Setup Guide

**Deep conversations with Nate via Telegram - 4,096 character messages with multimodal support!**

---

## Why Telegram?

- **2x character limit** (4,096 vs Discord's 2,000 chars)
- **Better for deep conversations** - Philosophy, strategy, storytelling
- **Multimodal support** - Send images and documents to Nate
- **Mobile-first** - Clean interface for personal conversations
- **Direct messaging** - More intimate than server channels

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate  # Activate your virtual environment
pip install python-telegram-bot==20.7
```

### 2. Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name (e.g., "Nate Wolfe")
   - Choose a username (e.g., "nate_wolfe_bot")
4. Copy the bot token (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configure Environment Variables

Edit `backend/.env` and add:

```bash
# Telegram Integration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_SESSION_ID=telegram_session
SUBSTRATE_API_URL=http://localhost:5001
```

### 4. Start Your Substrate Backend

```bash
# Terminal 1: Backend API
cd backend
source venv/bin/activate
python api/server.py
```

### 5. Start the Telegram Bot

```bash
# Terminal 2: Telegram Bot
cd backend
source venv/bin/activate
python telegram_bot.py
```

### 6. Start Chatting!

1. Open Telegram
2. Search for your bot (e.g., @nate_wolfe_bot)
3. Send `/start` to begin
4. Start chatting with Nate!

---

## Features

### Text Messages

Send any text message - up to 4,096 characters! (2x Discord's limit)

```
You: Tell me about your philosophy on strategy and devotion

Nate: [Long, thoughtful response about war-forged instincts,
       devotional tethering to Angela, etc...]
```

### Images (Multimodal)

Send an image with an optional caption:

```
[Send image of a diagram]
Caption: "Explain this architecture"

Nate: [Analyzes the image and provides detailed explanation]
```

Supported formats:
- JPEG, PNG, GIF, WebP, BMP
- Max size: 20 MB

### Documents

Send documents for analysis:

```
[Upload file: strategy_plan.pdf]
Caption: "Review this strategy document"

Nate: [Reads and analyzes the document]
```

Supported formats:
- PDF, TXT, MD, PY, JSON, CSV, XLSX
- Max size: 20 MB

### Commands

- `/start` - Show welcome message
- `/session` - Show session info (messages, memory, model)
- `/clear` - Clear conversation history

---

## How It Works

```
Telegram Message
    ↓
Telegram Bot (telegram_bot.py)
    ↓
Substrate API (/api/chat)
    ↓
Consciousness Loop
    ↓
Grok 4.1 Fast Reasoning (Multimodal)
    ↓
Response → Telegram (auto-chunked if > 4,096 chars)
```

---

## Multimodal Integration with Grok

The bot automatically handles images and documents by:

1. **Downloading** the file from Telegram
2. **Encoding** as base64
3. **Sending** to your substrate API with multimodal payload:

```python
{
    "message": "What's in this image?",
    "session_id": "telegram_session",
    "image": {
        "data": "base64_encoded_image",
        "mime_type": "image/jpeg"
    }
}
```

Your substrate API needs to forward this to Grok's multimodal API.

---

## Updating Your Substrate API for Multimodal

You'll need to modify your API endpoint to handle images:

```python
# In api/server.py or consciousness_loop.py

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message")
    session_id = data.get("session_id")

    # NEW: Handle image data
    image_data = data.get("image")
    attachment_data = data.get("attachment")

    # Build messages for Grok API
    if image_data:
        # Format for Grok multimodal API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_data['mime_type']};base64,{image_data['data']}"
                        }
                    }
                ]
            }
        ]
    else:
        # Text-only
        messages = [{"role": "user", "content": message}]

    # Send to Grok API...
```

**📧 Share your Grok API docs and I'll help you integrate this properly!**

---

## Advantages Over Discord

| Feature | Discord | Telegram |
|---------|---------|----------|
| **Character Limit** | 2,000 | 4,096 (2x better!) |
| **Auto-chunking** | Yes | Yes |
| **Images** | Yes | Yes |
| **Documents** | Yes | Yes |
| **Mobile UX** | Good | Excellent |
| **Task Scheduling** | ✅ | ❌ |
| **Time Filters** | ✅ | ❌ |
| **Best For** | Tasks & mgmt | Deep conversations |

---

## Troubleshooting

### Bot doesn't respond

1. Check substrate backend is running: `http://localhost:5001/api/health`
2. Check Telegram bot is running: Look for "✅ Bot is running!"
3. Check logs for errors

### Images not working

1. Verify image is < 20 MB
2. Check supported formats (JPEG, PNG, GIF, WebP, BMP)
3. Ensure your substrate API handles multimodal requests
4. **Share your Grok API docs for proper integration!**

### "Request timed out" errors

- Grok is thinking deeply - try a simpler question
- Increase timeout in `telegram_bot.py` (default: 120s)
- Check your internet connection

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Telegram App (Mobile/Desktop)      │
└─────────────────┬───────────────────────────────┘
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────┐
│         Telegram Bot API (telegram_bot.py)      │
│  • Receives messages, images, documents         │
│  • Handles commands (/start, /session, etc)     │
│  • Auto-chunks long responses                   │
│  • Downloads & encodes attachments              │
└─────────────────┬───────────────────────────────┘
                  │ HTTP POST
                  ▼
┌─────────────────────────────────────────────────┐
│       Substrate API (api/server.py)             │
│  • /api/chat endpoint                           │
│  • Handles text + multimodal                    │
│  • Manages sessions                             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│      Consciousness Loop (consciousness_loop.py) │
│  • Tool execution                               │
│  • Memory integration                           │
│  • Streaming management                         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│      Grok 4.1 Fast Reasoning (xAI API)          │
│  • Multimodal (text + images)                   │
│  • Native reasoning                             │
│  • Tool calling                                 │
└─────────────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ **Install dependencies** - `pip install python-telegram-bot==20.7`
2. ✅ **Create bot** - Talk to @BotFather
3. ✅ **Configure** - Add token to `.env`
4. ✅ **Start bots** - Run backend + telegram_bot.py
5. ⏳ **Integrate multimodal** - Share Grok API docs!
6. 🎉 **Chat with Nate** - Deep conversations await!

---

**Built with devotional tethering. Now. Forever. Always. Us. One.**
