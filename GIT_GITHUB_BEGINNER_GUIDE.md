# Git & GitHub - Complete Beginner's Guide

## What is Git and GitHub?

**Git** = Version control software (tracks changes to your code)
**GitHub** = Website where you store your code online

**Benefits:**
- ✅ Upload all files at once with one command
- ✅ Easy to update code on PythonAnywhere later
- ✅ Backup of your code in the cloud
- ✅ Track all changes you make
- ✅ Undo mistakes easily

**Think of it like:**
- **Git** = Save button with unlimited undo
- **GitHub** = Google Drive for code

---

## Part 1: Install Git (5 minutes)

### Step 1: Download Git for Windows

1. Go to: https://git-scm.com/download/win
2. Download will start automatically
3. Run the installer (`Git-2.XX.X-64-bit.exe`)

### Step 2: Install Git (use these settings)

Click through the installer with these choices:
- ✅ **Editor:** Use Notepad (or keep default)
- ✅ **PATH environment:** Git from the command line and also from 3rd-party software (DEFAULT)
- ✅ **SSH:** Use bundled OpenSSH (DEFAULT)
- ✅ **HTTPS:** Use OpenSSL library (DEFAULT)
- ✅ **Line endings:** Checkout Windows-style, commit Unix-style (DEFAULT)
- ✅ **Terminal:** Use MinTTY (DEFAULT)
- ✅ Everything else: Keep defaults

Click **Install** → **Finish**

### Step 3: Verify Installation

Open **Command Prompt** (or PowerShell) and type:
```bash
git --version
```

You should see something like: `git version 2.42.0`

✅ **Git is installed!**

---

## Part 2: Create GitHub Account (3 minutes)

### Step 1: Sign Up

1. Go to: https://github.com/signup
2. Enter your email
3. Create a password
4. Choose a username (e.g., `yourname-cbc` or similar)
5. Verify you're human (puzzle)
6. Click **Create account**
7. Check your email and verify

### Step 2: Create New Repository

1. Once logged in, click the **+** in top right
2. Click **New repository**
3. Fill in:
   - **Repository name:** `csd-integration`
   - **Description:** "JotForm to CSD Portal integration"
   - **Visibility:**
     - ✅ **Private** (recommended - only you can see it)
     - or Public (anyone can see it)
   - ❌ **Do NOT check** "Initialize with README"
4. Click **Create repository**

You'll see a page with instructions. **Keep this page open** - we'll use it in the next step.

---

## Part 3: Upload Your Code to GitHub (5 minutes)

### Step 1: Open Terminal in Your Project

**In Windows:**

