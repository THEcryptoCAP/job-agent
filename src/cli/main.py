#!/usr/bin/env python3
"""
Autonomous Job Application Agent - CLI Interface
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import ConfigManager
from src.core.database import Database
from src.cv_parser.parser import CVParser, CandidateProfile
from src.cv_parser.fit_scorer import FitScorer
from src.job_discovery.base import JobAggregator
from src.ai.generator import CoverLetterGenerator, ResumeTailor
from src.tracking.notifier import notifier, tracker, ApplicationTracker
from src.tracking.interview_prep import interview_prep


class JobAgentCLI:
    def __init__(self):
        self.config = ConfigManager().config
        self.db = Database()
        self.cv_parser = CVParser(self.db)
        self.fit_scorer = FitScorer()
        self.aggregator = JobAggregator()
        self.cover_letter_gen = CoverLetterGenerator()
        self.resume_tailor = ResumeTailor()
        self.tracker = ApplicationTracker(self.db)

    def profile(self, args):
        if args.upload:
            print(f"📄 Parsing resume: {args.upload}")
            profile = self.cv_parser.parse_resume_file(args.upload)
            candidate_id = self.cv_parser.save_to_database(profile)

            print(f"\n✅ Profile created (ID: {candidate_id})")
            print(f"\n{'='*50}")
            print("PROFILE SUMMARY")
            print(f"{'='*50}")
            print(f"Name: {profile.name}")
            print(f"Email: {profile.email}")
            print(f"Location: {profile.location}")
            print(f"LinkedIn: {profile.linkedin_url}")
            print(f"\nSkills ({len(profile.skills)}):")
            print(", ".join(profile.skills[:10]))
            print(f"\nExperience ({len(profile.experience)}):")
            for exp in profile.experience[:3]:
                print(f"  - {exp.get('title')} at {exp.get('company')}")
            print(f"\nEducation ({len(profile.education)}):")
            for edu in profile.education[:2]:
                print(f"  - {edu.get('degree')}")

        elif args.show:
            candidate = self.db.get_candidate(1)
            if candidate:
                print(f"\n{'='*50}")
                print("CANDIDATE PROFILE")
                print(f"{'='*50}")
                for key, value in candidate.items():
                    if value and key not in ['created_at', 'updated_at']:
                        print(f"{key.replace('_', ' ').title()}: {value}")

                skills = self.db.get_candidate_skills(1)
                if skills:
                    print(f"\nSkills:")
                    print(", ".join([s['name'] for s in skills[:10]]))

        else:
            print("Usage: job-agent profile --upload <resume_path>")

    def search(self, args):
        keywords = args.keywords.split(',') if args.keywords else ['software engineer']
        location = args.location or 'Remote'

        print(f"🔍 Searching for: {keywords} in {location}")

        jobs = self.aggregator.search(keywords, location, filters={
            'remote_only': args.remote_only,
            'min_salary': args.min_salary
        })

        print(f"\n✅ Found {len(jobs)} jobs\n")

        for i, job in enumerate(jobs[:args.limit], 1):
            print(f"{i}. {job['title']}")
            print(f"   🏢 {job['company']} | 📍 {job['location']}")
            print(f"   💰 ${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')}")
            if job.get('easy_apply'):
                print(f"   ✅ Easy Apply")
            print()

        return jobs

    def apply(self, args):
        keywords = args.keywords.split(',') if args.keywords else ['software engineer']
        location = args.location or 'Remote'

        print(f"🚀 Starting job search and application process...")

        jobs = self.aggregator.search(keywords, location)

        if not jobs:
            print("No jobs found!")
            return

        profile_data = {
            'name': 'Candidate',
            'email': 'candidate@example.com',
            'skills': ['Python', 'JavaScript', 'React', 'AWS'],
            'experience': [{'title': 'Software Engineer', 'company': 'Tech Corp'}],
            'location': location
        }

        print(f"\n📋 Processing {len(jobs)} jobs...\n")

        for job in jobs[:args.limit]:
            fit_result = self.fit_scorer.calculate_fit_score(profile_data, job)
            fit_score = fit_result['total_score']

            if fit_score >= self.config.scoring.min_score:
                print(f"✅ {job['title']} at {job['company']} (Fit: {fit_score}%)")

                self.tracker.track_application(job, fit_score)

                cover_letter = self.cover_letter_gen.generate(job, profile_data)
                if cover_letter.success:
                    print(f"   📝 Cover letter generated")

        print("\n🎉 Application process complete!")

    def score(self, args):
        job_id = args.job_id

        jobs = self.db.get_jobs(limit=100)
        job = next((j for j in jobs if str(j['id']) == str(job_id)), None)

        if not job:
            print(f"Job with ID {job_id} not found")
            return

        profile_data = {
            'name': 'Candidate',
            'skills': ['Python', 'JavaScript', 'React', 'AWS'],
            'experience': [{'title': 'Software Engineer', 'company': 'Tech Corp'}],
            'location': job.get('location', '')
        }

        fit_result = self.fit_scorer.calculate_fit_score(profile_data, job)

        print(f"\n{'='*50}")
        print("FIT SCORE ANALYSIS")
        print(f"{'='*50}")
        print(f"Job: {job['title']} at {job['company']}")
        print(f"\nOverall Score: {fit_result['total_score']}/100")
        print(f"Recommendation: {fit_result['recommendation'].replace('_', ' ').title()}")
        print(f"\nBreakdown:")
        for metric, score in fit_result['breakdown'].items():
            bar = '█' * int(score / 10) + '░' * (10 - int(score / 10))
            print(f"  {metric.replace('_', ' ').title():20} [{bar}] {score:.0f}%")

    def track(self, args):
        if args.stats:
            report = self.tracker.generate_report()
            print(report)

        elif args.list:
            status = args.list
            applications = self.tracker.get_applications_by_status(status)

            print(f"\n📋 Applications with status '{status}':\n")
            for app in applications[:20]:
                print(f"  • {app.get('title')} at {app.get('company')}")
                print(f"    Status: {app.get('status')} | Fit: {app.get('fit_score')}%")
                print(f"    Applied: {app.get('applied_at', 'N/A')[:10]}")
                print()

        else:
            apps = self.db.get_applications(limit=10)
            print(f"\n📊 Total Applications: {len(apps)}")

            if apps:
                print("\nRecent Applications:")
                for app in apps:
                    print(f"  • {app.get('title')} at {app.get('company')} - {app.get('status')}")

    def cover_letter(self, args):
        jobs = self.db.get_jobs(limit=10)
        if not jobs:
            jobs = self.aggregator.search(['software engineer'], 'Remote')[:1]

        if not jobs:
            print("No job found. Run 'job-agent search' first.")
            return

        job = jobs[0]
        profile = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1 555-123-4567',
            'skills': ['Python', 'JavaScript', 'React', 'AWS'],
            'experience': [
                {'title': 'Senior Software Engineer', 'company': 'Tech Corp', 'description': 'Built scalable APIs using Python and React, improving performance by 40%'}
            ]
        }

        print(f"\n📝 Generating cover letter for:")
        print(f"  Role: {job['title']}")
        print(f"  Company: {job['company']}\n")

        result = self.cover_letter_gen.generate(job, profile)

        if result.success:
            print("-" * 50)
            print(result.content)
            print("-" * 50)
        else:
            print(f"❌ Error: {result.error}")

    def interview(self, args):
        jobs = self.db.get_jobs(limit=1)
        if not jobs:
            jobs = self.aggregator.search(['software engineer'], 'Remote')[:1]

        if not jobs:
            print("No job found. Run 'job-agent search' first.")
            return

        job = jobs[0]

        print(f"\n🎤 Generating interview questions for:")
        print(f"  Role: {job['title']}")
        print(f"  Company: {job['company']}\n")

        questions = interview_prep.generate_questions(job.get('description', ''), job.get('title', ''))

        print(f"Generated {len(questions)} questions:\n")

        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q.type.upper()}] {q.category}")
            print(f"   {q.question}")
            print(f"   Difficulty: {q.difficulty}")
            print(f"   Listen for: {q.what_to_listen_for[:80]}...")
            print()

    def notify(self, args):
        stats = self.tracker.get_daily_stats()
        result = notifier.send_daily_digest(stats)
        print(f"✅ Daily digest sent!" if result else "❌ Failed to send digest")

    def run(self):
        parser = argparse.ArgumentParser(
            description='🤖 Autonomous Job Application Agent',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  job-agent profile --upload resume.pdf     Parse and save resume
  job-agent search "python,react" --remote  Search for remote jobs
  job-agent apply "software engineer"        Search and apply to jobs
  job-agent track --stats                   Show application stats
  job-agent cover-letter                    Generate cover letter
  job-agent interview                       Generate interview prep
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        profile_parser = subparsers.add_parser('profile', help='Manage candidate profile')
        profile_parser.add_argument('--upload', help='Upload and parse resume')
        profile_parser.add_argument('--show', action='store_true', help='Show profile')

        search_parser = subparsers.add_parser('search', help='Search for jobs')
        search_parser.add_argument('--keywords', '-k', default='software engineer', help='Job keywords')
        search_parser.add_argument('--location', '-l', default='Remote', help='Job location')
        search_parser.add_argument('--remote-only', '-r', action='store_true', help='Remote jobs only')
        search_parser.add_argument('--min-salary', type=int, help='Minimum salary')
        search_parser.add_argument('--limit', '-n', type=int, default=5, help='Number of results')

        apply_parser = subparsers.add_parser('apply', help='Apply to jobs')
        apply_parser.add_argument('--keywords', '-k', default='software engineer', help='Job keywords')
        apply_parser.add_argument('--location', '-l', default='Remote', help='Job location')
        apply_parser.add_argument('--limit', '-n', type=int, default=3, help='Max applications')

        score_parser = subparsers.add_parser('score', help='Calculate job fit score')
        score_parser.add_argument('--job-id', required=True, help='Job ID')

        track_parser = subparsers.add_parser('track', help='Track applications')
        track_parser.add_argument('--stats', action='store_true', help='Show statistics')
        track_parser.add_argument('--list', metavar='STATUS', help='List by status')

        cover_parser = subparsers.add_parser('cover-letter', help='Generate cover letter')
        cover_parser.add_argument('--job-id', help='Job ID')

        interview_parser = subparsers.add_parser('interview', help='Interview preparation')
        interview_parser.add_argument('--job-id', help='Job ID')

        notify_parser = subparsers.add_parser('notify', help='Send daily digest')
        notify_parser.add_argument('--test', action='store_true', help='Test notification')

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        command_map = {
            'profile': self.profile,
            'search': self.search,
            'apply': self.apply,
            'score': self.score,
            'track': self.track,
            'cover-letter': self.cover_letter,
            'interview': self.interview,
            'notify': self.notify
        }

        if args.command in command_map:
            command_map[args.command](args)
        else:
            print(f"Unknown command: {args.command}")


def main():
    cli = JobAgentCLI()
    cli.run()


if __name__ == '__main__':
    main()