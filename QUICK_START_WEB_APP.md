# Quick Start - DataFactZ Web App

Get the complete RAG chatbot system running in 5 minutes.

---

## Prerequisites Check

```bash
# Check Node.js (must be 16+)
node --version    # v16.0.0 or higher

# Check npm (must be 8+)
npm --version     # 8.0.0 or higher

# Check Python (must be 3.10+)
python --version  # Python 3.10.0 or higher
```

If any are missing, install from:
- Node.js & npm: https://nodejs.org (LTS recommended)
- Python: https://python.org (3.10+)

---

## Setup Steps (5 minutes)

### Step 1: Install Frontend (1 min)

```bash
cd web-app
npm install
```

Expected output:
```
added 200+ packages in 1.2s
```

### Step 2: Configure Backend

Ensure the main project has dependencies installed:

```bash
# From project root
pip install fastapi uvicorn scikit-learn -q
```

Your environment must have:
- `document_chunking.py`
- `sentence_transformers` model
- Sample documents in `sample_data/`

### Step 3: Start Backend Server (Terminal 1)

```bash
# From project root
python api_server.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
Starting DataFactZ RAG API Server...
Available at http://localhost:8000
Indexing sample documents...
✓ 6 documents indexed
✓ 42 total chunks
✓ Ready to accept queries
```

### Step 4: Start Frontend (Terminal 2)

```bash
cd web-app
npm start
```

Expected output:
```
Compiled successfully!
You can now view datafacz-rag-chatbot in the browser.
Local:            http://localhost:3000
```

Browser opens automatically to **http://localhost:3000**

### Step 5: Test the System

1. **Chat Page**
   - Type: "How much vacation time do I get?"
   - Should see response with citations

2. **Documents Page**
   - See all 6 indexed documents
   - Click "Reindex" button (takes ~2-3 seconds)

3. **Settings Page**
   - View system status (should all be green)
   - Adjust LLM type if desired

---

## Verify Everything Works

### Backend Health Check

```bash
# Test backend API
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2026-08-14T...","models_loaded":true}
```

### Frontend Health Check

```bash
# Open in browser
http://localhost:3000

# Should see:
# - DataFactZ logo top-left
# - Navigation sidebar on left
# - Welcome message from HR Assistant
# - Input field at bottom
```

### Query Test

In the chat interface:

1. Type: "What is the remote work policy?"
2. Should see answer in 2-3 seconds
3. Citations should appear below answer
4. Confidence badge should show "HIGH" or "MEDIUM"

---

## Common Issues & Fixes

### Issue: "Cannot find module 'react'"

**Fix:**
```bash
cd web-app
npm install
```

### Issue: "API is not responding"

**Fix:**
1. Verify backend is running: `http://localhost:8000/health`
2. Check `REACT_APP_API_URL` in `web-app/.env`
3. Restart backend server

### Issue: "No documents indexed"

**Fix:**
1. Verify `sample_data/` folder exists with .txt files
2. Click "Reindex" button in Documents page
3. Wait 3-5 seconds for indexing to complete

### Issue: "Port already in use"

**Fix - Port 3000 (Frontend):**
```bash
# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process

# Then restart: npm start
```

