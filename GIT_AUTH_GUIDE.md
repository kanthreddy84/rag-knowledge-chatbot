# 🔐 GitHub Authentication Guide

You need to authenticate to push code to your repository. Choose one method:

---

## **OPTION 1: SSH (Recommended - Most Secure)**

### **Step 1: Check if SSH key exists**
```powershell
Test-Path $env:USERPROFILE\.ssh\id_rsa
```
- If returns `True`: Skip to Step 3
- If returns `False`: Continue to Step 2

### **Step 2: Generate SSH key (if needed)**
```powershell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N ""
```

### **Step 3: Get your SSH public key**
```powershell
Get-Content $env:USERPROFILE\.ssh\id_rsa.pub
```
Copy the output (the entire key starting with `ssh-rsa`)

### **Step 4: Add SSH key to GitHub**
1. Go to: https://github.com/settings/keys
2. Click **"New SSH key"**
3. Title: `My Computer`
4. Key: Paste what you copied in Step 3
5. Click **"Add SSH key"**

### **Step 5: Test SSH connection**
```powershell
ssh -T git@github.com
```
You should see: `Hi kanthreddy84! You've successfully authenticated...`

### **Step 6: Update remote URL to SSH**
```powershell
cd "C:\AI Projects\RAG Knowledge Chatbot"
git remote set-url origin git@github.com:kanthreddy84/rag-knowledge-chatbot.git
```

### **Step 7: Push code**
```powershell
git push -u origin main
```

✅ Done! Code is pushed!

---

## **OPTION 2: Personal Access Token (Easier for Quick Setup)**

### **Step 1: Create Personal Access Token on GitHub**

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Token name:** `vercel-deployment`
4. **Select scopes:** Check only `repo` (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)

### **Step 2: Use token to push**

```powershell
cd "C:\AI Projects\RAG Knowledge Chatbot"

# When prompted for password, paste your token (not your GitHub password)
git push -u origin main
```

When prompted:
- **Username:** `kanthreddy84`
- **Password:** Paste your token (right-click to paste in PowerShell)

✅ Code is pushed!

### **Step 3: Save credentials (optional)**

To avoid entering token every time:
```powershell
git config --global credential.helper wincred
```
Then do the push above once, and Windows will remember it.

---

## **⚡ QUICK COMPARISON**

| Feature | SSH | Token |
|---------|-----|-------|
| Security | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Setup Time | 5 min | 2 min |
| Ease | Medium | Easy |
| Remember Password | No | Yes (optional) |
| Recommended | ✅ YES | OK |

---

## **🚀 MY RECOMMENDATION**

For your first deployment, use **OPTION 2 (Token)** - it's faster.

Later, switch to **SSH** for better security.

---

## **YOUR IMMEDIATE ACTION**

Choose one:

### **Quick (2 min) - Use Token:**
1. Create token at https://github.com/settings/tokens/new
2. Copy token
3. Run:
```powershell
cd "C:\AI Projects\RAG Knowledge Chatbot"
git push -u origin main
```
4. Paste token when prompted

### **Better (5 min) - Use SSH:**
1. Follow OPTION 1 steps above
2. Adds SSH key to GitHub
3. Never need password again

---

## **WHICH ONE SHOULD I CHOOSE?**

- **New to GitHub?** → Use **Token** (easier)
- **Setup once, use forever?** → Use **SSH** (better)
- **Just want to deploy now?** → Use **Token** (quickest)

Pick one and let me know which you chose! I'll help you push the code.
