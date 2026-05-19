import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InterviewQuestion:
    question: str
    type: str
    category: str
    difficulty: str
    what_to_listen_for: str
    red_flags: List[str]
    sample_answer: Optional[str] = None


class InterviewPrepGenerator:
    def __init__(self):
        self.behavioral_questions = [
            ("Tell me about a time you had to manage a difficult stakeholder.", "behavioral", "Communication", "mid"),
            ("Describe a project where you had to learn a new technology quickly.", "behavioral", "Learning", "mid"),
            ("Tell me about a time you failed and how you handled it.", "behavioral", "Resilience", "mid"),
            ("Describe a situation where you had to work with a difficult team member.", "behavioral", "Teamwork", "mid"),
            ("Tell me about a time you had to meet a tight deadline.", "behavioral", "Time Management", "mid"),
        ]

        self.technical_questions = {
            'software': [
                ("Explain the difference between REST and GraphQL.", "technical", "API Design", "mid"),
                ("Describe how you would design a scalable system.", "technical", "System Design", "senior"),
                ("What's your approach to debugging a production issue?", "technical", "Debugging", "mid"),
            ],
            'data': [
                ("Explain the difference between supervised and unsupervised learning.", "technical", "ML Concepts", "mid"),
                ("How would you handle missing data in a dataset?", "technical", "Data Processing", "mid"),
                ("Describe your experience with SQL optimization.", "technical", "SQL", "mid"),
            ],
            'product': [
                ("How do you prioritize features in a product roadmap?", "technical", "Strategy", "senior"),
                ("Describe your process for conducting user research.", "technical", "Research", "mid"),
                ("How do you measure product success?", "technical", "Metrics", "mid"),
            ],
            'default': [
                ("Walk me through your portfolio/project.", "technical", "Portfolio", "mid"),
                ("What tools and technologies are you most proficient in?", "technical", "Skills", "junior"),
            ]
        }

    def generate_questions(self, job_description: str, job_title: str = "") -> List[InterviewQuestion]:
        questions = []

        job_lower = job_description.lower()

        questions.extend(self._generate_behavioral_questions(5))

        role_category = self._detect_role_category(job_title, job_description)
        if role_category in self.technical_questions:
            tech_questions = self.technical_questions[role_category][:4]
        else:
            tech_questions = self.technical_questions['default'][:4]

        for q_text, q_type, q_cat, difficulty in tech_questions:
            questions.append(InterviewQuestion(
                question=q_text,
                type=q_type,
                category=q_cat,
                difficulty=difficulty,
                what_to_listen_for=self._get_listening_points(q_cat),
                red_flags=self._get_red_flags(q_cat),
                sample_answer=self._generate_sample_answer(q_text, q_cat)
            ))

        if any(word in job_lower for word in ['lead', 'manage', 'team']):
            questions.extend(self._generate_leadership_questions(3))

        if any(word in job_lower for word in ['problem', 'challenge', 'issue']):
            questions.extend(self._generate_problem_solving_questions(2))

        return questions

    def _generate_behavioral_questions(self, count: int) -> List[InterviewQuestion]:
        selected = []
        for i in range(min(count, len(self.behavioral_questions))):
            q = self.behavioral_questions[i]
            selected.append(InterviewQuestion(
                question=q[0],
                type='behavioral',
                category=q[2],
                difficulty=q[3],
                what_to_listen_for=self._get_listening_points(q[2]),
                red_flags=self._get_red_flags(q[2])
            ))
        return selected

    def _generate_leadership_questions(self, count: int) -> List[InterviewQuestion]:
        questions = [
            ("Tell me about a time you had to manage a team through a difficult period.", "behavioral", "Leadership", "senior"),
            ("How do you handle conflict within your team?", "behavioral", "Conflict Resolution", "mid"),
            ("Describe how you've mentored junior team members.", "behavioral", "Mentorship", "mid"),
        ]
        return [InterviewQuestion(
            question=q[0], type=q[1], category=q[2], difficulty=q[3],
            what_to_listen_for=self._get_listening_points(q[2]),
            red_flags=self._get_red_flags(q[2])
        ) for q in questions[:count]]

    def _generate_problem_solving_questions(self, count: int) -> List[InterviewQuestion]:
        questions = [
            ("Walk me through how you approach debugging a complex problem.", "situational", "Problem Solving", "mid"),
            ("Describe a technical challenge you faced and how you solved it.", "behavioral", "Problem Solving", "mid"),
        ]
        return [InterviewQuestion(
            question=q[0], type=q[1], category=q[2], difficulty=q[3],
            what_to_listen_for=self._get_listening_points(q[2]),
            red_flags=self._get_red_flags(q[2])
        ) for q in questions[:count]]

    def _detect_role_category(self, job_title: str, job_description: str) -> str:
        text = (job_title + ' ' + job_description).lower()

        if any(word in text for word in ['software', 'developer', 'engineer', 'code', 'programming']):
            return 'software'
        elif any(word in text for word in ['data', 'analyst', 'scientist', 'ml', 'machine learning']):
            return 'data'
        elif any(word in text for word in ['product', 'manager', 'roadmap']):
            return 'product'

        return 'default'

    def _get_listening_points(self, category: str) -> str:
        points = {
            'Communication': 'Look for specific examples, clarity in describing situations, and measurable outcomes.',
            'Learning': 'Focus on the learning process, not just the outcome. Did they seek resources? Ask questions?',
            'Resilience': 'Watch for accountability - do they own their mistakes? What did they learn?',
            'Teamwork': 'Notice how they describe others\' contributions. Do they take credit or share credit?',
            'Time Management': 'Look for prioritization strategies and trade-offs they made.',
            'Leadership': 'Focus on impact - how did their leadership affect the team or project?',
            'Conflict Resolution': 'Note if they sought understanding vs. just winning the argument.',
            'Mentorship': 'Look for specific examples of how they helped others grow.',
            'Problem Solving': 'Follow the logic - do they show systematic thinking?',
            'API Design': 'Check if they understand trade-offs between approaches.',
            'System Design': 'Look for scalability considerations and clean architecture.',
            'Debugging': 'Notice their systematic approach vs. random guessing.',
            'ML Concepts': 'Verify foundational understanding before getting into advanced topics.',
            'Data Processing': 'Check for awareness of downstream impact of data quality.',
            'SQL': 'Look for specific optimization techniques mentioned.',
            'Strategy': 'Look for data-driven decision making and customer focus.',
            'Research': 'Check for methodological rigor in their approach.',
            'Metrics': 'Notice if they mention both leading and lagging indicators.',
            'Portfolio': 'Focus on impact and lessons learned, not just technical details.',
            'Skills': 'Listen for depth vs. breadth - can they go deep on anything?'
        }
        return points.get(category, 'Look for specific examples and concrete outcomes.')

    def _get_red_flags(self, category: str) -> List[str]:
        flags = {
            'Communication': [
                'Vague or generic answers without specifics',
                'Blaming others for failures',
                'Inability to describe their own contributions clearly'
            ],
            'Learning': [
                'Claiming to have learned something instantly without process',
                'Not being able to explain what they learned'
            ],
            'Resilience': [
                'Blaming others or external factors',
                'Not taking ownership of mistakes',
                'Not being able to explain what they would do differently'
            ],
            'Teamwork': [
                'Only speaking negatively about colleagues',
                'Not acknowledging others\' contributions',
                'Creating conflicts rather than resolving them'
            ],
            'Time Management': [
                'No prioritization strategy mentioned',
                'Working overtime as the only solution',
                'Not knowing when to say no'
            ],
            'Leadership': [
                'Micromanaging instead of empowering',
                'Taking all credit for team success',
                'Not developing others'
            ]
        }
        return flags.get(category, ['Generic answers', 'No specific examples'])

    def _generate_sample_answer(self, question: str, category: str) -> Optional[str]:
        if 'STAR' in question.upper() or 'behavioral' in category.lower():
            return (
                "STAR Method Example:\n"
                "S - Situation: [Describe the context]\n"
                "T - Task: [Explain what you needed to accomplish]\n"
                "A - Action: [Detail what you did specifically]\n"
                "R - Result: [Share the outcome with metrics if possible]"
            )
        return None

    def generate_scorecard(self, questions: List[InterviewQuestion]) -> Dict:
        scorecard = {
            'categories': {},
            'total_questions': len(questions),
            'scoring_guide': {}
        }

        for q in questions:
            if q.category not in scorecard['categories']:
                scorecard['categories'][q.category] = []
            scorecard['categories'][q.category].append(q.difficulty)

            if q.difficulty not in scorecard['scoring_guide']:
                scorecard['scoring_guide'][q.difficulty] = {
                    '1-2': 'Does not meet requirements',
                    '3': 'Partially meets requirements',
                    '4': 'Meets requirements',
                    '5': 'Exceeds requirements'
                }

        return scorecard


interview_prep = InterviewPrepGenerator()