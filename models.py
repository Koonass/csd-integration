"""
Database models for tracking submissions
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import config


class Database:
    """Handle all database operations"""

    def __init__(self, db_path: Path = config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                jotform_submission_id TEXT UNIQUE NOT NULL,
                submitter_name TEXT,
                submitter_email TEXT,
                builder_name TEXT,
                plan_name TEXT,
                csd_submission_status TEXT DEFAULT 'pending',
                csd_submission_date TIMESTAMP,
                csd_confirmation_number TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                raw_data TEXT NOT NULL
            )
        ''')

        # Create field mapping history table (for tracking changes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS field_mapping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mapping_version TEXT,
                mapping_data TEXT NOT NULL,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def insert_submission(self, data: Dict[str, Any]) -> int:
        """Insert a new submission record"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO submissions (
                jotform_submission_id,
                submitter_name,
                submitter_email,
                builder_name,
                plan_name,
                raw_data
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('jotform_id'),
            data.get('submitter_name'),
            data.get('submitter_email'),
            data.get('builder_name'),
            data.get('plan_name'),
            json.dumps(data.get('raw_data', {}))
        ))

        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return submission_id

    def update_submission_status(
        self,
        submission_id: int,
        status: str,
        confirmation_number: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update the status of a submission"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE submissions
            SET csd_submission_status = ?,
                csd_submission_date = CURRENT_TIMESTAMP,
                csd_confirmation_number = ?,
                error_message = ?
            WHERE id = ?
        ''', (status, confirmation_number, error_message, submission_id))

        conn.commit()
        conn.close()

    def increment_retry_count(self, submission_id: int):
        """Increment the retry count for a submission"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE submissions
            SET retry_count = retry_count + 1
            WHERE id = ?
        ''', (submission_id,))

        conn.commit()
        conn.close()

    def get_submission(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a submission by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_submissions(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve all submissions, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute('''
                SELECT * FROM submissions
                WHERE csd_submission_status = ?
                ORDER BY submission_date DESC
                LIMIT ?
            ''', (status, limit))
        else:
            cursor.execute('''
                SELECT * FROM submissions
                ORDER BY submission_date DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_failed_submissions(self) -> List[Dict[str, Any]]:
        """Get all failed submissions that need manual review"""
        return self.get_all_submissions(status='failed')

    def get_pending_submissions(self) -> List[Dict[str, Any]]:
        """Get all pending submissions"""
        return self.get_all_submissions(status='pending')
