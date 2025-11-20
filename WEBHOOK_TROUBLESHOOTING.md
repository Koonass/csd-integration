# Webhook Connection Troubleshooting

## The Problem

JotForm webhooks need a **publicly accessible URL** (reachable from the internet).

- ❌ `http://localhost:5000/csd-webhook` - Only accessible on your computer
- ❌ `http://127.0.0.1:5000/csd-webhook` - Same as localhost
- ✅ `https://yourname.pythonanywhere.com/csd-webhook` - Public URL
- ✅ `https://abc123.ngrok.io/csd-webhook` - Public URL via tunnel

## Solutions

### Option 1: Test Locally Without JotForm (FASTEST)

Use the test script to simulate JotForm webhooks:

```bash
# Make sure Flask is running in one terminal
python app.py

# In another terminal, run the test
python test_webhook.py
```

This will send test data directly to your local server and you should see:
- Submission appears in dashboard
- Data saved to database
- Entry in logs

### Option 2: Use ngrok for Local Testing (RECOMMENDED FOR DEVELOPMENT)

ngrok creates a public URL that tunnels to your localhost.

**Step 1: Download ngrok**
- Go to https://ngrok.com/download
- Download for Windows
- Extract ngrok.exe

**Step 2: Start ngrok**
```bash
# In a new terminal
ngrok http 5000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

**Step 3: Update JotForm webhook**
- Copy the https URL (e.g., `https://abc123.ngrok.io`)
- Go to JotForm → Form Settings → Integrations → Webhooks
- Set webhook URL to: `https://abc123.ngrok.io/csd-webhook`

**Step 4: Test**
- Submit your JotForm
- Watch ngrok terminal for incoming requests
- Check dashboard for submission

**Important:** ngrok URL changes each time you restart ngrok (free plan). You'll need to update JotForm webhook each time.

### Option 3: Deploy to PythonAnywhere (RECOMMENDED FOR PRODUCTION)

Deploy your app to PythonAnywhere for a permanent public URL.

**See README.md for full deployment instructions**

Quick steps:
1. Sign up at https://www.pythonanywhere.com (free account works)
2. Upload files
3. Install dependencies
4. Configure web app
5. Use URL: `https://yourusername.pythonanywhere.com/csd-webhook`

## Checking If Webhook is Working

### 1. Verify Flask App is Running

```bash
# Should show "Running on http://127.0.0.1:5000"
python app.py
```

### 2. Test Health Endpoint Locally

```bash
# Open browser to:
http://localhost:5000/health

# Or use curl:
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "database": "connected"
}
```

### 3. Check Logs

```bash
# Watch logs in real-time
tail -f logs/submissions.log
```

### 4. Check Database

```bash
# See all submissions
sqlite3 submissions.db "SELECT * FROM submissions;"

# Count submissions
sqlite3 submissions.db "SELECT COUNT(*) FROM submissions;"
```

## Common Issues

### Issue: "Connection refused" when testing

**Cause:** Flask app not running

**Solution:**
```bash
python app.py
```

### Issue: No submissions appear after JotForm submission

**Cause:** JotForm can't reach localhost

**Solutions:**
- Use test_webhook.py for local testing
- Use ngrok to expose localhost
- Deploy to PythonAnywhere

### Issue: ngrok URL not working

**Checks:**
1. Is ngrok running? Check terminal
2. Is Flask running? Check other terminal
3. Did you use the HTTPS URL (not HTTP)?
4. Did you add `/csd-webhook` to the end?

### Issue: JotForm says "Webhook failed"

**Checks:**
1. Is the URL publicly accessible?
2. Test in browser - should return JSON response
3. Check JotForm webhook logs for error details
4. Check your app logs: `tail -f logs/submissions.log`

## Testing Checklist

- [ ] Flask app running (`python app.py`)
- [ ] Can access dashboard (http://localhost:5000)
- [ ] Health check works (http://localhost:5000/health)
- [ ] Test script works (`python test_webhook.py`)
- [ ] Either:
  - [ ] ngrok running and URL updated in JotForm, OR
  - [ ] Deployed to PythonAnywhere with URL in JotForm
- [ ] JotForm webhook configured and enabled
- [ ] Test submission sent from JotForm
- [ ] Submission appears in dashboard

## Debugging Steps

### Step 1: Test Flask App Locally

```bash
# Terminal 1: Start Flask
python app.py

# Terminal 2: Test health
curl http://localhost:5000/health

# Terminal 3: Send test webhook
python test_webhook.py
```

### Step 2: Check for Errors

```bash
# View logs
cat logs/submissions.log

# Check recent errors
grep ERROR logs/submissions.log
```

### Step 3: Test Public URL

```bash
# If using ngrok
curl https://your-ngrok-url.ngrok.io/health

# If using PythonAnywhere
curl https://yourusername.pythonanywhere.com/health
```

### Step 4: Test JotForm Webhook

1. Go to JotForm → Form Settings → Integrations → Webhooks
2. Click "Test Webhook"
3. Check if request arrives in logs
4. Check dashboard for submission

## Quick Reference

```bash
# Start Flask app
python app.py

# Test locally
python test_webhook.py

# Start ngrok (in separate terminal)
ngrok http 5000

# Watch logs
tail -f logs/submissions.log

# Check database
sqlite3 submissions.db "SELECT id, builder_name, csd_submission_status FROM submissions;"
```

## Next Steps After Connection Works

1. Submit real JotForm data
2. Verify field mappings are correct
3. Check data appears properly in dashboard
4. Test CSD Portal submission
5. Fix any field mapping issues
