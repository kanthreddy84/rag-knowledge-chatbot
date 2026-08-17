# 🚀 Complete Deployment Guide

## Overview
This guide covers deploying the DataFactZ RAG Chatbot to production using:
- **Frontend:** React → **Vercel** (Free)
- **Backend:** FastAPI → **Railway** or **Render** (Free)

---

## 📋 Prerequisites

1. GitHub account (for version control)
2. Vercel account (free at vercel.com)
3. Railway or Render account (for backend)
4. Git installed locally

---

## Part 1: Deploy Frontend to Vercel

### **Step 1: Prepare Your Repository**

```bash
# Navigate to project root
cd "C:\AI Projects\RAG Knowledge Chatbot"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - RAG Chatbot"

# Create .gitignore
echo "node_modules/" > .gitignore
echo "build/" >> .gitignore
echo ".env.local" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### **Step 2: Push to GitHub**

1. Go to [GitHub](https://github.com) and create new repository named `rag-knowledge-chatbot`
2. Add remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/rag-knowledge-chatbot.git
git branch -M main
git push -u origin main
```

### **Step 3: Deploy to Vercel**

1. **Go to** [vercel.com](https://vercel.com)
2. **Sign up** with GitHub account (free)
3. **Click** "New Project"
4. **Select** your `rag-knowledge-chatbot` repository
5. **Configure:**
   - Framework: `Create React App`
   - Root Directory: `web-app`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)
   - Install Command: `npm install` (auto-detected)

6. **Add Environment Variables:**
   - Click "Environment Variables"
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.com` (we'll get this after backend deployment)

7. **Deploy!** Click "Deploy"

**✅ Frontend URL:** `https://your-project.vercel.app`

---

## Part 2: Deploy Backend to Railway (Recommended)

Railway is perfect for FastAPI with free tier ($5/month free credit).

### **Step 1: Prepare Backend**

Create `requirements.txt` in project root:

```bash
# Make sure all dependencies are listed
pip freeze > requirements.txt
```

Key packages needed:
```
FastAPI==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
sentence-transformers==2.2.2
scikit-learn==1.3.2
numpy==1.24.3
```

Create `Procfile` in root directory:

```
web: python api_server.py
```

Create `runtime.txt`:

```
python-3.11.0
```

### **Step 2: Deploy to Railway**

1. **Go to** [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your `rag-knowledge-chatbot` repository
6. **Configure:**
   - Root directory: Leave empty (project root)
   - Environment: Add `PORT=8000`

7. **Railway will auto-detect** FastAPI and deploy!

**✅ Backend URL:** `https://your-backend-railway.up.railway.app`

---

## Part 3: Update Frontend Environment Variables

Once backend is deployed:

1. Go to **Vercel Dashboard**
2. Select your project
3. Go to **Settings → Environment Variables**
4. Update `REACT_APP_API_URL` with your Railway URL
5. **Redeploy:** Click "Deployments → Redeploy"

---

## Part 4: Alternative - Deploy Backend to Render

If you prefer Render over Railway:

1. **Go to** [render.com](https://render.com)
2. **Sign up** with GitHub
3. **Click** "New +"
4. **Select** "Web Service"
5. **Connect** your GitHub repo
6. **Configure:**
   - Name: `rag-chatbot-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port 8000`

7. **Deploy!**

**✅ Backend URL:** `https://rag-chatbot-api.onrender.com`

---

## 🔧 Configuration for Production

### **Update CORS in api_server.py**

For production, restrict CORS to your frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],  # Your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Environment Variables**

Create `.env` file in root:

```env
# Backend
FASTAPI_ENV=production
PORT=8000

# Frontend (Vercel)
REACT_APP_API_URL=https://your-backend-railway.up.railway.app
```

---

## 📊 Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] Vercel project linked and deployed
- [ ] Frontend accessible at Vercel URL
- [ ] Railway/Render project created
- [ ] Backend API responding (test `/health` endpoint)
- [ ] `REACT_APP_API_URL` environment variable set
- [ ] Frontend redeployed with backend URL
- [ ] Documents indexed on backend
- [ ] Clickable citations working on production
- [ ] Document viewer loading documents
- [ ] CORS configured for production

---

## 🧪 Testing Production Deployment

### **Test Frontend:**
```bash
# Go to your Vercel URL
https://your-project.vercel.app

# Test:
# 1. Ask a question
# 2. Click a citation
# 3. Verify document loads
```

### **Test Backend:**
```bash
# Test health endpoint
curl https://your-backend-url.com/health

# Test query endpoint
curl -X POST https://your-backend-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the dress code policy?"}'

# Test document retrieval
curl https://your-backend-url.com/api/documents/Code_of_Conduct/content
```

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| **Vercel** | FREE | Unlimited requests, 100 GB bandwidth |
| **Railway** | $5/month free credit | Easily covers FastAPI + vector DB |
| **Render** | FREE | Limited to 5 projects, 100 hours/month |
| **Pinecone** | $0-40/month | Optional, FAISS is free |
| **Total** | FREE-40/month | Completely free option available |

---

## 🆓 Completely Free Setup

- Vercel Frontend: FREE
- Railway Backend: FREE (with $5 monthly credit, never runs out for small projects)
- FAISS Vector DB: FREE (built-in, no additional cost)
- Total: **COMPLETELY FREE**

---

## 🚨 Important Notes

### **Document Indexing in Production**

Your documents are indexed automatically on backend startup. Make sure your documents are:
- In the `sample_data` folder
- Pushed to GitHub
- Will auto-index when Railway/Render starts

### **Vector Database**

- Using FAISS (local, in-memory)
- Documents re-indexed on every restart (fresh data)
- No persistent storage cost
- Scale: Works well for 15-30 HR policy documents

### **API Rate Limits**

- Vercel: Generous limits for free tier
- Railway: No rate limiting on free tier
- Render: Fair use policy (no hard limits)

---

## 📖 Monitoring & Logs

### **Vercel Logs**
- Go to Vercel Dashboard
- Select project
- Click "Logs"
- View real-time activity

### **Railway Logs**
- Go to Railway Dashboard
- Select project
- Click "Deployments"
- View build and runtime logs

### **Render Logs**
- Go to Render Dashboard
- Select service
- Click "Logs"
- View real-time output

---

## 🔄 Continuous Deployment

Both Vercel and Railway/Render support continuous deployment:

1. **Push code to GitHub**
2. **Automatic deployment triggered**
3. **Service automatically rebuilds and restarts**
4. **New changes live in seconds**

No manual deployment needed after initial setup!

---

## 📞 Troubleshooting

### **Frontend 404 on Documents**
- Check `REACT_APP_API_URL` is set correctly
- Verify backend is running
- Check CORS settings in backend

### **Backend Connection Issues**
- Verify Railway/Render service is running
- Check service logs for errors
- Test `/health` endpoint directly

### **Documents Not Loading**
- Ensure `sample_data` folder is in GitHub repo
- Check backend startup logs
- Verify documents are indexed

### **Slow Performance**
- Check Railway/Render resource usage
- Consider upgrading (paid tier)
- Monitor API response times

---

## 🎉 After Deployment

Congratulations! Your RAG Chatbot is live! 

**Share with:**
- Team members: `https://your-project.vercel.app`
- Clients: Professional, production-grade application
- Public: Scalable, free, and reliable

---

## 📚 Resources

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://railway.app/docs)
- [Render Docs](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Questions?** Refer to the documentation or check service status pages.

**Status Pages:**
- Vercel Status: https://www.vercelstatus.com
- Railway Status: https://status.railway.app
- Render Status: https://status.render.com
