import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import asdict


class Database:
    def __init__(self, db_path: str = "data/job_agent.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self.conn = None
        self._init_db()

    def _ensure_db_dir(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def _get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                location TEXT,
                linkedin_url TEXT,
                summary TEXT,
                raw_resume_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                name TEXT,
                category TEXT,
                proficiency TEXT,
                years_experience REAL,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                company TEXT,
                title TEXT,
                location TEXT,
                start_date TEXT,
                end_date TEXT,
                description TEXT,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                institution TEXT,
                degree TEXT,
                field_of_study TEXT,
                start_date TEXT,
                end_date TEXT,
                gpa REAL,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT,
                source TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                employment_type TEXT,
                seniority_level TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                salary_currency TEXT,
                posted_date TEXT,
                application_url TEXT,
                easy_apply BOOLEAN,
                applicant_count INTEGER,
                company_url TEXT,
                company_logo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source, external_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                candidate_id INTEGER,
                fit_score INTEGER,
                status TEXT DEFAULT 'pending',
                resume_path TEXT,
                cover_letter_path TEXT,
                applied_at TIMESTAMP,
                viewed_at TIMESTAMP,
                responded_at TIMESTAMP,
                interview_at TIMESTAMP,
                offer_at TIMESTAMP,
                rejected_at TIMESTAMP,
                notes TEXT,
                screening_responses TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screening_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                question_text TEXT,
                answer_text TEXT,
                times_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                jobs_found INTEGER,
                applications_sent INTEGER,
                responses_received INTEGER,
                interviews_scheduled INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)
        """)

        conn.commit()

    def insert_candidate(self, data: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO candidates (name, email, phone, location, linkedin_url, summary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.get('name'), data.get('email'), data.get('phone'),
              data.get('location'), data.get('linkedin_url'), data.get('summary')))
        conn.commit()
        return cursor.lastrowid

    def get_candidate(self, candidate_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def insert_skill(self, candidate_id: int, skill: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO skills (candidate_id, name, category, proficiency, years_experience)
            VALUES (?, ?, ?, ?, ?)
        """, (candidate_id, skill.get('name'), skill.get('category'),
              skill.get('proficiency'), skill.get('years_experience')))
        conn.commit()
        return cursor.lastrowid

    def get_candidate_skills(self, candidate_id: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills WHERE candidate_id = ?", (candidate_id,))
        return [dict(row) for row in cursor.fetchall()]

    def insert_experience(self, candidate_id: int, exp: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO experience (candidate_id, company, title, location, start_date, end_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (candidate_id, exp.get('company'), exp.get('title'), exp.get('location'),
              exp.get('start_date'), exp.get('end_date'), exp.get('description')))
        conn.commit()
        return cursor.lastrowid

    def get_candidate_experience(self, candidate_id: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experience WHERE candidate_id = ?", (candidate_id,))
        return [dict(row) for row in cursor.fetchall()]

    def insert_education(self, candidate_id: int, edu: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO education (candidate_id, institution, degree, field_of_study, start_date, end_date, gpa)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (candidate_id, edu.get('institution'), edu.get('degree'), edu.get('field_of_study'),
              edu.get('start_date'), edu.get('end_date'), edu.get('gpa')))
        conn.commit()
        return cursor.lastrowid

    def get_candidate_education(self, candidate_id: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM education WHERE candidate_id = ?", (candidate_id,))
        return [dict(row) for row in cursor.fetchall()]

    def insert_job(self, job: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO jobs (
                    external_id, source, title, company, location, description,
                    employment_type, seniority_level, salary_min, salary_max, salary_currency,
                    posted_date, application_url, easy_apply, applicant_count, company_url, company_logo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (job.get('external_id'), job.get('source'), job.get('title'),
                  job.get('company'), job.get('location'), job.get('description'),
                  job.get('employment_type'), job.get('seniority_level'), job.get('salary_min'),
                  job.get('salary_max'), job.get('salary_currency'), job.get('posted_date'),
                  job.get('application_url'), job.get('easy_apply'), job.get('applicant_count'),
                  job.get('company_url'), job.get('company_logo')))
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else self.get_job_by_external(job.get('source'), job.get('external_id'))['id']
        except sqlite3.IntegrityError:
            return self.get_job_by_external(job.get('source'), job.get('external_id'))['id']

    def get_job_by_external(self, source: str, external_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE source = ? AND external_id = ?", (source, external_id))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_jobs(self, source: Optional[str] = None, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if source:
            cursor.execute("SELECT * FROM jobs WHERE source = ? ORDER BY created_at DESC LIMIT ?", (source, limit))
        else:
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def insert_application(self, app: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (
                job_id, candidate_id, fit_score, status, resume_path,
                cover_letter_path, applied_at, screening_responses
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (app.get('job_id'), app.get('candidate_id'), app.get('fit_score'),
              app.get('status', 'pending'), app.get('resume_path'),
              app.get('cover_letter_path'), app.get('applied_at'),
              app.get('screening_responses')))
        conn.commit()
        return cursor.lastrowid

    def update_application_status(self, app_id: int, status: str, timestamp: Optional[str] = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        ts = timestamp or datetime.now().isoformat()
        cursor.execute(f"""
            UPDATE applications SET status = ?, updated_at = ?, {status}_at = ?
            WHERE id = ?
        """, (status, ts, ts, app_id))
        conn.commit()

    def get_applications(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute("""
                SELECT a.*, j.title, j.company, j.location, j.source
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.status = ?
                ORDER BY a.created_at DESC LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT a.*, j.title, j.company, j.location, j.source
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                ORDER BY a.created_at DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_application_stats(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) as count FROM applications GROUP BY status")
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as total FROM applications")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT AVG(fit_score) as avg_score FROM applications WHERE fit_score IS NOT NULL")
        avg_score = cursor.fetchone()['avg_score'] or 0

        return {
            'total': total,
            'by_status': status_counts,
            'avg_fit_score': round(avg_score, 1)
        }

    def insert_screening_qa(self, qa: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO screening_questions (source, question_text, answer_text, times_used)
            VALUES (?, ?, ?, COALESCE((SELECT times_used FROM screening_questions WHERE source = ? AND question_text = ?), 0))
        """, (qa.get('source'), qa.get('question_text'), qa.get('answer_text'),
              qa.get('source'), qa.get('question_text')))
        conn.commit()
        return cursor.lastrowid

    def get_screening_answer(self, question: str, source: str) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT answer_text FROM screening_questions
            WHERE source = ? AND question_text LIKE ?
            ORDER BY times_used DESC LIMIT 1
        """, (source, f"%{question[:50]}%"))
        row = cursor.fetchone()
        return row['answer_text'] if row else None

    def add_to_blacklist(self, company: str, reason: str = ""):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO company_blacklist (company_name, reason) VALUES (?, ?)", (company, reason))
        conn.commit()

    def add_to_whitelist(self, company: str, priority: int = 1):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO company_whitelist (company_name, priority) VALUES (?, ?)", (company, priority))
        conn.commit()

    def is_blacklisted(self, company: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM company_blacklist WHERE company_name = ?", (company,))
        return cursor.fetchone() is not None

    def is_whitelisted(self, company: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM company_whitelist WHERE company_name = ?", (company,))
        return cursor.fetchone() is not None

    def get_whitelist_companies(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT company_name FROM company_whitelist ORDER BY priority DESC")
        return [row['company_name'] for row in cursor.fetchall()]

    def get_blacklist_companies(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, reason FROM company_blacklist")
        return [{'name': row['company_name'], 'reason': row['reason']} for row in cursor.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()


db = Database()