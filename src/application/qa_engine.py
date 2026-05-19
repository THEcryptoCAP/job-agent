import re
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class QuestionAnswer:
    question: str
    answer: str
    category: str
    confidence: float = 1.0


class QAEngine:
    def __init__(self, db=None):
        self.db = db

        self.default_answers = {
            'work_authorization': {
                'authorized': 'Yes, I am authorized to work in the US',
                'sponsor': 'Yes, I will require sponsorship',
                'both': 'I am authorized to work and will require sponsorship'
            },
            'visa_status': {
                'citizen': 'I am a US citizen',
                'green_card': 'I am a permanent resident (green card holder)',
                'h1b': 'I am currently on H1B visa',
                'opt': 'I am on OPT'
            },
            'remote_work': {
                'yes': 'Yes, I am open to remote work',
                'no': 'I prefer to work on-site',
                'hybrid': 'I am open to hybrid work arrangements'
            },
            'relocation': {
                'yes': 'Yes, I am willing to relocate',
                'no': 'I prefer to work remotely'
            },
            'experience_years': {
                '1': '1 year',
                '2': '2 years',
                '3': '3 years',
                '5': '5 years',
                '7': '7+ years',
                '10': '10+ years'
            },
            'salary_expectation': {
                'low': '$80,000 - $100,000',
                'mid': '$100,000 - $130,000',
                'high': '$130,000 - $160,000',
                'very_high': '$160,000+'
            },
            'notice_period': {
                'immediate': 'I can start immediately',
                '2weeks': '2 weeks notice',
                '1month': '1 month notice',
                '2months': '2 months notice'
            },
            'education': {
                'bachelors': "Bachelor's degree",
                'masters': "Master's degree",
                'phd': 'PhD',
                'bootcamp': 'Coding bootcamp'
            }
        }

        self.question_patterns = {
            'authorization': [
                r'authorized.*work',
                r'work.*authorization',
                r'legally.*eligible',
                r'can.*work'
            ],
            'visa': [
                r'visa.*status',
                r'immigration.*status',
                r'sponsorship.*need',
                r'require.*sponsorship'
            ],
            'remote': [
                r'remote.*work',
                r'work.*from.*home',
                r'telecommute',
                r'hybrid'
            ],
            'relocation': [
                r'relocat',
                r'move.*to',
                r'location.*flexible'
            ],
            'experience': [
                r'years.*experience',
                r'experience.*level',
                r'how.*long.*worked'
            ],
            'salary': [
                r'salary.*expect',
                r'compensation',
                r'expected.*pay',
                r'pay.*range'
            ],
            'notice': [
                r'notice.*period',
                r'can.*start',
                r'available.*date'
            ],
            'education': [
                r'education.*level',
                r'degree',
                r'qualification'
            ],
            'tools': [
                r'tools.*used',
                r'technology.*stack',
                r'programming.*language'
            ],
            'availability': [
                r'availability',
                r'when.*can.*start',
                r'start.*date'
            ]
        }

    def get_answer(self, question: str, source: str = 'general', context: Optional[Dict] = None) -> Optional[str]:
        question_lower = question.lower()

        if self.db:
            saved_answer = self.db.get_screening_answer(question, source)
            if saved_answer:
                self._increment_usage(question, source)
                return saved_answer

        answer = self._match_question(question_lower, context)

        if answer and self.db:
            self.db.insert_screening_qa({
                'source': source,
                'question_text': question,
                'answer_text': answer
            })

        return answer

    def _match_question(self, question: str, context: Optional[Dict]) -> Optional[str]:
        for category, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question):
                    return self._get_category_answer(category, context)

        if context and context.get('profile'):
            return self._generate_contextual_answer(question, context)

        return self._get_default_fallback(question)

    def _get_category_answer(self, category: str, context: Optional[Dict]) -> str:
        if category in self.default_answers:
            category_answers = self.default_answers[category]
            return list(category_answers.values())[0]
        return ""

    def _generate_contextual_answer(self, question: str, context: Dict) -> str:
        profile = context.get('profile', {})

        if 'experience' in question.lower() and profile.get('experience'):
            years = len(profile.get('experience', []))
            return f"I have approximately {years} years of experience in my field."

        if 'salary' in question.lower():
            return "I am flexible and open to discussing compensation based on the role and market rates."

        if 'remote' in question.lower():
            return "Yes, I am open to remote work arrangements."

        return None

    def _get_default_fallback(self, question: str) -> str:
        fallbacks = [
            "Yes",
            "No",
            "I am flexible on this matter",
            "I am open to discussing this further",
            "Please refer to my resume for details"
        ]

        if any(word in question.lower() for word in ['are', 'can', 'will', 'do']):
            return "Yes"

        return random.choice(fallbacks) if 'random' in dir() else "I am flexible on this matter"

    def _increment_usage(self, question: str, source: str):
        pass

    def add_custom_answer(self, question_pattern: str, answer: str):
        self.default_answers.setdefault('custom', {})[question_pattern] = answer

    def get_answers_for_job(self, questions: List[str], profile_data: Dict,
                           source: str = 'linkedin') -> Dict[str, str]:
        answers = {}
        context = {'profile': profile_data}

        for question in questions:
            answer = self.get_answer(question, source, context)
            if answer:
                answers[question] = answer

        return answers


import random
qa_engine = QAEngine()