# 🚀 Hugging Face Spaces Deployment Guide

## Step 1: Create Hugging Face Account
1. Go to [huggingface.co](https://huggingface.co)
2. Sign up / Log in

## Step 2: Create a New Space
1. Click your profile → **New Space**
2. Fill in:
   - **Space name:** `nexusai` (or your choice)
   - **License:** MIT
   - **SDK:** **Streamlit**
   - **Visibility:** Public or Private

## Step 3: Clone Your Space
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/nexusai
```

## Step 4: Copy Your Files
Copy ALL files from `nexus AI` folder to the cloned space folder.

## Step 5: Add Secrets (API Keys)
In Hugging Face:
1. Go to your Space → **Settings** → **Repository secrets**
2. Add:
   - `GROQ_API_KEY` = your Groq key
   - `GEMINI_API_KEY` = your Gemini key
   - `TAVILY_API_KEY` = your Tavily key (optional)

## Step 6: Push to Hugging Face
```bash
cd nexusai
git add .
git commit -m "Initial deployment"
git push
```

## Step 7: Wait for Build
Your space will build automatically. Check the **Logs** tab for progress.

---

## 🔧 Troubleshooting

### "Module not found" error
Add the missing package to `requirements.txt`

### App won't start
Check the Logs tab in your Space settings

### API keys not working
Make sure secrets are added correctly (no quotes, no spaces)

---

## 📝 Files Required
- `app.py` - Main application
- `requirements.txt` - Dependencies
- `README.md` - With YAML frontmatter
- All folders (`services/`, `ui/`, `config/`, `utils/`)

DO NOT include `.env` file - use Hugging Face Secrets instead!
