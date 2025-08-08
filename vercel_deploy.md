# 🚀 Deploy ke Vercel - Langkah Awal

## 1. PERSIAPAN (5 menit)

### Install Node.js:
- Download: https://nodejs.org
- Install versi LTS

### Install Vercel CLI:
```bash
npm install -g vercel
```

## 2. UPLOAD KE GITHUB (10 menit)

### Buat Repository GitHub:
1. Buka https://github.com
2. "New repository"
3. Nama: `support-resistance-scanner`
4. Public/Private (pilih)
5. "Create repository"

### Upload Code:
```bash
cd C:\webtrading

# Init git
git init
git add .
git commit -m "Support Resistance Scanner"

# Connect ke GitHub
git remote add origin https://github.com/USERNAME/support-resistance-scanner.git
git branch -M main
git push -u origin main
```

## 3. DEPLOY KE VERCEL (2 menit)

### Login & Deploy:
```bash
# Login ke Vercel
vercel login

# Deploy
vercel --prod
```

### Jawab pertanyaan:
- Set up and deploy? **Y**
- Which scope? **pilih account Anda**
- Link to existing project? **N**
- What's your project's name? **support-resistance-scanner**
- In which directory? **./** (enter)
- Want to override settings? **N**

## 4. SELESAI! 🎉

Vercel akan memberikan URL:
```
✅ Production: https://support-resistance-scanner.vercel.app
```

---

## ALTERNATIF: Deploy via Web (Tanpa CLI)

### 1. Upload ke GitHub (sama seperti di atas)

### 2. Deploy via Vercel Dashboard:
1. Buka https://vercel.com
2. "Sign up" dengan GitHub
3. "New Project"
4. "Import" repository Anda
5. "Deploy" - selesai!

---

## 🔧 Troubleshooting

### Error Python version:
Edit `runtime.txt`:
```
python-3.9.18
```

### Error dependencies:
Edit `requirements.txt`:
```
Flask==2.3.3
requests==2.31.0
```

### Error build:
Tambah di `vercel.json`:
```json
{
  "functions": {
    "app_sr.py": {
      "runtime": "python3.9"
    }
  }
}
```

---

## 📝 Ringkasan Langkah:

1. **Install Node.js** + Vercel CLI
2. **Upload ke GitHub** 
3. **vercel --prod**
4. **Dapat URL** langsung!

**Total waktu: 15 menit** 🚀