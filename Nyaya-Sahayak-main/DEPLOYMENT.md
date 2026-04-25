
# Deployment Guide: Nyaya-Sahayak

We recommend deploying using **Streamlit Community Cloud** because it is free, easy, and connects directly to GitHub.

## Prerequisites

1.  A **GitHub Account**.
2.  A **Streamlit Community Cloud Account** (Sign up at share.streamlit.io).
3.  Your **Groq API Key**.

---

## Step 1: Prepare the Project for GitHub

1.  **Check `.gitignore`**:
    Ensure you have a `.gitignore` file that excludes sensitive data (like `.env` and `.venv`). We have created one for you that:
    *   Excludes `.env` (your API keys).
    *   Excludes `.venv` (your local environment).
    *   **Includes** `data/processed` and `data/vector_store` (so the app works instantly without rebuilding the index).

2.  **Verify `requirements.txt`**:
    Ensure all libraries are listed. Your current file looks correct for Streamlit Cloud.

---

## Step 2: Push to GitHub

Determine if you have Git installed. If not, install it or upload files manually.

### Option A: Using Git (Recommended)

Run these commands in your project terminal:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit for deployment"

# Create a new repository on GitHub.com:
# 1. Go to github.com/new
# 2. Name it "nyaya-sahayak"
# 3. Do NOT initialize with README/license (keep it empty)

# Link and push (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/nyaya-sahayak.git
git branch -M main
git push -u origin main
```

### Option B: Manual Upload
1.  Go to creating a new repo on GitHub.
2.  Click "uploading an existing file".
3.  Drag and drop your project folders.

---

## Step 3: Deploy on Streamlit Cloud

1.  Go to **[share.streamlit.io](https://share.streamlit.io/)**.
2.  Click **"New app"**.
3.  Select your GitHub repository (`nyaya-sahayak`).
4.  **Configuration**:
    *   **Main file path**: `ui/streamlit_app.py` (Important! Do not leave as default).
    *   **Python version**: 3.11 or 3.12 (Recommended).
5.  Click **"Deploy!"**.

---

## Step 4: Add Secrets (Important)

Your app will fail initially because the `.env` file (containing your API key) was not uploaded. You must add it securely.

1.  On your deployed app dashboard, click **"Settings"** -> **"Secrets"**.
2.  Copy the contents of your local `.env` file and paste them into the box in TOML format:

```toml
GROQ_API_KEY = "your-gsk-key-here"
GROQ_MODEL = "llama3-8b-8192"
```

3.  Click **"Save"**.
4.  Reboot the app if it doesn't automatically restart.

## Done! 🚀
Your app is now live with a public URL!
