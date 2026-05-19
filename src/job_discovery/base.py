from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class Job:
    external_id: str
    source: str
    title: str
    company: str
    location: str
    description: str
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    posted_date: Optional[str] = None
    application_url: Optional[str] = None
    easy_apply: bool = False
    applicant_count: Optional[int] = None
    company_url: Optional[str] = None
    company_logo: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'external_id': self.external_id,
            'source': self.source,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'employment_type': self.employment_type,
            'seniority_level': self.seniority_level,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'posted_date': self.posted_date,
            'application_url': self.application_url,
            'easy_apply': self.easy_apply,
            'applicant_count': self.applicant_count,
            'company_url': self.company_url,
            'company_logo': self.company_logo
        }


class JobSource(ABC):
    @abstractmethod
    def search_jobs(self, keywords: List[str], location: str = "", **kwargs) -> List[Job]:
        pass

    @abstractmethod
    def get_job_details(self, job_url: str) -> Job:
        pass


class LinkedInScraper(JobSource):
    def __init__(self):
        self.source_name = "linkedin"

    def search_jobs(self, keywords: List[str], location: str = "", **kwargs) -> List[Job]:
        jobs = []

        easy_apply_only = kwargs.get('easy_apply_only', True)

        sample_jobs = [
            {
                'id': 'linkedin-1234567890',
                'title': 'Senior Software Engineer',
                'company': 'Google',
                'location': location or 'Remote',
                'description': 'We are looking for a Senior Software Engineer to join our team. '
                               'Responsibilities include designing and implementing scalable systems, '
                               'mentoring junior engineers, and collaborating with cross-functional teams. '
                               'Requirements: 5+ years of experience, proficiency in Python/Java, '
                               'experience with cloud services (AWS/GCP), strong problem-solving skills.',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'salary_min': 150000,
                'salary_max': 200000,
                'salary_currency': 'USD',
                'posted_date': '2 days ago',
                'application_url': 'https://www.linkedin.com/jobs/view/1234567890',
                'easy_apply': True,
                'applicant_count': 45
            },
            {
                'id': 'linkedin-1234567891',
                'title': 'Frontend Developer',
                'company': 'Stripe',
                'location': location or 'San Francisco, CA',
                'description': 'Join our team as a Frontend Developer. You will build beautiful, '
                               'performant web applications using React, TypeScript, and modern CSS. '
                               'Experience with React, TypeScript, and CSS required.',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid-Senior',
                'salary_min': 120000,
                'salary_max': 160000,
                'salary_currency': 'USD',
                'posted_date': '5 days ago',
                'application_url': 'https://www.linkedin.com/jobs/view/1234567891',
                'easy_apply': True,
                'applicant_count': 32
            },
            {
                'id': 'linkedin-1234567892',
                'title': 'Product Manager',
                'company': 'Notion',
                'location': location or 'Remote',
                'description': 'We are seeking a Product Manager to lead our product strategy. '
                               'Define roadmap, work with engineering, and drive product vision.',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid-Level',
                'salary_min': 130000,
                'salary_max': 170000,
                'salary_currency': 'USD',
                'posted_date': '1 week ago',
                'application_url': 'https://www.linkedin.com/jobs/view/1234567892',
                'easy_apply': True,
                'applicant_count': 78
            }
        ]

        for job_data in sample_jobs:
            for keyword in keywords:
                if keyword.lower() in job_data['title'].lower() or keyword.lower() in job_data['description'].lower():
                    job = Job(
                        external_id=job_data['id'],
                        source=self.source_name,
                        title=job_data['title'],
                        company=job_data['company'],
                        location=job_data['location'],
                        description=job_data['description'],
                        employment_type=job_data.get('employment_type'),
                        seniority_level=job_data.get('seniority_level'),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        salary_currency=job_data.get('salary_currency'),
                        posted_date=job_data.get('posted_date'),
                        application_url=job_data.get('application_url'),
                        easy_apply=job_data.get('easy_apply', False),
                        applicant_count=job_data.get('applicant_count')
                    )
                    jobs.append(job)
                    break

        return jobs

    def get_job_details(self, job_url: str) -> Job:
        job_id = job_url.split('/')[-1]
        return Job(
            external_id=job_id,
            source=self.source_name,
            title="Software Engineer",
            company="Sample Company",
            location="Remote",
            description="Full job description here...",
            easy_apply=True
        )


class IndeedScraper(JobSource):
    def __init__(self):
        self.source_name = "indeed"

    def search_jobs(self, keywords: List[str], location: str = "", **kwargs) -> List[Job]:
        jobs = []

        sample_jobs = [
            {
                'id': 'indeed-1234567890',
                'title': 'Software Developer',
                'company': 'Amazon',
                'location': location or 'Seattle, WA',
                'description': 'Software Developer position at Amazon. Work on cutting-edge technology, '
                               'solve complex problems, and collaborate with talented teams.',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid-Level',
                'salary_min': 130000,
                'salary_max': 180000,
                'salary_currency': 'USD',
                'posted_date': '3 days ago',
                'application_url': 'https://www.indeed.com/viewjob?jk=1234567890',
                'easy_apply': True,
                'applicant_count': 120
            },
            {
                'id': 'indeed-1234567891',
                'title': 'Data Analyst',
                'company': 'Netflix',
                'location': location or 'Los Angeles, CA',
                'description': 'Join Netflix as a Data Analyst. Analyze user data, create dashboards, '
                               'and drive business decisions with insights.',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid-Level',
                'salary_min': 110000,
                'salary_max': 140000,
                'salary_currency': 'USD',
                'posted_date': '1 week ago',
                'application_url': 'https://www.indeed.com/viewjob?jk=1234567891',
                'easy_apply': True,
                'applicant_count': 85
            }
        ]

        for job_data in sample_jobs:
            for keyword in keywords:
                if keyword.lower() in job_data['title'].lower() or keyword.lower() in job_data['description'].lower():
                    job = Job(
                        external_id=job_data['id'],
                        source=self.source_name,
                        title=job_data['title'],
                        company=job_data['company'],
                        location=job_data['location'],
                        description=job_data['description'],
                        employment_type=job_data.get('employment_type'),
                        seniority_level=job_data.get('seniority_level'),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        salary_currency=job_data.get('salary_currency'),
                        posted_date=job_data.get('posted_date'),
                        application_url=job_data.get('application_url'),
                        easy_apply=job_data.get('easy_apply', False),
                        applicant_count=job_data.get('applicant_count')
                    )
                    jobs.append(job)
                    break

        return jobs

    def get_job_details(self, job_url: str) -> Job:
        return Job(
            external_id="indeed-details",
            source=self.source_name,
            title="Job Details",
            company="Company",
            location="Location",
            description="Full description"
        )


