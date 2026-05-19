import os
import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    experience: List[Dict] = field(default_factory=list)
    education: List[Dict] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)


class CVParser:
    def __init__(self, db=None):
        self.db = db

    def parse_resume_from_text(self, text: str) -> CandidateProfile:
        profile = CandidateProfile()

        profile.name = self._extract_name(text)
        profile.email = self._extract_email(text)
        profile.phone = self._extract_phone(text)
        profile.location = self._extract_location(text)
        profile.linkedin_url = self._extract_linkedin(text)
        profile.summary = self._extract_summary(text)
        profile.skills = self._extract_skills(text)
        profile.experience = self._extract_experience(text)
        profile.education = self._extract_education(text)
        profile.certifications = self._extract_certifications(text)
        profile.languages = self._extract_languages(text)

        return profile

    def parse_resume_file(self, file_path: str) -> CandidateProfile:
        text = self._read_file(file_path)
        return self.parse_resume_from_text(text)

    def _read_file(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            return self._read_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            return self._read_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _read_pdf(self, file_path: str) -> str:
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            return self._read_pdf_textract(file_path)

    def _read_pdf_textract(self, file_path: str) -> str:
        try:
            import textract
            return textract.process(file_path).decode('utf-8')
        except ImportError:
            return "[PDF reading requires PyPDF2 or textract]"

    def _read_docx(self, file_path: str) -> str:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            return "[DOCX reading requires python-docx]"

    def _extract_name(self, text: str) -> str:
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 50 and not any(c in line for c in ['@', 'http', '+1']):
                if not any(word in line.lower() for word in ['email', 'phone', 'address', 'summary']):
                    return line
        return ""

    def _extract_email(self, text: str) -> str:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        phone_patterns = [
            r'\+?1?\s?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+?[0-9]{1,4}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{2,4}'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""

    def _extract_location(self, text: str) -> str:
        location_patterns = [
            r'(?:Location|Address)[\s:]*([A-Za-z\s,]+(?:,?\s*[A-Z]{2})?)',
            r'([A-Za-z\s]+,\s*[A-Z]{2})\s*(?:\n|,|$)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_linkedin(self, text: str) -> str:
        linkedin_pattern = r'(?:linkedin\.com/in/)([a-zA-Z0-9-]+)'
        match = re.search(linkedin_pattern, text)
        if match:
            return f"https://linkedin.com/in/{match.group(1)}"
        return ""

    def _extract_summary(self, text: str) -> str:
        summary_patterns = [
            r'(?:Summary|Profile|About)[\s:]*\n?(.+?)(?:\n\n|\n[A-Z])',
            r'(?:SUMMARY|PROFILE|ABOUT)[\s:]*\n?(.+?)(?:\n\n|\n[A-Z])'
        ]
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()[:500]
                return summary
        return ""

    def _extract_skills(self, text: str) -> List[str]:
        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Rails',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'SQL',
            'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Kafka',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
            'NLP', 'Computer Vision', 'Data Science', 'Data Analysis', 'Statistics',
            'Excel', 'PowerBI', 'Tableau', 'Figma', 'Sketch', 'Adobe XD',
            'HTML', 'CSS', 'SASS', 'Tailwind', 'GraphQL', 'REST', 'API',
            'Agile', 'Scrum', 'Kanban', 'JIRA', 'Confluence',
            'Linux', 'Unix', 'Bash', 'PowerShell',
            'Security', 'CI/CD', 'DevOps', 'SRE',
            'Product Management', 'Project Management', 'Leadership',
            'Communication', 'Problem Solving', 'Teamwork'
        ]

        text_lower = text.lower()
        found_skills = []

        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return list(set(found_skills))

    def _extract_experience(self, text: str) -> List[Dict]:
        experience = []
        exp_section = self._extract_section(text, ['experience', 'employment', 'work history'])

        if not exp_section:
            return experience

        exp_pattern = r'([A-Za-z\s]+)\s*[-|–]\s*(.+?)(?:\n|$)'
        matches = re.finditer(exp_pattern, exp_section[:2000])

        for match in matches:
            company = match.group(1).strip()
            details = match.group(2).strip()

            if company and len(company) < 50:
                experience.append({
                    'company': company,
                    'title': details.split('\n')[0][:100] if details else "",
                    'description': details
                })

        return experience[:10]

    def _extract_education(self, text: str) -> List[Dict]:
        education = []
        edu_section = self._extract_section(text, ['education', 'academic'])

        if not edu_section:
            return education

        degree_patterns = [
            r'(Bachelor|Master|PhD|MBA|MS|MA|BS|BA)[^\n]*',
            r'(B\.|M\.|Ph\.D)[^\n]*'
        ]

        for pattern in degree_patterns:
            matches = re.finditer(pattern, edu_section)
            for match in matches:
                degree = match.group(0).strip()
                if len(degree) > 5 and len(degree) < 100:
                    education.append({
                        'degree': degree,
                        'institution': '',
                        'field_of_study': ''
                    })

        return education[:5]

    def _extract_section(self, text: str, keywords: List[str]) -> str:
        for keyword in keywords:
            pattern = rf'(?:{keyword})[\s:]*\n?(.+?)(?:\n(?:[A-Z][a-z]+\s+(?:experience|education|skills|employment))|\n\n|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        return ""

    def _extract_certifications(self, text: str) -> List[str]:
        cert_section = self._extract_section(text, ['certification', 'certificate'])
        if not cert_section:
            return []

        certs = []
        for line in cert_section.split('\n')[:10]:
            line = line.strip()
            if line and len(line) < 100:
                certs.append(line)
        return certs

    def _extract_languages(self, text: str) -> List[str]:
        lang_section = self._extract_section(text, ['language', 'languages'])
        if not lang_section:
            return []

        languages = []
        lang_pattern = r'([A-Za-z]+)\s*(?:fluent|native|proficient|intermediate|elementary)?'
        matches = re.finditer(lang_pattern, lang_section[:500])

        for match in matches:
            lang = match.group(1).strip()
            if len(lang) > 2 and lang.lower() not in ['the', 'and', 'for', 'with', 'experience']:
                languages.append(lang)

        return list(set(languages))[:10]

    def save_to_database(self, profile: CandidateProfile) -> int:
        if not self.db:
            return 0

        candidate_data = {
            'name': profile.name,
            'email': profile.email,
            'phone': profile.phone,
            'location': profile.location,
            'linkedin_url': profile.linkedin_url,
            'summary': profile.summary
        }

        candidate_id = self.db.insert_candidate(candidate_data)

        for skill in profile.skills:
            self.db.insert_skill(candidate_id, {'name': skill, 'category': 'technical'})

        for exp in profile.experience:
            self.db.insert_experience(candidate_id, exp)

        for edu in profile.education:
            self.db.insert_education(candidate_id, edu)

        return candidate_id


cv_parser = CVParser()