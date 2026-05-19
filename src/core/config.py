import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AppConfig:
    name: str = "Autonomous Job Agent"
    version: str = "1.0.0"
    debug: bool = True


@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    path: str = "data/job_agent.db"


@dataclass
class JobSourceConfig:
    enabled: bool = True
    easy_apply_only: bool = True
    max_per_day: int = 50
    max_per_search: int = 50
    search_params: Dict[str, Any] = field(default_factory=dict)
    remote_only: bool = False


@dataclass
class ScoringConfig:
    min_score: int = 60
    weights: Dict[str, int] = field(default_factory=lambda: {
        "title_match": 25,
        "skills_match": 30,
        "location_match": 15,
        "salary_match": 15,
        "experience_match": 15
    })


@dataclass
class AutomationConfig:
    headless: bool = False
    slow_mode: bool = True
    delay_min: int = 1000
    delay_max: int = 3000


@dataclass
class AIConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None


@dataclass
class CoverLetterConfig:
    style: str = "modern"
    max_words: int = 350
    include_contact: bool = True


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    to_emails: list = field(default_factory=list)


@dataclass
class WhatsAppConfig:
    enabled: bool = False
    twilio_sid: str = ""
    twilio_token: str = ""
    from_number: str = ""
    to_number: str = ""


@dataclass
class NotificationConfig:
    email: EmailConfig = field(default_factory=EmailConfig)
    whatsapp: WhatsAppConfig = field(default_factory=WhatsAppConfig)


@dataclass
class UserProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    summary: str = ""
    experience: list = field(default_factory=list)
    education: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    certifications: list = field(default_factory=list)
    languages: list = field(default_factory=list)


@dataclass
class PlatformCredentials:
    email: str = ""
    password: str = ""


@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    job_sources: Dict[str, JobSourceConfig] = field(default_factory=dict)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    cover_letter: CoverLetterConfig = field(default_factory=CoverLetterConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    user: UserProfile = field(default_factory=UserProfile)
    platforms: Dict[str, PlatformCredentials] = field(default_factory=dict)


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / "config" / "default.yaml")

    def _load_config(self) -> Config:
        if not os.path.exists(self.config_path):
            return Config()

        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            return Config()

        config = Config()

        if 'app' in data:
            config.app = AppConfig(**data['app'])

        if 'database' in data:
            config.database = DatabaseConfig(**data['database'])

        if 'job_sources' in data:
            config.job_sources = {
                k: JobSourceConfig(**v) for k, v in data['job_sources'].items()
            }

        if 'scoring' in data:
            config.scoring = ScoringConfig(**data['scoring'])

        if 'automation' in data:
            config.automation = AutomationConfig(**data['automation'])

        if 'ai' in data:
            config.ai = AIConfig(**data['ai'])
            config.ai.api_key = os.environ.get('OPENAI_API_KEY')

        if 'cover_letter' in data:
            config.cover_letter = CoverLetterConfig(**data['cover_letter'])

        if 'notifications' in data:
            config.notifications = NotificationConfig(**data['notifications'])

        if 'user' in data:
            user_data = data['user']
            if 'profile' in user_data:
                user_data = user_data['profile']
            config.user = UserProfile(**user_data)

        if 'platforms' in data:
            config.platforms = {
                k: PlatformCredentials(**v) for k, v in data['platforms'].items()
            }

        return config

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        data = self._to_dict()
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def _to_dict(self) -> Dict:
        return {
            'app': {
                'name': self.config.app.name,
                'version': self.config.app.version,
                'debug': self.config.app.debug
            },
            'database': {
                'type': self.config.database.type,
                'path': self.config.database.path
            },
            'job_sources': {
                k: {'enabled': v.enabled, 'easy_apply_only': v.easy_apply_only,
                    'max_per_day': v.max_per_day, 'search_params': v.search_params}
                for k, v in self.config.job_sources.items()
            },
            'scoring': {
                'min_score': self.config.scoring.min_score,
                'weights': self.config.scoring.weights
            },
            'automation': {
                'headless': self.config.automation.headless,
                'slow_mode': self.config.automation.slow_mode,
                'delay_min': self.config.automation.delay_min,
                'delay_max': self.config.automation.delay_max
            },
            'ai': {
                'provider': self.config.ai.provider,
                'model': self.config.ai.model,
                'temperature': self.config.ai.temperature,
                'max_tokens': self.config.ai.max_tokens
            },
            'cover_letter': {
                'style': self.config.cover_letter.style,
                'max_words': self.config.cover_letter.max_words,
                'include_contact': self.config.cover_letter.include_contact
            },
            'notifications': {
                'email': {
                    'enabled': self.config.notifications.email.enabled,
                    'smtp_host': self.config.notifications.email.smtp_host,
                    'smtp_port': self.config.notifications.email.smtp_port,
                    'username': self.config.notifications.email.username,
                    'password': self.config.notifications.email.password,
                    'from_email': self.config.notifications.email.from_email,
                    'to_emails': self.config.notifications.email.to_emails
                },
                'whatsapp': {
                    'enabled': self.config.notifications.whatsapp.enabled,
                    'twilio_sid': self.config.notifications.whatsapp.twilio_sid,
                    'twilio_token': self.config.notifications.whatsapp.twilio_token,
                    'from_number': self.config.notifications.whatsapp.from_number,
                    'to_number': self.config.notifications.whatsapp.to_number
                }
            },
            'user': {
                'name': self.config.user.name,
                'email': self.config.user.email,
                'phone': self.config.user.phone,
                'location': self.config.user.location,
                'linkedin_url': self.config.user.linkedin_url,
                'summary': self.config.user.summary,
                'experience': self.config.user.experience,
                'education': self.config.user.education,
                'skills': self.config.user.skills,
                'certifications': self.config.user.certifications,
                'languages': self.config.user.languages
            }
        }

    def update_user_profile(self, profile_data: Dict):
        for key, value in profile_data.items():
            if hasattr(self.config.user, key):
                setattr(self.config.user, key, value)
        self.save()

    def get_job_source(self, source: str) -> Optional[JobSourceConfig]:
        return self.config.job_sources.get(source)


config_manager = ConfigManager()