**Fix - Port 8000 (Backend):**
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Then restart: python api_server.py
```

### Issue: "Models loading takes forever"

**Expected behavior:**
- First run: 30-60 seconds (downloads ~130MB sentence-transformers model)
- Subsequent runs: 1-2 seconds (cached locally)

Be patient on first startup.

---

## Project Structure

```
RAG Knowledge Chatbot/
├── web-app/                    # React frontend (Port 3000)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Chat, Documents, Settings
│   │   ├── App.jsx             # Router setup
│   │   └── index.css           # Styles + Tailwind
│   ├── public/index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env
│
├── api_server.py               # FastAPI backend (Port 8000)
├── document_chunking.py        # Document processing
├── embedding_module_free.py    # Embedding provider
├── requirements.txt            # Python dependencies
├── sample_data/                # HR policy documents
│   ├── Leave_and_Time_Off_Policy.txt
│   ├── Remote_Work_Policy.txt
│   ├── Code_of_Conduct.txt
│   └── ... (3+ more documents)
│
├── WEB_APP_SETUP.md           # Detailed setup guide
├── WEB_APP_README.md          # Feature documentation
└── QUICK_START_WEB_APP.md     # This file
```

---

## Architecture Overview

```
┌──────────────────────────────────────────┐
│    Web Browser (http://localhost:3000)   │
│  ┌────────────────────────────────────┐  │
│  │  React App (Dark Mode, Responsive) │  │
│  │                                    │  │
│  │  Chat     │ Documents │ Settings   │  │
│  └────────────────────────────────────┘  │
│           ↓ HTTP/JSON                    │
├──────────────────────────────────────────┤
│  FastAPI Server (http://localhost:8000) │
│  • Query Processing                      │
│  • Document Management                   │
│  • Embedding Integration                 │
├──────────────────────────────────────────┤
│  RAG Backend (Python)                    │
│  • Document Chunker (400 tokens/chunk)   │
│  • Embeddings (sentence-transformers)    │
│  • Vector Search (cosine similarity)     │
│  • 6 policy documents, 42 chunks         │
└──────────────────────────────────────────┘
```

---

## What You Can Do Now

✅ **Ask policy questions** - Get answers grounded in official documents
✅ **See citations** - Every answer shows source documents with relevance scores
✅ **Manage documents** - Upload, reindex, delete policy documents
✅ **Configure settings** - Adjust LLM type and retrieval parameters
✅ **View system status** - Monitor backend health and readiness

---

## Next Steps

### To Add LLM Answer Generation

The web app currently shows retrieved documents. To add actual LLM answers:

1. **Install Ollama for FREE setup:**
   ```bash
   # Download from https://ollama.ai
   # Run: ollama serve
   # Models load automatically
   ```

2. **Or use Claude for HYBRID setup:**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   # Update Settings page to HYBRID
   ```

3. **LLM generation code** is in `llm_answer_generation.py` - integrate with backend

### To Deploy

1. **Vercel (Frontend)** - Push to GitHub, connect to Vercel
2. **Heroku/AWS (Backend)** - Deploy FastAPI server
3. **Docker** - Use provided Dockerfile setup

See `WEB_APP_SETUP.md` for deployment details.

### To Customize

- **Colors**: Edit `tailwind.config.js`
- **Pages**: Add to `src/pages/` + update `App.jsx`
- **Components**: Modify in `src/components/`
- **Styling**: Edit `src/index.css`

---

## Terminal Cheatsheet

```bash
# Start frontend
cd web-app && npm start

# Start backend
python api_server.py

# Install dependencies
npm install
pip install -r requirements.txt

# Check backend health
curl http://localhost:8000/health

# Rebuild Tailwind CSS
npm run build

# Clear npm cache
npm cache clean --force

# Kill process on port
lsof -ti:3000 | xargs kill -9     # macOS/Linux
# Windows: See "Common Issues" section
```

---

## Environment Variables

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

### Backend (api_server.py uses hardcoded defaults)
- PORT: 8000
- HOST: 0.0.0.0
- Sample data folder: `sample_data/`
- Auto-reindex on startup: Yes

---

## Documentation Files

| File | Purpose |
|------|---------|
| `WEB_APP_SETUP.md` | Detailed installation and configuration |
| `WEB_APP_README.md` | Features, components, API integration |
| `QUICK_START_WEB_APP.md` | This file - 5-minute setup |
| `README.md` | Main project documentation |
| `requirements.txt` | Python dependencies |

---

## Success Indicators

Your system is working correctly when:

1. ✅ `npm start` opens browser to http://localhost:3000
2. ✅ Chat page shows welcome message
3. ✅ Backend shows "Ready to accept queries"
4. ✅ Typing "How much vacation?" gets an answer with citations
5. ✅ Documents page shows 6 indexed documents
6. ✅ Settings page shows all green status badges

---

## Troubleshooting Flow

```
Problem?
│
├─ Can't start npm/backend?
│  └─ Check Node/Python versions + paths
│
├─ Backend not responding?
│  └─ Check port 8000 not in use, API health
│
├─ Query returns empty?
│  └─ Run "Reindex" in Documents page
│
├─ Styling looks broken?
│  └─ Delete node_modules, npm install, npm start
│
└─ Something else?
   └─ Check console for errors: F12 (Browser) or terminal
```

---

## Performance Notes

- **First load:** 30-60 seconds (downloads embedding model)
- **Subsequent loads:** 1-2 seconds (cached)
- **Query latency:** 0.5-2 seconds (depends on document count)
- **Chat response:** 2-4 seconds (with LLM generation)

---

## Support Resources

- **React Docs:** https://react.dev
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Lucide Icons:** https://lucide.dev
- **API Docs:** http://localhost:8000/docs (when backend running)
- **FastAPI:** https://fastapi.tiangolo.com

---

**Ready to start?**

```bash
# Terminal 1 - Backend
python api_server.py

# Terminal 2 - Frontend
cd web-app && npm start

# Browser opens automatically → http://localhost:3000
```

Questions? See WEB_APP_SETUP.md for detailed documentation.

**Enjoy your DataFactZ HR Policy Assistant!**

---

**Version:** 1.0.0
**Last Updated:** August 2026
**Status:** Production Ready
