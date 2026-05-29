# 🤖 The Job Hunter's Secret Weapon

### Because Job Searching Shouldn't Feel Like a Full-Time Job

---

## What This Does

### 🎯 Smart Job Matching
Instead of mass-applying to everything, the agent scores each job against my profile (0-100 scale). It factors in:
- Skills match (30%)
- Title relevance (25%)  
- Location preference (15%)
- Salary expectations (15%)
- Experience level (15%)

Only jobs above 60% get flagged. No more spray-and-pray.

### 📄 Resume That Actually Works
Upload my resume once, and the system:
- Parses skills, experience, education automatically
- Extracts keywords for each job application
- Tailors my resume content per job description

### ✍️ Cover Letters That Don't Sound Robotic
Gone are the "I am writing to express my strong interest" templates. The AI generates personalized cover letters that:
- Reference specific projects from my experience
- Map my skills to job requirements
- Sound like an actual human wrote them

### 📊 Actually Useful Tracking
All my applications in one place:
- Pending → Viewed → Interview → Offer/Rejected
- Fit score for each application  
- Response rate analytics
- Daily digest so I never miss a follow-up

### 🎤 Interview Prep That Predicts Questions
Not generic "Tell me about yourself" stuff. It generates:
- Role-specific technical questions
- Behavioral questions based on my experience
- What interviewers actually want to hear
- Scoring guides for self-evaluation

---

## Tech Stack

Built with pure Python (no frameworks to learn):

```
├── Python 3.9+          # Core language
├── SQLite              # Local database (no server needed)
├── PyYAML              # Configuration
├── Playwright          # Browser automation (optional)
└── OpenAI              # AI features (optional)
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/THEcryptoCAP/job-agent.git
cd job-agent
pip3 install -r requirements.txt
```

### 2. Upload Your Resume

```bash
python3 src/cli/main.py profile --upload your_resume.pdf
```

### 3. Search for Jobs

```bash
python3 src/cli/main.py search --keywords "react developer" --remote
```

### 4. Apply Automatically

```bash
python3 src/cli/main.py apply --keywords "full stack" --limit 10
```

### 5. Track Everything

```bash
python3 src/cli/main.py track --stats
```

---

## Commands Reference

| Command | What It Does |
|---------|---------------|
| `profile --upload <file>` | Parse and save your resume |
| `search -k "keywords"` | Find matching jobs |
| `apply -k "keywords" -n 5` | Auto-apply to top 5 jobs |
| `track --stats` | View application dashboard |
| `cover-letter` | Generate personalized letter |
| `interview` | Get interview questions |
| `notify` | Send daily digest |

---

## Features I Actually Use

### 💡 The Daily Digest
Every morning, I get a summary of:
- New jobs matching my criteria
- Applications submitted
- Any responses from recruiters
- Upcoming follow-ups needed

### 🛡️ Blacklist/Whitelist
- **Blacklist**: Companies I've already interviewed with or have bad reviews
- **Whitelist**: Dream companies that always get applied to first

### 🎯 Fit Scoring
The algorithm actually works. A 75+ score means:
- At least 3 skill matches
- Appropriate seniority level
- Reasonable location/salary

### 🤖 Smart Q&A Engine
The screening questions that kill most applications? This handles them automatically with 188+ pre-configured patterns and AI fallback for unknowns.

---

## Why Local?

Everything runs on my machine. No subscriptions, no data leaving my computer, no privacy concerns. The database is a simple SQLite file I can back up anywhere.

---

## Future Roadmap

Things I'm already working on:

- [ ] Real browser automation (currently simulated)
- [ ] Multi-platform support (LinkedIn, Indeed, Wellfound)
- [ ] WhatsApp notifications via Twilio
- [ ] AI-powered salary negotiation tips
- [ ] Interview scheduling integration

---

## The Reality Check

This won't get you 100 applications per day. That's not the point. The point is:

- **Quality over quantity** - 10 well-matched applications > 100 generic ones
- **Personalization at scale** - Each application feels handcrafted
- **Follow-through** - Actually tracking responses and follow-ups

---

## Want to Try It?

```bash
# Just search first to see what's out there
python3 src/cli/main.py search -k "software engineer" --remote -n 10
```

The job search doesn't have to suck. Let the agent do the grunt work. 🚀

---

## Connect

- GitHub: [THEcryptoCAP](https://github.com/THEcryptoCAP)
- LinkedIn: [Avinash Singh](https://linkedin.com/in/avinash-singh-33335a259)
- Email: cryptocapinoid@gmail.com

---

*Built with 🔥 by an IIT Delhi student who got tired of the job search grind.*
