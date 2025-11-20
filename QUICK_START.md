# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher installed
- JotForm account with existing form
- Access to CSD Portal

## Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd csd_integration

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Test Locally (2 minutes)

```bash
# Start the Flask application
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

Open browser to http://localhost:5000 - you should see the dashboard!

## Step 3: Test Webhook (1 minute)

In a new terminal:

```bash
# Activate virtual environment again
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux

# Run test
python test_webhook.py
```

Check the dashboard - you should see a test submission!

## Step 4: Review Field Mapping

1. Go to http://localhost:5000/mapping
2. Review the field mappings
3. Note which fields need adjustment
4. Edit `field_mapping.json` if needed

## Step 5: Configure JotForm Webhook

1. Log into JotForm
2. Go to your form settings
3. Settings → Integrations → Webhooks
4. Add webhook URL:
   - For local testing: Use ngrok or similar tunnel
   - For production: `https://yourusername.pythonanywhere.com/csd-webhook`
5. Test by submitting the form

## Important Notes

### Field Mapping Review Needed

The current field mapping is a **starting point**. You'll need to review and update `field_mapping.json` because:

1. **Some JotForm fields don't have direct CSD equivalents**
   - These are mapped to COMPOSITE_NOTES (combined into notes field)
   - You may want to map them differently

2. **CSD Portal requires these fields:**
   - Project Name (currently auto-generated from builder + plan)
   - Province/State (currently defaults to "GA")
   - You may want to add these to your JotForm

3. **Test with real data before production:**
   ```bash
   # Submit test form in JotForm
   # Check logs/submissions.log
   # Verify submission appears in CSD Portal
   ```

### Files to Customize

- `field_mapping.json` - Adjust field mappings
- `config.py` - Change settings (URLs, timeouts, etc.)
- `csd_submitter.py` - Customize CSD submission logic if needed

### Next Steps After Testing

1. **Review field mappings** - Update based on your needs
2. **Test CSD submission** - Verify data appears correctly
3. **Add missing fields** - Add required CSD fields to JotForm
4. **Deploy to PythonAnywhere** - See README.md for deployment guide
5. **Configure JotForm webhook** - Point to production URL
6. **Monitor first submissions** - Watch logs closely

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Can't access http://localhost:5000
- Check if Flask app is running
- Check firewall settings
- Try http://127.0.0.1:5000

### Test webhook fails
- Make sure Flask app is running first
- Check logs/submissions.log for errors

### Need help?
1. Check logs: `tail -f logs/submissions.log`
2. View README.md for detailed documentation
3. Check database: `sqlite3 submissions.db "SELECT * FROM submissions;"`

## What's Next?

### For Development:
- Run test submissions
- Refine field mappings
- Test error handling
- Review logs

### For Production:
- Deploy to PythonAnywhere (see README.md)
- Update JotForm webhook URL
- Monitor first real submissions
- Set up backups

## Quick Reference

```bash
# Start app
python app.py

# Test webhook
python test_webhook.py

# View logs
tail -f logs/submissions.log

# Check database
sqlite3 submissions.db "SELECT * FROM submissions ORDER BY submission_date DESC LIMIT 5;"

# View dashboard
# http://localhost:5000
```

Good luck! 🚀
