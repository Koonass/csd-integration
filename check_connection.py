"""
Quick diagnostic script to check if everything is set up correctly
"""
import sys
import os
import requests
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_files():
    """Check if all required files exist"""
    print_header("1. Checking Project Files")

    required_files = [
        'app.py',
        'config.py',
        'models.py',
        'csd_submitter.py',
        'utils.py',
        'field_mapping.json',
        'requirements.txt'
    ]

    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING!")
            all_present = False

    return all_present


def check_dependencies():
    """Check if Python packages are installed"""
    print_header("2. Checking Dependencies")

    required_packages = ['flask', 'requests', 'bs4']
    all_installed = True

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED!")
            all_installed = False

    if not all_installed:
        print("\nTo install missing packages:")
        print("  pip install -r requirements.txt")

    return all_installed


def check_flask_running(base_url='http://localhost:5000'):
    """Check if Flask app is running"""
    print_header("3. Checking Flask Application")

    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ Flask app is running at {base_url}")
            print(f"  Health check response: {response.json()}")
            return True
        else:
            print(f"✗ Flask app responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Flask app at {base_url}")
        print("\n  The Flask app is NOT running.")
        print("  Start it with: python app.py")
        return False
    except Exception as e:
        print(f"✗ Error checking Flask app: {str(e)}")
        return False


def check_database():
    """Check if database exists and is accessible"""
    print_header("4. Checking Database")

    db_file = Path('submissions.db')

    if db_file.exists():
        print(f"✓ Database file exists: {db_file}")

        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM submissions")
            count = cursor.fetchone()[0]
            print(f"  Current submissions: {count}")
            conn.close()
            return True
        except Exception as e:
            print(f"✗ Error accessing database: {str(e)}")
            return False
    else:
        print(f"⚠ Database doesn't exist yet (will be created on first run)")
        return True


def check_logs():
    """Check if logs directory exists"""
    print_header("5. Checking Logs")

    log_dir = Path('logs')
    log_file = log_dir / 'submissions.log'

    if log_dir.exists():
        print(f"✓ Log directory exists")
        if log_file.exists():
            # Get last few lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-5:] if len(lines) >= 5 else lines
                if last_lines:
                    print(f"  Last log entries:")
                    for line in last_lines:
                        print(f"    {line.strip()}")
        else:
            print(f"  No log file yet (will be created on first run)")
        return True
    else:
        print(f"⚠ Log directory doesn't exist (will be created on first run)")
        return True


def check_webhook_url():
    """Guide user on webhook configuration"""
    print_header("6. Webhook Configuration")

    print("For JotForm webhook to work, you need a PUBLIC URL.")
    print("\nCurrent situation:")
    print("  ✗ http://localhost:5000/csd-webhook - NOT publicly accessible")
    print("  ✗ http://127.0.0.1:5000/csd-webhook - NOT publicly accessible")
    print("\nOptions:")
    print("  1. Use test_webhook.py to test locally (no JotForm needed)")
    print("  2. Use ngrok to expose localhost (free, temporary URL)")
    print("  3. Deploy to PythonAnywhere (free, permanent URL)")
    print("\nSee WEBHOOK_TROUBLESHOOTING.md for detailed instructions.")


def main():
    """Run all checks"""
    print("\n" + "🔍 CSD Integration System Diagnostics" + "\n")

    checks = [
        ("Files", check_files()),
        ("Dependencies", check_dependencies()),
        ("Flask App", check_flask_running()),
        ("Database", check_database()),
        ("Logs", check_logs())
    ]

    check_webhook_url()

    # Summary
    print_header("Summary")

    all_passed = all(result for _, result in checks)

    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print("\n" + "="*60)

    if all_passed:
        print("\n✓ All checks passed!")
        print("\nNext steps:")
        print("  1. If Flask app is running, test with:")
        print("     python test_webhook.py")
        print("  2. If not running, start it:")
        print("     python app.py")
        print("  3. For JotForm integration, see:")
        print("     WEBHOOK_TROUBLESHOOTING.md")
    else:
        print("\n⚠ Some checks failed. Review the output above.")
        print("   See WEBHOOK_TROUBLESHOOTING.md for solutions.")

    print("\n")


if __name__ == '__main__':
    main()
