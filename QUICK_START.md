# Quick Start Guide

Get Substrate AI running in 5 minutes!

## Step 1: Get OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in Step 3)

## Step 2: Install Dependencies

### Backend (Python)

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### Frontend (Node.js)

```bash
cd frontend

# Install packages
npm install
```

## Step 3: Configure API Key

```bash
cd backend

# Copy example config
cp config/.env.example .env

# Edit .env and add your key
# Change this line:
OPENROUTER_API_KEY=your_openrouter_key_here
# To:
OPENROUTER_API_KEY=sk-or-v1-...your-actual-key...
```

## Step 3.5: Setup ALEX Agent (Optional but Recommended)

The repository includes a pre-configured example agent called **ALEX** (Adaptive Learning & Execution Companion). To use it:

```bash
cd backend
source venv/bin/activate  # If not already activated

# Import ALEX agent
python setup_alex.py
```

This will automatically configure ALEX as your default agent. If you skip this step, you'll start with a blank agent that you can customize later.

## Step 4: Start Backend

```bash
cd backend
source venv/bin/activate  # If not already activated
python api/server.py
```

You should see:
```
✅ Substrate AI Backend starting...
✅ Server running on http://localhost:8284
```

## Step 5: Start Frontend

Open a **new terminal** (keep backend running):

```bash
cd frontend
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

## Step 6: Chat!

1. Open your browser to `http://localhost:5173`
2. You'll see the chat interface
3. If you imported ALEX, you'll be chatting with ALEX - a multi-faceted AI colleague
4. Type a message and press Enter
5. Watch the AI respond with streaming text!

**Note:** If you didn't import ALEX, you'll start with a blank agent. You can customize it in the Memory Blocks panel (right sidebar).

## What's Next?

### Customize the Agent

Edit the agent's personality in the **Memory Blocks** panel (right sidebar):

- **Persona**: Who the AI is
- **Human**: What it knows about you

### Try Tools

Ask the AI to:
- "Remember that I love Python programming" (uses core_memory_append)
- "Search for information about neural networks" (uses archival_memory_search)

### Configure Settings

Click the **gear icon** (left sidebar) to adjust:
- Model selection (try different LLMs!)
- Temperature, max tokens, etc.
- Streaming behavior

## Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Need 3.11+

# Check if port is in use
lsof -i :8284

# If in use, kill it:
kill -9 $(lsof -t -i:8284)
```

**Frontend can't connect:**
```bash
# Make sure backend is running
curl http://localhost:8284/api/health

# Should return: {"status": "healthy"}
```

**"Invalid API Key" error:**
- Double-check your OpenRouter key in `backend/.env`
- Make sure there are no quotes around the key
- Make sure there are no extra spaces

## Stop Everything

```bash
# Stop frontend: Ctrl+C in frontend terminal
# Stop backend: Ctrl+C in backend terminal
```

## Need Help?

- 📖 Full docs: See `README.md`
- 🐛 Issues: Check GitHub Issues
- 💬 Questions: GitHub Discussions

---

**Enjoy your new AI agent! 🎉**

