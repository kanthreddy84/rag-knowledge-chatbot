# ⚡ Deployment Quick Start (30 minutes)

## 🎯 Your Mission
Get RAG Chatbot live on Vercel + Railway in 30 minutes - completely FREE!

---

## ✅ Checklist

### **5 Minutes: GitHub Setup**

- [ ] Go to [github.com](https://github.com) → Sign in
- [ ] Click **"+"** → **"New repository"**
- [ ] Name: `rag-knowledge-chatbot`
- [ ] Description: `AI HR Policy Assistant using RAG`
- [ ] Click **"Create repository"**
- [ ] Copy the commands shown and run in PowerShell:

```powershell
cd "C:\AI Projects\RAG Knowledge Chatbot"
git init
git add .
git commit -m "Initial commit - RAG Chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rag-knowledge-chatbot.git
git push -u origin main
```

---

### **5 Minutes: Vercel Frontend Deployment**

- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Click **"Sign Up"** → **"Continue with GitHub"**
- [ ] Authorize Vercel
- [ ] Click **"Add New"** → **"Project"**
- [ ] Select your `rag-knowledge-chatbot` repo
- [ ] **Framework:** Select `Create React App`
- [ ] **Root Directory:** Change to `web-app`
- [ ] Click **"Deploy"**
- [ ] ✅ Wait for deployment to complete
- [ ] Copy your URL: `https://your-name.vercel.app`

---

### **5 Minutes: Railway Backend Deployment**

- [ ] Go to [railway.app](https://railway.app)
- [ ] Click **"Start New Project"**
- [ ] Select **"Deploy from GitHub repo"**
- [ ] Choose your `rag-knowledge-chatbot` repo
- [ ] Click **"Deploy"**
- [ ] ✅ Wait for build to complete
- [ ] Copy your URL from the Dashboard: `https://your-railway-url.up.railway.app`

---

### **10 Minutes: Connect Frontend to Backend**

- [ ] Go back to **Vercel Dashboard**
- [ ] Click your project
- [ ] Go to **Settings** → **Environment Variables**
- [ ] Add new variable:
  - **Name:** `REACT_APP_API_URL`
  - **Value:** `https://your-railway-url.up.railway.app` (from Railway)
- [ ] Click **"Save"**
- [ ] Go to **Deployments**
- [ ] Click the latest deployment
- [ ] Click **"Redeploy"**
- [ ] ✅ Wait 1-2 minutes for redeployment

---

### **5 Minutes: Test Your Live App**

- [ ] Open [https://your-name.vercel.app](https://your-name.vercel.app)
- [ ] Ask: _"What is the dress code policy?"_
- [ ] ✅ Should see answer with citations
- [ ] Click a citation
- [ ] ✅ Document should load on right panel
- [ ] Try: _"What is the remote work policy?"_
- [ ] ✅ All working!

---

## 🎉 You're Done!

Your RAG Chatbot is now LIVE and FREE!

**Share your app:**
```
Frontend (React):  https://your-name.vercel.app
Backend (FastAPI): https://your-railway-url.up.railway.app
```

---

## 💰 Cost Breakdown

| Service | Monthly Cost |
|---------|--------------|
| Vercel  | FREE ✅      |
| Railway | FREE ✅ ($5 credit covers it) |
| **TOTAL** | **FREE** ✅ |

---

## 🔍 Verify Everything Works

### Test Frontend
```
1. Go to https://your-name.vercel.app
2. Ask: "What is the code of conduct?"
3. Click citation
4. See document load
```

### Test Backend Health
```
Visit: https://your-railway-url.up.railway.app/health

Should see:
{
  "status": "healthy",
  "timestamp": "...",
  "models_loaded": true
}
```

### Test Document Retrieval
```
Visit: https://your-railway-url.up.railway.app/api/documents

Should see list of indexed documents
```

---

## 🆘 Quick Fixes

### **Frontend says "Failed to get response"**
- Check `REACT_APP_API_URL` is set correctly in Vercel
- Make sure backend Railway is running (check Railway dashboard)
- Redeploy Vercel after setting environment variable

### **Document shows 404 error**
- Verify Railway backend is running
- Check backend has indexed documents (see Railway logs)
- Clear browser cache and refresh

### **Railway shows build error**
- Check that `requirements.txt` has all dependencies
- Verify `api_server.py` has no syntax errors
- Check Railway logs for specific error message

---

## 📊 What You Have Now

✅ **Production-Grade RAG Chatbot**
✅ **6 HR Policy Documents Indexed**
✅ **182 Document Chunks**
✅ **Clickable Citations with Document Viewer**
✅ **Dark/Light Mode Support**
✅ **Chat History Management**
✅ **Fully Responsive Design**
✅ **Enterprise-Ready Architecture**
✅ **Zero Monthly Cost**

---

## 🚀 Next Steps (Optional)

1. **Add more documents** → Update `sample_data` folder → Push to GitHub → Auto-redeploy
2. **Customize branding** → Update colors in `tailwind.config.js` → Push → Auto-redeploy
3. **Add more features** → Implement → Push → Instant deployment on Vercel
4. **Monitor performance** → Check Vercel/Railway dashboards

---

## 📞 Need Help?

**Common Issues:**
- Vercel: Check "Logs" tab for errors
- Railway: Check "Logs" tab for errors
- Frontend: Open browser DevTools (F12) → Console → Check for errors

**Resources:**
- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://railway.app/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)

---

## ✨ Congratulations!

Your RAG Chatbot is **LIVE** and **FREE**! 🎉

Share it with your team:
```
https://your-name.vercel.app
```

Enjoy your production-grade AI assistant! 🚀