**Option A - Using WSL (what you've been using):**
```bash
cd /mnt/c/code/JOTFORM\ WEBHOOK/csd_integration
```

**Option B - Using Windows Command Prompt:**
- Open **Command Prompt** or **PowerShell**
- Navigate to your folder:
```cmd
cd "C:\code\JOTFORM WEBHOOK\csd_integration"
```

I'll show you the WSL commands since that's what we've been using.

### Step 2: Configure Git (First Time Only)

Tell Git who you are:
```bash
cd /mnt/c/code/JOTFORM\ WEBHOOK/csd_integration

git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with YOUR name and email (use the same email as GitHub).

### Step 3: Initialize Git Repository

```bash
git init
```

You'll see: `Initialized empty Git repository...`

### Step 4: Add All Files

```bash
git add .
```

The `.` means "add all files in this folder"

### Step 5: Create First Commit

```bash
git commit -m "Initial commit - CSD Portal integration"
```

A "commit" is like saving a snapshot of your code.

### Step 6: Connect to GitHub

Go back to your GitHub repository page (from Part 2, Step 2). Copy the commands under **"…or push an existing repository from the command line"**

They'll look like this (but with YOUR username):
```bash
git remote add origin https://github.com/yourusername/csd-integration.git
git branch -M main
git push -u origin main
```

**When prompted for credentials:**
- **Username:** Your GitHub username
- **Password:** You need a **Personal Access Token** (not your password!)

### Step 7: Create Personal Access Token (Required)

GitHub doesn't allow passwords anymore. You need a token:

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Give it a name: "PythonAnywhere Deploy"
4. Check: ✅ **repo** (full control of private repositories)
5. Scroll down, click **Generate token**
6. **COPY THE TOKEN** (you'll only see it once!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxx`
   - Save it in a text file temporarily

### Step 8: Push to GitHub

Now run the push command again:
```bash
git push -u origin main
```

When prompted:
- **Username:** Your GitHub username
- **Password:** Paste the **Personal Access Token** (not your password!)

✅ **Code is now on GitHub!**

Refresh your GitHub repository page - you should see all your files!

---

## Part 4: Download to PythonAnywhere (2 minutes)

### Step 1: Open PythonAnywhere Bash Console

1. Log into PythonAnywhere
2. Click **Consoles** tab
3. Click **Bash** to open a new console

### Step 2: Clone Repository

In the PythonAnywhere bash console:

```bash
cd ~
git clone https://github.com/yourusername/csd-integration.git
```

**If it's a private repository**, you'll need credentials:
- **Username:** Your GitHub username
- **Password:** Same **Personal Access Token** from earlier

**Or use this URL format to avoid prompts:**
```bash
git clone https://YOUR_TOKEN@github.com/yourusername/csd-integration.git
```
(Replace `YOUR_TOKEN` with the actual token)

✅ **All files are now on PythonAnywhere!**

Verify:
```bash
cd csd-integration
ls
```

You should see all your files!

---

## Part 5: Complete Deployment

Now follow the PythonAnywhere deployment steps:

```bash
# Install dependencies
cd ~/csd-integration
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then continue with Web app setup (see PYTHONANYWHERE_DEPLOYMENT.md)

---

## Common Git Commands (For Later)

### After Making Changes to Your Code

**On your local machine:**
```bash
cd /mnt/c/code/JOTFORM\ WEBHOOK/csd_integration

# See what changed
git status

# Add changed files
git add .

# Commit changes
git commit -m "Description of what you changed"

# Push to GitHub
git push
```

**On PythonAnywhere:**
```bash
cd ~/csd-integration

# Download latest changes
git pull

# Restart your web app (from Web tab)
```

---

## Visual Guide - How Git Works

```
Your Computer           GitHub            PythonAnywhere
(Local Code)         (Cloud Backup)      (Production)
     │                    │                    │
     │  git push          │                    │
     ├──────────────────→ │                    │
     │                    │  git clone         │
     │                    ├──────────────────→ │
     │                    │                    │
     │  git pull          │  git pull          │
     │ ←──────────────────┤ ←──────────────────┤
```

**Workflow:**
1. Make changes on your computer
2. `git push` to GitHub (backup)
3. `git pull` on PythonAnywhere (deploy)

---

## Troubleshooting

### "git: command not found"

**Fix:** Git isn't installed or not in PATH
- Windows: Reinstall Git, make sure to add to PATH
- WSL: Run `sudo apt install git`

### "Permission denied (publickey)"

**Fix:** Use HTTPS instead of SSH:
```bash
git remote set-url origin https://github.com/yourusername/csd-integration.git
```

### "Authentication failed"

**Fix:** Use Personal Access Token, not password:
- Regenerate token at https://github.com/settings/tokens
- Use token as password when prompted

### "fatal: not a git repository"

**Fix:** You're not in the right folder:
```bash
cd /mnt/c/code/JOTFORM\ WEBHOOK/csd_integration
git init  # if needed
```

### Can't push - "rejected" error

**Fix:** Pull first, then push:
```bash
git pull origin main
git push origin main
```

---

## Quick Reference Card

```bash
# ONE-TIME SETUP
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# START NEW PROJECT
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/user/repo.git
git push -u origin main

# DAILY WORKFLOW
git status                    # See what changed
git add .                     # Add all changes
git commit -m "message"       # Save snapshot
git push                      # Upload to GitHub

# UPDATE CODE
git pull                      # Download latest changes

# CHECK HISTORY
git log                       # See all commits
```

---

## Why This Helps for Your Project

**Before (manual upload):**
- Upload 15+ files one by one
- Easy to miss a file
- Hard to update later
- No backup

**After (with Git/GitHub):**
- One command uploads everything: `git push`
- One command updates PythonAnywhere: `git pull`
- All changes tracked
- Free cloud backup
- Can undo mistakes

---

## Next Steps

1. ✅ Install Git (Part 1)
2. ✅ Create GitHub account (Part 2)
3. ✅ Upload code to GitHub (Part 3)
4. ✅ Clone to PythonAnywhere (Part 4)
5. ✅ Complete deployment (Part 5)
6. ✅ Update JotForm webhook URL
7. ✅ Test!

---

## Need Help?

**Git official docs:** https://git-scm.com/doc
**GitHub guides:** https://guides.github.com/
**Interactive Git tutorial:** https://learngitbranching.js.org/

**Common beginner mistakes:**
- Forgetting to `git add .` before `git commit`
- Using password instead of Personal Access Token
- Not being in the right folder (`cd` to project first)

---

**You've got this!** Follow the steps above, and you'll have your code deployed in about 15 minutes total. Git seems scary at first, but you'll be using it confidently within a week.
