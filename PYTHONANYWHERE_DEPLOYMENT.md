# PythonAnywhere Deployment Guide

## Step-by-Step Deployment

### Step 1: Prepare Files for Upload

You have two options to upload files:

#### Option A: Upload via Web Interface

1. Log into PythonAnywhere: https://www.pythonanywhere.com
2. Go to **Files** tab
3. Create directory: `/home/yourusername/csd-integration/`
4. Upload all files from your `csd_integration` folder

#### Option B: Use Git (Recommended)

**On your local machine:**

```bash
cd "/mnt/c/code/JOTFORM WEBHOOK/csd_integration"

# Initialize git if not already
git init
git add .
git commit -m "Initial CSD integration deployment"

# Push to GitHub/GitLab (create repo first)
git remote add origin https://github.com/yourusername/csd-integration.git
git push -u origin main
```

**On PythonAnywhere console:**

```bash
cd ~
git clone https://github.com/yourusername/csd-integration.git
```

---

### Step 2: Install Dependencies on PythonAnywhere

1. Open a **Bash console** on PythonAnywhere
2. Run these commands:

```bash
cd ~/csd-integration

# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Expected output:** All packages install successfully

---

### Step 3: Set Up Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose:
   - **Manual configuration** (not Flask wizard)
   - **Python 3.10** (or whatever version you prefer)
4. Click through to create

---

### Step 4: Configure WSGI File

1. In the **Web** tab, find the **Code** section
2. Click on the WSGI configuration file link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Delete all the existing content**
4. **Paste this code:**

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/csd-integration'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Flask app
from app import app as application
```

**IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username!

5. **Save** the file (Ctrl+S or click Save button)

---

### Step 5: Set Working Directory and Virtual Environment

Back in the **Web** tab:

1. **Source code:** Set to `/home/yourusername/csd-integration`
2. **Working directory:** Set to `/home/yourusername/csd-integration`
3. **Virtualenv:** Set to `/home/yourusername/csd-integration/venv`

---

### Step 6: Reload Web App

1. Scroll to top of **Web** tab
2. Click the big green **Reload** button
3. Wait for it to finish

---

### Step 7: Test the Deployment

1. Visit your site: `https://yourusername.pythonanywhere.com`
2. You should see the dashboard!
3. Test health endpoint: `https://yourusername.pythonanywhere.com/health`

**If you get errors:**
- Check the **Error log** link in the Web tab
- Check the **Server log** link
- See troubleshooting section below

---

### Step 8: Update JotForm Webhook

1. Go to JotForm: https://form.jotform.com/240734091032042
2. Settings → Integrations → Webhooks
3. **Add new webhook** or edit existing
4. Set URL to: `https://yourusername.pythonanywhere.com/csd-webhook`
5. **Save**
6. Click **Test Webhook** to verify

---

### Step 9: Test End-to-End

1. Submit your JotForm
2. Check PythonAnywhere dashboard: `https://yourusername.pythonanywhere.com`
3. Submission should appear!
4. Check logs on PythonAnywhere:
   ```bash
   cd ~/csd-integration
   tail -f logs/submissions.log
   ```

---

## Troubleshooting

### Error: "ImportError: No module named 'flask'"

**Fix:**
```bash
cd ~/csd-integration
source venv/bin/activate
pip install -r requirements.txt
```

Make sure the virtualenv path in Web tab matches: `/home/yourusername/csd-integration/venv`

---

### Error: "No such file or directory: 'submissions.db'"

**Fix:** Database needs to be created
```bash
cd ~/csd-integration
source venv/bin/activate
python -c "from models import Database; db = Database()"
```

Or just let it auto-create on first submission.

---

### Error: "Permission denied" on logs directory

**Fix:**
```bash
cd ~/csd-integration
mkdir -p logs
chmod 755 logs
```

---

### Can't see the dashboard (blank page or 500 error)

1. Check **Error log** in Web tab
2. Common issues:
   - WSGI file has wrong username
   - Virtual environment path is wrong
   - Working directory not set
   - Import error (check error log)

**Debug steps:**
```bash
cd ~/csd-integration
source venv/bin/activate
python app.py  # Test locally first
```

---

### Webhook receives but nothing happens

Check logs:
```bash
cd ~/csd-integration
tail -f logs/submissions.log
```

Check database:
```bash
cd ~/csd-integration
python -c "from models import Database; db = Database(); print(db.get_all_submissions())"
```

---

## File Permissions

Make sure files are readable:
```bash
cd ~/csd-integration
chmod 644 *.py *.json *.txt *.md
chmod 755 logs
chmod 644 logs/*.log
```

---

## Updating Your Deployment

When you make changes locally:

**Option 1: Git (Recommended)**
```bash
# Local machine
git add .
git commit -m "Update message"
git push

# PythonAnywhere console
cd ~/csd-integration
git pull
source venv/bin/activate
pip install -r requirements.txt  # if requirements changed

# Then reload web app from Web tab
```

**Option 2: File Upload**
1. Upload changed files via Files tab
2. Reload web app from Web tab

---

## Monitoring in Production

### View Logs
```bash
cd ~/csd-integration
tail -f logs/submissions.log
```

### Check Database
```bash
cd ~/csd-integration
source venv/bin/activate
python -c "from models import Database; db = Database(); subs = db.get_all_submissions(limit=5); print(f'Total: {len(subs)} submissions')"
```

### Download Database Backup
1. Go to **Files** tab
2. Navigate to `csd-integration/submissions.db`
3. Click **Download** button
4. Save locally with date: `submissions_backup_2024-11-20.db`

---

## Environment Variables (Optional)

For production secrets:

1. Click **Bash console**
2. Edit `.bashrc`:
   ```bash
   nano ~/.bashrc
   ```
3. Add at end:
   ```bash
   export FLASK_SECRET_KEY="your-secure-random-key-here"
   export JOTFORM_WEBHOOK_SECRET="your-jotform-secret"
   ```
4. Save and reload:
   ```bash
   source ~/.bashrc
   ```
5. Reload web app

---

## URLs Reference

After deployment, these URLs will work:

- **Dashboard:** `https://yourusername.pythonanywhere.com/`
- **Submissions:** `https://yourusername.pythonanywhere.com/submissions`
- **Field Mapping:** `https://yourusername.pythonanywhere.com/mapping`
- **Health Check:** `https://yourusername.pythonanywhere.com/health`
- **Webhook (for JotForm):** `https://yourusername.pythonanywhere.com/csd-webhook`

---

## Quick Deployment Checklist

- [ ] Files uploaded to `/home/yourusername/csd-integration/`
- [ ] Virtual environment created and packages installed
- [ ] Web app created (Manual configuration, Python 3.10)
- [ ] WSGI file configured with correct username
- [ ] Source code path set in Web tab
- [ ] Working directory set in Web tab
- [ ] Virtualenv path set in Web tab
- [ ] Web app reloaded
- [ ] Dashboard accessible in browser
- [ ] Health check returns JSON
- [ ] JotForm webhook URL updated
- [ ] Test submission sent from JotForm
- [ ] Submission appears in dashboard

---

## Need Help?

1. **Check PythonAnywhere forums:** https://www.pythonanywhere.com/forums/
2. **Check error logs:** Web tab → Error log link
3. **Check server logs:** Web tab → Server log link
4. **Test locally first:** Ensure app works locally before deploying

---

**Ready to deploy?** Follow the steps above in order, and you'll be live in about 15 minutes!
