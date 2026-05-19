import os
import json
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class GeneratedDocument:
    content: str
    format: str
    success: bool
    error: Optional[str] = None


class CoverLetterGenerator:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.style = self.config.get('style', 'modern')
        self.max_words = self.config.get('max_words', 350)

    def generate(self, job: Dict, profile: Dict) -> GeneratedDocument:
        try:
            content = self._generate_content(job, profile)

            return GeneratedDocument(
                content=content,
                format='text',
                success=True
            )
        except Exception as e:
            return GeneratedDocument(
                content="",
                format='text',
                success=False,
                error=str(e)
            )

    def _generate_content(self, job: Dict, profile: Dict) -> str:
        job_title = job.get('title', 'the position')
        company = job.get('company', 'your company')
        location = job.get('location', '')

        name = profile.get('name', '')
        experience = profile.get('experience', [])
        skills = profile.get('skills', [])

        key_skill = skills[0] if skills else 'software development'
        latest_role = experience[0].get('title', 'Software Engineer') if experience else 'Software Engineer'
        latest_company = experience[0].get('company', '') if experience else ''

        hook = self._generate_hook(job, profile)
        body = self._generate_body(job, profile)
        closing = self._generate_closing(profile, job.get('company', 'your company'))

        letter = f"{hook}\n\n{body}\n\n{closing}"

        return letter

    def _generate_hook(self, job: Dict, profile: Dict) -> str:
        company = job.get('company', 'your company')
        title = job.get('title', 'role')

        if profile.get('experience'):
            exp = profile['experience'][0]
            achievement = self._extract_achievement(exp.get('description', ''))
            if achievement:
                return f"Last year I {achievement} — exactly the challenge your team is solving for {title} at {company}."

        return f"I am writing to express my strong interest in the {title} position at {company}."

    def _generate_body(self, job: Dict, profile: Dict) -> str:
        job_desc = job.get('description', '')
        skills = profile.get('skills', [])
        experience = profile.get('experience', [])

        relevant_skills = self._extract_relevant_skills(job_desc, skills)
        relevant_exp = self._extract_relevant_experience(job_desc, experience)

        paragraphs = []

        if relevant_skills:
            skills_text = ', '.join(relevant_skills[:4])
            paragraphs.append(
                f"With my background in {skills_text}, I am confident I can contribute meaningfully to your team."
            )

        if relevant_exp:
            exp = relevant_exp[0]
            paragraphs.append(
                f"In my current role at {exp.get('company', 'my current employer')}, I have developed strong skills "
                f"in {exp.get('title', 'the field')} that directly align with this position's requirements."
            )

        if job.get('seniority_level'):
            level = job['seniority_level']
            paragraphs.append(
                f"I am particularly excited about this opportunity as it aligns perfectly with my experience level "
                f"and career trajectory in the {level} space."
            )

        return '\n\n'.join(paragraphs)

    def _generate_closing(self, profile: Dict, company: str = "your company") -> str:
        name = profile.get('name', '')
        email = profile.get('email', '')
        phone = profile.get('phone', '')

        return (
            f"Thank you for considering my application. I would welcome the opportunity to discuss how "
            f"my skills and experience can contribute to {company}'s goals. "
            f"I look forward to hearing from you.\n\n"
            f"Best regards,\n{name}"
        )

    def _extract_achievement(self, description: str) -> Optional[str]:
        if not description:
            return None

        achievements = [
            r'increased[^\.]+by\s+(\d+%)',
            r'reduced[^\.]+by\s+(\d+%)',
            r'improved[^\.]+by\s+(\d+%)',
            r'delivered[^\.]+(?:result|project)',
            r'led[^\.]+(?:team|project)',
            r'saved[^\.]+(?:time|cost|money)'
        ]

        for pattern in achievements:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(0)[:80]

        return None

    def _extract_relevant_skills(self, job_desc: str, candidate_skills: List[str]) -> List[str]:
        if not job_desc or not candidate_skills:
            return []

        job_lower = job_desc.lower()
        relevant = []

        for skill in candidate_skills:
            if skill.lower() in job_lower:
                relevant.append(skill)

        return relevant

    def _extract_relevant_experience(self, job_desc: str, experience: List[Dict]) -> List[Dict]:
        if not job_desc or not experience:
            return []

        job_keywords = set(re.findall(r'\b\w+\b', job_desc.lower()))
        relevant = []

        for exp in experience:
            exp_text = (exp.get('title', '') + ' ' + exp.get('description', '')).lower()
            exp_keywords = set(re.findall(r'\b\w+\b', exp_text))

            overlap = len(job_keywords & exp_keywords)
            if overlap >= 3:
                relevant.append(exp)

        return relevant[:2]


class ResumeTailor:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def tailor(self, base_resume: str, job: Dict) -> GeneratedDocument:
        try:
            tailored = self._tailor_content(base_resume, job)

            return GeneratedDocument(
                content=tailored,
                format='text',
                success=True
            )
        except Exception as e:
            return GeneratedDocument(
                content=base_resume,
                format='text',
                success=False,
                error=str(e)
            )

    def _tailor_content(self, base_resume: str, job: Dict) -> str:
        job_desc = job.get('description', '')
        job_title = job.get('title', '')

        keywords = self._extract_keywords(job_desc)

        lines = base_resume.split('\n')
        tailored_lines = []

        for line in lines:
            if any(kw.lower() in line.lower() for kw in keywords[:10]):
                tailored_lines.append(line)
            elif not any(kw in line.lower() for kw in ['summary', 'skills', 'experience']):
                tailored_lines.append(line)

        return '\n'.join(tailored_lines)

    def _extract_keywords(self, job_desc: str) -> List[str]:
        common_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'aws', 'docker',
            'kubernetes', 'sql', 'agile', 'scrum', 'machine learning', 'data',
            'design', 'product', 'marketing', 'sales', 'analytics'
        ]

        found = []
        job_lower = job_desc.lower()

        for kw in common_keywords:
            if kw in job_lower:
                found.append(kw)

        return found


import re
cover_letter_generator = CoverLetterGenerator()
resume_tailor = ResumeTailor()