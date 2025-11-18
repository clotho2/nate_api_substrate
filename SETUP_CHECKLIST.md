# Setup Checklist

Use this checklist to verify your Substrate AI installation is ready to use.

## ✅ Pre-Flight Checks

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] OpenRouter API key obtained (https://openrouter.ai/keys)
- [ ] Git repository cloned or downloaded

## ✅ Backend Setup

- [ ] Virtual environment created (`python3 -m venv venv`)
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `config/.env.example`
- [ ] `OPENROUTER_API_KEY` set in `.env`
- [ ] ALEX agent imported (`python setup_alex.py`)
- [ ] Backend starts without errors (`python api/server.py`)

## ✅ Frontend Setup

- [ ] Dependencies installed (`npm install`)
- [ ] Frontend starts without errors (`npm run dev`)
- [ ] Frontend accessible at http://localhost:5173

## ✅ First Chat Test

- [ ] Backend running on http://localhost:8284
- [ ] Frontend running on http://localhost:5173
- [ ] Can open chat interface in browser
- [ ] Can send a message to ALEX
- [ ] Receive a response from ALEX
- [ ] Streaming works (text appears progressively)

## ✅ Verification

Run these commands to verify everything works:

```bash
# Backend health check
curl http://localhost:8284/api/health
# Should return: {"status":"ok"}

# Agent info
curl http://localhost:8284/api/agent/info
# Should show ALEX agent info

# Memory blocks
curl http://localhost:8284/api/memory/blocks
# Should return list of memory blocks
```

## 🐛 Troubleshooting

**Backend won't start:**
- Check if port 8284 is in use: `lsof -i :8284`
- Kill existing process: `lsof -ti:8284 | xargs kill -9`
- Check `.env` file exists and has `OPENROUTER_API_KEY`

**Frontend can't connect:**
- Verify backend is running: `curl http://localhost:8284/api/health`
- Check browser console for CORS errors
- Verify frontend is on port 5173

**ALEX agent not working:**
- Run setup script again: `python setup_alex.py`
- Check agent exists: `curl http://localhost:8284/api/agent/info`
- Verify ALEX file exists: `ls examples/agents/alex.af`

**"Invalid API Key" error:**
- Double-check `OPENROUTER_API_KEY` in `.env`
- No quotes around the key
- No extra spaces
- Key starts with `sk-or-v1-`

---

**Once all checks pass, you're ready to chat with ALEX! 🎉**

