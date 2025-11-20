"""
Flask application for receiving JotForm webhooks and submitting to CSD Portal
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import BadRequest

import config
from models import Database
from csd_submitter import CSDSubmitter
from utils import setup_logging, parse_jotform_webhook, validate_webhook


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Setup logging
logger = setup_logging()

# Initialize database
db = Database()

# Initialize CSD submitter
csd_submitter = CSDSubmitter()


@app.route('/')
def index():
    """Homepage showing system status"""
    try:
        recent_submissions = db.get_all_submissions(limit=10)
        stats = {
            'total': len(db.get_all_submissions(limit=1000)),
            'pending': len(db.get_pending_submissions()),
            'failed': len(db.get_failed_submissions())
        }
        return render_template('index.html', submissions=recent_submissions, stats=stats)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return f"Error loading dashboard: {str(e)}", 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })


@app.route('/csd-webhook', methods=['POST'])
def csd_webhook():
    """
    Receive webhook from JotForm and process submission

    Expected webhook data format from JotForm:
    {
        "submissionID": "...",
        "rawRequest": {...},
        "formID": "...",
        ...
    }
    """
    try:
        # Get raw webhook data
        if request.is_json:
            webhook_data = request.get_json()
        else:
            webhook_data = request.form.to_dict()

        logger.info(f"Received webhook from JotForm: {webhook_data.get('submissionID', 'unknown')}")

        # Validate webhook (optional - if using webhook secret)
        if config.JOTFORM_WEBHOOK_SECRET:
            if not validate_webhook(request, config.JOTFORM_WEBHOOK_SECRET):
                logger.warning("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 403

        # Parse webhook data
        parsed_data = parse_jotform_webhook(webhook_data)

        if not parsed_data:
            logger.error("Failed to parse webhook data")
            return jsonify({'error': 'Invalid webhook data'}), 400

        # Save to database
        submission_id = db.insert_submission(parsed_data)
        logger.info(f"Saved submission to database with ID: {submission_id}")

        # Attempt to submit to CSD Portal
        try:
            result = csd_submitter.submit_to_csd(parsed_data['raw_data'])

            if result['success']:
                db.update_submission_status(
                    submission_id,
                    status='success',
                    confirmation_number=result.get('confirmation_number')
                )
                logger.info(f"Successfully submitted to CSD Portal: {submission_id}")
                return jsonify({
                    'success': True,
                    'message': 'Submitted to CSD Portal',
                    'submission_id': submission_id
                })
            else:
                # First attempt failed, try retry
                db.increment_retry_count(submission_id)

                if parsed_data.get('retry_count', 0) < config.MAX_RETRIES:
                    logger.info(f"Retrying submission {submission_id}")
                    result = csd_submitter.submit_to_csd(parsed_data['raw_data'])

                    if result['success']:
                        db.update_submission_status(
                            submission_id,
                            status='success',
                            confirmation_number=result.get('confirmation_number')
                        )
                        return jsonify({
                            'success': True,
                            'message': 'Submitted to CSD Portal (retry)',
                            'submission_id': submission_id
                        })

                # All retries failed
                db.update_submission_status(
                    submission_id,
                    status='failed',
                    error_message=result.get('error')
                )
                logger.error(f"Failed to submit to CSD Portal: {result.get('error')}")

                return jsonify({
                    'success': False,
                    'message': 'Failed to submit to CSD Portal',
                    'error': result.get('error'),
                    'submission_id': submission_id
                }), 500

        except Exception as e:
            logger.error(f"Error submitting to CSD Portal: {str(e)}", exc_info=True)
            db.update_submission_status(
                submission_id,
                status='failed',
                error_message=str(e)
            )
            return jsonify({
                'success': False,
                'message': 'Error processing submission',
                'error': str(e),
                'submission_id': submission_id
            }), 500

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/submissions')
def view_submissions():
    """View all submissions"""
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit', 100))

    submissions = db.get_all_submissions(status=status_filter, limit=limit)

    return render_template('submissions.html', submissions=submissions)


@app.route('/submission/<int:submission_id>')
def view_submission(submission_id):
    """View a single submission detail"""
    submission = db.get_submission(submission_id)

    if not submission:
        return "Submission not found", 404

    return render_template('submission_detail.html', submission=submission)


@app.route('/retry/<int:submission_id>', methods=['POST'])
def retry_submission(submission_id):
    """Manually retry a failed submission"""
    submission = db.get_submission(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    try:
        raw_data = json.loads(submission['raw_data'])
        result = csd_submitter.submit_to_csd(raw_data)

        if result['success']:
            db.update_submission_status(
                submission_id,
                status='success',
                confirmation_number=result.get('confirmation_number')
            )
            return jsonify({
                'success': True,
                'message': 'Successfully resubmitted'
            })
        else:
            db.increment_retry_count(submission_id)
            return jsonify({
                'success': False,
                'error': result.get('error')
            }), 500

    except Exception as e:
        logger.error(f"Error retrying submission: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/mapping')
def view_mapping():
    """View and edit field mappings"""
    try:
        with open(config.FIELD_MAPPING_FILE, 'r') as f:
            mapping_data = json.load(f)
        return render_template('mapping.html', mapping=mapping_data)
    except Exception as e:
        logger.error(f"Error loading mapping: {str(e)}")
        return f"Error loading mapping: {str(e)}", 500


@app.route('/mapping/update', methods=['POST'])
def update_mapping():
    """Update field mappings"""
    try:
        new_mapping = request.get_json()

        # Validate mapping structure
        if 'mappings' not in new_mapping:
            return jsonify({'error': 'Invalid mapping structure'}), 400

        # Backup current mapping
        backup_path = config.FIELD_MAPPING_FILE.with_suffix('.json.backup')
        with open(config.FIELD_MAPPING_FILE, 'r') as f:
            current_mapping = f.read()
        with open(backup_path, 'w') as f:
            f.write(current_mapping)

        # Save new mapping
        new_mapping['last_updated'] = datetime.now().isoformat()
        with open(config.FIELD_MAPPING_FILE, 'w') as f:
            json.dump(new_mapping, f, indent=2)

        logger.info("Field mapping updated successfully")

        return jsonify({
            'success': True,
            'message': 'Mapping updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating mapping: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    config.LOG_DIR.mkdir(exist_ok=True)

    # Run development server
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