class WellfoundScraper(JobSource):
    def __init__(self):
        self.source_name = "wellfound"

    def search_jobs(self, keywords: List[str], location: str = "", **kwargs) -> List[Job]:
        jobs = []

        sample_jobs = [
            {
                'id': 'wellfound-1234567890',
                'title': 'Full Stack Engineer',
                'company': 'Linear',
                'location': location or 'Remote',
                'description': 'Linear is building the issue tracking tool for modern software teams. '
                               'Looking for a Full Stack Engineer to help build our web application. '
                               'Tech stack: React, Node.js, PostgreSQL.',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid-Senior',
                'salary_min': 140000,
                'salary_max': 180000,
                'salary_currency': 'USD',
                'posted_date': '2 days ago',
                'application_url': 'https://wellfound.com/jobs/1234567890',
                'easy_apply': True,
                'applicant_count': 156
            },
            {
                'id': 'wellfound-1234567891',
                'title': 'Backend Engineer',
                'company': 'Vercel',
                'location': location or 'Remote',
                'description': 'Vercel is looking for a Backend Engineer to work on our infrastructure. '
                               'Experience with Go, Kubernetes, and distributed systems preferred.',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'salary_min': 160000,
                'salary_max': 220000,
                'salary_currency': 'USD',
                'posted_date': '5 days ago',
                'application_url': 'https://wellfound.com/jobs/1234567891',
                'easy_apply': True,
                'applicant_count': 89
            },
            {
                'id': 'wellfound-1234567892',
                'title': 'DevOps Engineer',
                'company': 'Railway',
                'location': location or 'Remote',
                'description': 'Help build the infrastructure platform for developers. '
                               'Experience with Docker, Kubernetes, and AWS required.',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid-Level',
                'salary_min': 120000,
                'salary_max': 150000,
                'salary_currency': 'USD',
                'posted_date': '1 week ago',
                'application_url': 'https://wellfound.com/jobs/1234567892',
                'easy_apply': True,
                'applicant_count': 45
            }
        ]

        for job_data in sample_jobs:
            for keyword in keywords:
                if keyword.lower() in job_data['title'].lower() or keyword.lower() in job_data['description'].lower():
                    job = Job(
                        external_id=job_data['id'],
                        source=self.source_name,
                        title=job_data['title'],
                        company=job_data['company'],
                        location=job_data['location'],
                        description=job_data['description'],
                        employment_type=job_data.get('employment_type'),
                        seniority_level=job_data.get('seniority_level'),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        salary_currency=job_data.get('salary_currency'),
                        posted_date=job_data.get('posted_date'),
                        application_url=job_data.get('application_url'),
                        easy_apply=job_data.get('easy_apply', False),
                        applicant_count=job_data.get('applicant_count')
                    )
                    jobs.append(job)
                    break

        return jobs

    def get_job_details(self, job_url: str) -> Job:
        return Job(
            external_id="wellfound-details",
            source=self.source_name,
            title="Job Details",
            company="Company",
            location="Remote",
            description="Full description"
        )


class JobAggregator:
    def __init__(self, sources: Optional[List[str]] = None):
        self.sources = sources or ['linkedin', 'indeed', 'wellfound']
        self.scrapers = {}

        if 'linkedin' in self.sources:
            self.scrapers['linkedin'] = LinkedInScraper()
        if 'indeed' in self.sources:
            self.scrapers['indeed'] = IndeedScraper()
        if 'wellfound' in self.sources:
            self.scrapers['wellfound'] = WellfoundScraper()

    def search(self, keywords: List[str], location: str = "", filters: Optional[Dict] = None) -> List[Dict]:
        all_jobs = []

        for source, scraper in self.scrapers.items():
            try:
                jobs = scraper.search_jobs(keywords, location)
                for job in jobs:
                    job_dict = job.to_dict()

                    if filters:
                        if filters.get('min_salary') and job.salary_min and job.salary_min < filters['min_salary']:
                            continue
                        if filters.get('max_salary') and job.salary_max and job.salary_max > filters['max_salary']:
                            continue
                        if filters.get('remote_only') and 'remote' not in job.location.lower():
                            continue

                    all_jobs.append(job_dict)
            except Exception as e:
                print(f"Error fetching from {source}: {e}")

        return all_jobs

    def get_details(self, source: str, job_url: str) -> Optional[Dict]:
        if source in self.scrapers:
            try:
                job = self.scrapers[source].get_job_details(job_url)
                return job.to_dict()
            except Exception as e:
                print(f"Error getting job details from {source}: {e}")
        return None


aggregator = JobAggregator()