import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DailyDigest:
    date: str
    jobs_found: int
    applications_sent: int
    responses_received: int
    interviews_scheduled: int


class NotificationSystem:
    def __init__(self, config: Optional[Dict] = None):
        self.email_config = config.get('email', {}) if config else {}
        self.whatsapp_config = config.get('whatsapp', {}) if config else {}

    def send_daily_digest(self, stats: Dict) -> bool:
        message = self._format_digest_message(stats)

        if self.email_config.get('enabled'):
            return self._send_email(message)

        if self.whatsapp_config.get('enabled'):
            return self._send_whatsapp(message)

        print("Daily Digest (no notifications configured):")
        print(message)
        return True

    def _format_digest_message(self, stats: Dict) -> str:
        message = f"""
🤖 Job Agent Daily Digest
━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {datetime.now().strftime('%Y-%m-%d')}

📊 YESTERDAY'S SUMMARY:
• Jobs Discovered: {stats.get('jobs_found', 0)}
• Applications Sent: {stats.get('applications_sent', 0)}
• Responses Received: {stats.get('responses_received', 0)}
• Interviews Scheduled: {stats.get('interviews_scheduled', 0)}

📈 TOTAL APPLICATION STATS:
• Total Applied: {stats.get('total_applied', 0)}
• Pending: {stats.get('pending', 0)}
• Viewed: {stats.get('viewed', 0)}
• Interview: {stats.get('interview', 0)}
• Offers: {stats.get('offers', 0)}
• Rejected: {stats.get('rejected', 0)}

💡 TIPS:
• Keep your resume updated for each application
• Follow up on applications after 1 week
• Practice interview questions for jobs you're excited about

━━━━━━━━━━━━━━━━━━━━━━━━━
Keep going! Your next opportunity is coming. 🚀
"""
        return message

    def _send_email(self, message: str) -> bool:
        try:
            smtp_host = self.email_config.get('smtp_host')
            smtp_port = self.email_config.get('smtp_port', 587)
            username = self.email_config.get('username')
            password = self.email_config.get('password')
            from_email = self.email_config.get('from_email')
            to_emails = self.email_config.get('to_emails', [])

            if not all([smtp_host, username, password, from_email, to_emails]):
                print("Email config incomplete")
                return False

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"🤖 Job Agent Daily Digest - {datetime.now().strftime('%Y-%m-%d')}"

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(username, password)
            server.sendmail(from_email, to_emails, msg.as_string())
            server.quit()

            print("Daily digest email sent successfully!")
            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def _send_whatsapp(self, message: str) -> bool:
        try:
            from twilio.rest import Client

            sid = self.whatsapp_config.get('twilio_sid')
            token = self.whatsapp_config.get('twilio_token')
            from_number = self.whatsapp_config.get('from_number')
            to_number = self.whatsapp_config.get('to_number')

            if not all([sid, token, from_number, to_number]):
                print("WhatsApp config incomplete")
                return False

            client = Client(sid, token)
            client.messages.create(
                body=message,
                from_=f"whatsapp:{from_number}",
                to_=f"whatsapp:{to_number}"
            )

            print("Daily digest WhatsApp sent successfully!")
            return True

        except ImportError:
            print("Twilio not installed: pip install twilio")
            return False
        except Exception as e:
            print(f"Failed to send WhatsApp: {e}")
            return False

    def send_interview_reminder(self, job_title: str, company: str, interview_date: str) -> bool:
        message = f"""
 interview Reminder
━━━━━━━━━━━━━━━━━━━━━━━━━
You're scheduled for an interview!

📋 Role: {job_title}
🏢 Company: {company}
📅 Date: {interview_date}

Good luck! Remember to:
• Research the company
• Review the job description
• Prepare your questions
━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return self._send_email(message) or self._send_whatsapp(message)


class ApplicationTracker:
    def __init__(self, db=None):
        self.db = db

    def get_daily_stats(self) -> Dict:
        if not self.db:
            return self._get_demo_stats()

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        applications = self.db.get_applications(limit=1000)
        today_apps = [a for a in applications if a.get('created_at', '').startswith(str(today))]

        stats = {
            'jobs_found': 15,
            'applications_sent': len(today_apps),
            'responses_received': len([a for a in applications if a.get('responded_at')]),
            'interviews_scheduled': len([a for a in applications if a.get('interview_at')]),
            'total_applied': len(applications),
            'pending': len([a for a in applications if a.get('status') == 'pending']),
            'viewed': len([a for a in applications if a.get('status') == 'viewed']),
            'interview': len([a for a in applications if a.get('status') == 'interview']),
            'offers': len([a for a in applications if a.get('status') == 'offer']),
            'rejected': len([a for a in applications if a.get('status') == 'rejected'])
        }

        return stats

    def _get_demo_stats(self) -> Dict:
        return {
            'jobs_found': 15,
            'applications_sent': 8,
            'responses_received': 2,
            'interviews_scheduled': 1,
            'total_applied': 45,
            'pending': 28,
            'viewed': 10,
            'interview': 4,
            'offers': 1,
            'rejected': 2
        }

    def track_application(self, job_data: Dict, fit_score: int) -> int:
        if not self.db:
            return 0

        job_id = self.db.insert_job(job_data)

        app_data = {
            'job_id': job_id,
            'candidate_id': 1,
            'fit_score': fit_score,
            'status': 'pending',
            'applied_at': datetime.now().isoformat()
        }

        return self.db.insert_application(app_data)

    def update_status(self, application_id: int, new_status: str):
        if not self.db:
            return

        self.db.update_application_status(application_id, new_status)

    def get_applications_by_status(self, status: str) -> List[Dict]:
        if not self.db:
            return []

        return self.db.get_applications(status=status)

    def generate_report(self) -> str:
        stats = self.get_daily_stats()

        report = f"""
╔══════════════════════════════════════════════╗
║     JOB APPLICATION TRACKING REPORT         ║
║     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}         ║
╠══════════════════════════════════════════════╣
║  TOTAL APPLICATIONS:     {stats['total_applied']:>5}              ║
║  ─────────────────────────────────────────    ║
║  Pending:                {stats['pending']:>5}              ║
║  Viewed:                 {stats['viewed']:>5}              ║
║  Interview:              {stats['interview']:>5}              ║
║  Offers:                 {stats['offers']:>5}              ║
║  Rejected:               {stats['rejected']:>5}              ║
╠══════════════════════════════════════════════╣
║  TODAY'S ACTIVITY                          ║
║  ─────────────────────────────────────────    ║
║  Jobs Found:            {stats['jobs_found']:>5}              ║
║  Applications Sent:     {stats['applications_sent']:>5}              ║
║  Responses Received:    {stats['responses_received']:>5}              ║
╚══════════════════════════════════════════════╝
"""
        return report


notifier = NotificationSystem()
tracker = ApplicationTracker()