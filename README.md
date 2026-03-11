# 📋 Interview Prep Assistant

AI-powered interview preparation tool. Upload JD + Resume → Get personalized interview questions + Mock interview practice.

---

## 🎯 What It Does

```
1. Upload job description (JD) and your resume
2. AI analyzes the gap between JD requirements and your skills
3. Generates personalized interview questions
4. (Phase 2) Conduct mock interview with AI interviewer
5. (Phase 3) Get evaluation report and track progress
```

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/yourusername/interview-prep-assistant.git
cd interview-prep-assistant

# 2. Setup
python -m venv venv
source venv/bin/activate          # Mac/Linux
# .\venv\Scripts\Activate.ps1     # Windows

# 3. Install
pip install -r requirements.txt

# 4. Config
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 5. Run
streamlit run app/main.py
```

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4o-mini
- **Parser**: pdfplumber, python-docx
- **Validation**: Pydantic

---

## 📊 Development Progress

### ✅ Phase 0: Setup (Completed)
```
[✓] Project structure created
[✓] Git initialized
[✓] Dependencies configured
[✓] Environment setup completed
```

### 🚧 Phase 1: MVP - Question Generator (In Progress)
**Target**: Upload files → AI generates personalized questions

**Core Features**:
- [⬜] File upload (PDF/DOCX/TXT)
- [⬜] Text extraction from files
- [⬜] JD analysis (extract required skills, responsibilities)
- [⬜] Resume analysis (extract experience, skills)
- [⬜] Gap analysis (JD vs Resume matching)
- [⬜] Question generation (10 personalized questions)
- [⬜] Display questions with difficulty & reference answers

**Files to Complete** (in order):
```
1. [ ] config.py                          - Global config
2. [ ] models/schemas.py                   - Data models
3. [ ] utils/logger.py                     - Logging
4. [ ] core/parsers/                       - File parsing
   [ ] pdf_parser.py
   [ ] docx_parser.py
   [ ] txt_parser.py
   [ ] parser_factory.py
5. [ ] services/llm_service.py             - LLM wrapper
6. [ ] prompts/                            - Prompt templates
   [ ] jd_extraction.py
   [ ] resume_extraction.py
   [ ] gap_analysis.py
   [ ] question_generation.py
7. [ ] core/analyzers/                     - Analysis logic
   [ ] jd_analyzer.py
   [ ] resume_analyzer.py
   [ ] gap_analyzer.py
8. [ ] core/generators/                    - Question generator
   [ ] question_generator.py
9. [ ] app/main.py                         - App entry
10. [ ] app/pages/                         - UI pages
    [ ] 01_upload.py
    [ ] 02_analysis.py
    [ ] 03_questions.py
```

**Estimated Time**: 3-5 days  
**Commit Strategy**: One commit per file/module completed

---

### 📅 Phase 2: Mock Interview (Planned)
**Target**: Interactive AI interviewer with follow-up questions

**Features**:
- [ ] Chat-based interview interface
- [ ] AI interviewer persona (system prompt)
- [ ] Real-time answer evaluation
- [ ] Follow-up questions based on answers
- [ ] Session state management (conversation memory)
- [ ] Interview completion report

**New Files Needed**:
```
- core/interview/interviewer.py
- core/interview/answer_evaluator.py
- core/interview/session_manager.py
- prompts/interviewer_system.py
- prompts/answer_evaluation.py
- app/pages/04_mock_interview.py
- app/pages/05_report.py
```

**Estimated Time**: 3-5 days

---

### 📅 Phase 3: History & Analytics (Planned)
**Target**: Track progress and build personal question bank

**Features**:
- [ ] SQLite database integration
- [ ] Save interview sessions
- [ ] View history & re-practice
- [ ] Wrong answer notebook
- [ ] Bookmark questions
- [ ] Export reports to PDF
- [ ] Progress tracking dashboard

**New Files Needed**:
```
- models/database.py
- services/db_service.py
- services/export_service.py
- app/pages/06_history.py
- utils/pdf_generator.py
```

**Estimated Time**: 3-5 days

---

## 📁 Project Structure

```
interview-prep-assistant/
│
├── .env                          # API keys (DO NOT COMMIT)
├── .env.example                  # Template
├── .gitignore
├── requirements.txt
├── README.md
├── config.py
│
├── app/                          # Streamlit UI
│   ├── main.py
│   ├── pages/
│   │   ├── 01_upload.py
│   │   ├── 02_analysis.py
│   │   ├── 03_questions.py
│   │   ├── 04_mock_interview.py      # Phase 2
│   │   ├── 05_report.py              # Phase 2
│   │   └── 06_history.py             # Phase 3
│   └── components/
│
├── core/                         # Business logic
│   ├── parsers/                  # File parsing
│   ├── analyzers/                # AI analysis
│   ├── generators/               # Question generation
│   └── interview/                # Mock interview (Phase 2)
│
├── prompts/                      # LLM prompts
├── models/                       # Data models
├── services/                     # Services (LLM, DB, Export)
├── utils/                        # Utilities
├── data/                         # Data storage
│   └── uploads/
└── tests/                        # Tests
```

---

## 🔄 Git Workflow

```bash
# After completing each file/module:
git add .
git commit -m "feat: add [module_name] - [brief description]"
git push

# Example commits:
# git commit -m "feat: add config.py - global settings"
# git commit -m "feat: add PDF parser - extract text from PDF"
# git commit -m "feat: add JD analyzer - LLM-based extraction"
```

---

## 📝 Current Sprint

**Now Working On**: Phase 1 - File Upload & Question Generation  
**Next File**: `config.py`  
**Last Updated**: 2025-01-XX

---

## 📄 License

MIT

---

## 🤝 Contributing

This is a personal learning project. Feedback welcome!

---

**Note**: Update this README after completing each module to track progress.