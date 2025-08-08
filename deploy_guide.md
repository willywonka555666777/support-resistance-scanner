# 🚀 Deploy ke Server Gratis

## 1. HEROKU (Recommended)

### Setup:
```bash
# Install Heroku CLI
# Download dari: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Files yang dibutuhkan:
- ✅ `Procfile` - sudah dibuat
- ✅ `requirements.txt` - sudah dibuat  
- ✅ `runtime.txt` - sudah dibuat

---

## 2. RAILWAY

### Setup:
1. Buka https://railway.app
2. Login dengan GitHub
3. "New Project" > "Deploy from GitHub repo"
4. Connect repository
5. Auto deploy!

---

## 3. RENDER

### Setup:
1. Buka https://render.com
2. "New" > "Web Service"
3. Connect GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app_sr:app`

---

## 4. PYTHONANYWHERE (Free Tier)

### Setup:
1. Buka https://www.pythonanywhere.com
2. Create free account
3. Upload files via "Files" tab
4. "Web" > "Add new web app"
5. Choose Flask
6. Point to `app_sr.py`

---

## 5. VERCEL (Serverless)

### Setup:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Tambahan file untuk Vercel:
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "./app_sr.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

---

## 6. GLITCH

### Setup:
1. Buka https://glitch.com
2. "New Project" > "Import from GitHub"
3. Paste repository URL
4. Auto deploy!

---

## 🎯 Rekomendasi:

### **Untuk Pemula:** 
- **Railway** - paling mudah, auto deploy
- **Heroku** - reliable, banyak tutorial

### **Untuk Advanced:**
- **Render** - fast, modern
- **Vercel** - serverless, global CDN

### **Gratis Terbatas:**
- **PythonAnywhere** - 1 web app gratis
- **Heroku** - 550 jam/bulan gratis

---

## 📝 Langkah Deploy (Railway):

1. **Push ke GitHub:**
```bash
git init
git add .
git commit -m "Support Resistance Scanner"
git branch -M main
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

2. **Deploy di Railway:**
- Login https://railway.app
- "New Project" > "Deploy from GitHub repo"
- Pilih repository
- ✅ Auto deploy!

3. **Akses aplikasi:**
- Railway akan berikan URL: `https://your-app.railway.app`

**Total waktu: 5 menit!** 🚀