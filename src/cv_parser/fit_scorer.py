import re
from typing import Dict, List, Optional


class FitScorer:
    def __init__(self, weights: Optional[Dict] = None):
        self.weights = weights or {
            'title_match': 25,
            'skills_match': 30,
            'location_match': 15,
            'salary_match': 15,
            'experience_match': 15
        }

    def calculate_fit_score(self, candidate_profile: Dict, job: Dict) -> Dict:
        scores = {}

        title_score = self._calculate_title_score(
            candidate_profile.get('skills', []),
            candidate_profile.get('experience', []),
            job.get('title', '')
        )
        scores['title_match'] = title_score

        skills_score = self._calculate_skills_score(
            candidate_profile.get('skills', []),
            job.get('description', '')
        )
        scores['skills_match'] = skills_score

        location_score = self._calculate_location_score(
            candidate_profile.get('location', ''),
            job.get('location', '')
        )
        scores['location_match'] = location_score

        salary_score = self._calculate_salary_score(
            job.get('salary_min'),
            job.get('salary_max'),
            candidate_profile.get('expected_salary')
        )
        scores['salary_match'] = salary_score

        experience_score = self._calculate_experience_score(
            candidate_profile.get('experience', []),
            job.get('seniority_level'),
            job.get('description', '')
        )
        scores['experience_match'] = experience_score

        total_score = sum(
            scores[key] * (self.weights.get(key, 0) / 100)
            for key in scores
        )

        return {
            'total_score': round(total_score, 1),
            'breakdown': scores,
            'recommendation': self._get_recommendation(total_score)
        }

    def _calculate_title_score(self, skills: List[str], experience: List[Dict], job_title: str) -> float:
        if not job_title:
            return 50

        job_title_lower = job_title.lower()

        title_keywords = {
            'senior': ['senior', 'sr.', 'lead', 'principal', 'staff', 'manager'],
            'mid': ['engineer', 'developer', 'analyst', 'specialist', 'consultant'],
            'junior': ['junior', 'jr.', 'entry', 'intern', 'associate', 'trainee']
        }

        level_score = 50

        for level, keywords in title_keywords.items():
            if any(kw in job_title_lower for kw in keywords):
                level_score = 80 if level == 'senior' else 60 if level == 'mid' else 40
                break

        role_score = 50

        role_keywords = ['software', 'frontend', 'backend', 'fullstack', 'devops', 'data',
                         'product', 'design', 'marketing', 'sales']

        for skill in skills:
            if any(rk in skill.lower() for rk in role_keywords):
                if any(rk in job_title_lower for rk in role_keywords):
                    role_score = 90
                    break

        return (level_score * 0.3 + role_score * 0.7)

    def _calculate_skills_score(self, candidate_skills: List[str], job_description: str) -> float:
        if not job_description or not candidate_skills:
            return 30

        job_desc_lower = job_description.lower()

        matched_skills = 0
        for skill in candidate_skills:
            skill_lower = skill.lower()
            if skill_lower in job_desc_lower:
                matched_skills += 1

        if not candidate_skills:
            return 30

        match_ratio = matched_skills / len(candidate_skills)

        return min(100, match_ratio * 100 * 1.5)

    def _calculate_location_score(self, candidate_location: str, job_location: str) -> float:
        if not job_location:
            return 70

        job_loc_lower = job_location.lower()
        cand_loc_lower = candidate_location.lower() if candidate_location else ""

        if 'remote' in job_loc_lower:
            return 90

        if not cand_loc_lower:
            return 50

        if cand_loc_lower in job_loc_lower or job_loc_lower in cand_loc_lower:
            return 90

        return 30

    def _calculate_salary_score(self, salary_min: Optional[int], salary_max: Optional[int],
                                 expected_salary: Optional[int]) -> float:
        if not salary_min and not salary_max:
            return 70

        if not expected_salary:
            return 70

        if salary_min and expected_salary >= salary_min:
            if salary_max and expected_salary <= salary_max:
                return 90
            elif expected_salary <= salary_min * 1.2:
                return 80

        return 50

    def _calculate_experience_score(self, experience: List[Dict], seniority: str, job_description: str) -> float:
        if not experience:
            return 40

        years_exp = len(experience)

        exp_level = 'mid'
        if years_exp <= 2:
            exp_level = 'junior'
        elif years_exp >= 5:
            exp_level = 'senior'

        if seniority:
            seniority_lower = seniority.lower()
            if 'senior' in seniority_lower or 'lead' in seniority_lower or 'principal' in seniority_lower:
                target_level = 'senior'
            elif 'junior' in seniority_lower or 'entry' in seniority_lower or 'intern' in seniority_lower:
                target_level = 'junior'
            else:
                target_level = 'mid'
        else:
            target_level = 'mid'

        if exp_level == target_level:
            return 90
        elif (exp_level == 'senior' and target_level == 'mid') or (exp_level == 'mid' and target_level == 'senior'):
            return 70
        elif exp_level == 'junior' and target_level in ['mid', 'senior']:
            return 30
        elif exp_level == 'senior' and target_level == 'junior':
            return 50
        else:
            return 50

    def _get_recommendation(self, score: float) -> str:
        if score >= 80:
            return 'strong_match'
        elif score >= 60:
            return 'good_match'
        elif score >= 40:
            return 'weak_match'
        else:
            return 'no_match'


fit_scorer = FitScorer()