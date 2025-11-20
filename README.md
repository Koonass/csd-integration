# CSD Portal Integration

Automated system for receiving JotForm submissions and forwarding them to the CSD Portal.

## Overview

This Flask application receives webhook notifications from JotForm, stores submission data in a local database, and automatically submits the data to the CSD Portal design request form.

## Features

- **Webhook Receiver**: Accepts JotForm webhook POST requests
- **Database Tracking**: SQLite database for audit trail and backup
- **Field Mapping**: JSON-based configuration for easy field mapping updates
- **Retry Logic**: Automatic retry for failed submissions
- **Web Dashboard**: View submission status and history
- **Manual Retry**: Retry failed submissions through web interface
- **Error Logging**: Comprehensive logging for debugging

## Project Structure

```
csd_integration/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── models.py                   # Database models and operations
├── csd_submitter.py            # CSD Portal submission logic
├── utils.py                    # Utility functions
├── field_mapping.json          # Field mapping configuration (EDITABLE)
├── requirements.txt            # Python dependencies
├── submissions.db              # SQLite database (auto-created)
├── templates/                  # HTML templates
│   ├── index.html
│   ├── submissions.html
│   ├── submission_detail.html
│   └── mapping.html
├── logs/                       # Log files (auto-created)
│   └── submissions.log
└── static/                     # Static files (CSS, JS)
    ├── css/
    └── js/
```

## Installation

### Local Development

1. **Install Python 3.8+** (if not already installed)

2. **Navigate to project directory:**
   ```bash
   cd csd_integration
   ```

3. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the dashboard:**
   Open browser to `http://localhost:5000`

### PythonAnywhere Deployment

1. **Upload files to PythonAnywhere:**
   - Use Git or file upload
   - Place in `/home/yourusername/csd-integration/`

2. **Install dependencies:**
   ```bash
   pip install --user -r requirements.txt
   ```

3. **Configure Web App:**
   - Dashboard → Web tab → Add new web app
   - Choose Flask
   - Point to `app.py`
   - Set working directory

4. **Update JotForm webhook URL:**
   - Go to JotForm form settings
   - Settings → Integrations → Webhooks
   - Add: `https://yourusername.pythonanywhere.com/csd-webhook`

## Configuration

### Environment Variables

Set these in PythonAnywhere or your local environment:

```bash
# Optional - JotForm webhook secret for security
export JOTFORM_WEBHOOK_SECRET="your-secret-here"

# Flask secret key (change in production)
export FLASK_SECRET_KEY="your-secret-key"

# Debug mode (False for production)
export FLASK_DEBUG="False"

# Admin email for notifications
export ADMIN_EMAIL="your-email@example.com"
```

### Field Mapping

Edit `field_mapping.json` to customize field mappings. The file structure:

```json
{
  "version": "1.0",
  "mappings": [
    {
      "jotform_field": "builderName",
      "jotform_label": "Builder Name",
      "csd_field": "ctl00_cphBody_txtBuilderName",
      "csd_field_type": "text",
      "required": true,
      "transform": null,
      "notes": "Main builder/company name"
    }
  ]
}
```

**Field Mapping Types:**

- **Direct mapping**: `transform: null` - Value copied as-is
- **Composite notes**: `csd_field: "COMPOSITE_NOTES"` - Added to notes field
- **Value mapping**: `transform: "map_roof_type"` - Value transformed via mapping
- **File upload**: `transform: "upload_file"` - File downloaded and uploaded

## Testing

### Test Webhook Locally

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Use the test script:**
   ```bash
   python test_webhook.py
   ```

3. **Or use curl:**
   ```bash
   curl -X POST http://localhost:5000/csd-webhook \
     -H "Content-Type: application/json" \
     -d @test_data.json
   ```

### Test JotForm Integration

1. Submit a test form in JotForm
2. Check logs: `logs/submissions.log`
3. View in dashboard: `http://localhost:5000/submissions`
4. Verify in CSD Portal

## Usage

### Webhook Endpoint

**URL:** `/csd-webhook`
**Method:** POST
**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

JotForm automatically sends data when a form is submitted.

### Web Interface

- **Dashboard** (`/`): Overview and recent submissions
- **All Submissions** (`/submissions`): Full submission history
- **Submission Detail** (`/submission/<id>`): Individual submission details
- **Field Mapping** (`/mapping`): View current field mappings
- **Health Check** (`/health`): API health status

### Manual Retry

For failed submissions:

1. Go to Submissions page
2. Click "View" on failed submission
3. Click "Retry Submission" button
4. Or use API: `POST /retry/<submission_id>`

## Monitoring

### Check Logs

```bash
tail -f logs/submissions.log
```

### Database Query

```bash
sqlite3 submissions.db "SELECT * FROM submissions ORDER BY submission_date DESC LIMIT 10;"
```

### Failed Submissions

```bash
sqlite3 submissions.db "SELECT * FROM submissions WHERE csd_submission_status='failed';"
```

## Troubleshooting

### Webhook Not Receiving Data

1. Check JotForm webhook configuration
2. Verify URL is correct (include `/csd-webhook`)
3. Check PythonAnywhere error logs
4. Test with curl locally

### CSD Portal Submission Fails

1. Check error message in database
2. Verify field mapping is correct
3. Test CSD Portal manually
4. Check if CSD Portal form changed
5. Review logs for ASP.NET errors

### Database Errors

1. Check file permissions
2. Ensure SQLite is installed
3. Delete `submissions.db` and restart (recreates database)

### Import Errors

1. Verify all dependencies installed: `pip install -r requirements.txt`
2. Check Python version (3.8+)
3. Check virtual environment is activated

## Maintenance

### Backup Database

```bash
# Copy database file
cp submissions.db submissions_backup_$(date +%Y%m%d).db

# Or export to CSV
sqlite3 submissions.db -csv -header "SELECT * FROM submissions;" > backup.csv
```

### Update Field Mapping

1. Edit `field_mapping.json`
2. Backup current version first
3. Test with sample submission
4. Restart application if needed

### Monitor Disk Space

Database and logs grow over time. Monitor disk usage:

```bash
du -h submissions.db
du -h logs/
```

## Security Considerations

1. **Enable webhook secret** in JotForm settings
2. **Use HTTPS** in production (PythonAnywhere provides SSL)
3. **Secure database file** with proper permissions
4. **Don't commit secrets** to version control
5. **Rotate Flask secret key** periodically

## Future Enhancements

- [ ] Email notifications for failed submissions
- [ ] Web-based field mapping editor
- [ ] File attachment handling
- [ ] Bulk retry functionality
- [ ] Statistics and analytics dashboard
- [ ] Export submissions to CSV/Excel
- [ ] Scheduled health checks
- [ ] Integration with other systems

## Support

For issues:

1. Check logs: `logs/submissions.log`
2. Review database: Failed submissions
3. Test connectivity: Health check endpoint
4. Review field mapping: `/mapping` page

## License

Internal use only - Company proprietary

## Version History

- **v1.0** - Initial release
  - JotForm webhook receiver
  - CSD Portal submission
  - Field mapping system
  - Web dashboard
  - Database tracking
