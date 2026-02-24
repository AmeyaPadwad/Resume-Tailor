# Resume Tailor

A local, AI-powered resume tailoring tool that helps you customize your resume for each job application, track applications, and manage referrals — all running on your machine.

---

## Introduction

Resume Tailor is a Streamlit-based desktop app that combines keyword matching and LLM-powered suggestions to help you tailor your resume to any job description. It uses [Groq API](https://groq.com) for fast, free LLM inference and stores all data locally as CSVs and PDFs — no cloud storage, no subscriptions.

**Features:**

- Store and view your master resume
- Add job descriptions and get an AI match score with keyword gap analysis
- Generate tailored resume suggestions using an LLM
- Track job application status
- Manage a referral database

---

## How to Use

1. **Master Resume tab** — Upload your resume as a PDF. This becomes the base for all tailoring.
2. **Add Job Description tab** — Paste a job description along with the company name and job title. Hit:
   - `Save Job` to log the application
   - `Tailor Resume` to get an AI match score, keyword gaps, and suggested bullet rewrites
3. **Tracking tab** — View all saved applications, update their status, and read notes.
4. **Referral Database tab** — Log contacts at companies you're applying to for easy reference.

The data is stored in the following structure in the root directory:

```
root/
└── data/
    ├── resumes/
    │   ├── master_resume.pdf
    │   ├── tailored_resume_1.pdf
    │   ├── tailored_resume_2.pdf
    │   └── ...
    ├── jobs.csv
    └── referrals.csv
```

---

## Setup

### 1. Install dependencies

Run the setup script from the project root:

```bash
bash setup.sh
```

This will create a virtual environment and install all required packages.

### 2. Get a Groq API key

Groq provides free, fast LLM inference. To get your key:

1. Go to [console.groq.com](https://console.groq.com) and sign up for a free account
2. Navigate to **API Keys** in the left sidebar
3. Click **Create API Key**, give it a name, and copy the key

### 3. Add your API key

Open the `.env` file in the project root directory and add your API key:

```
GROQ_API_KEY=your_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## Tasks To Be Completed

### Add Job Description Tab

- [ ] Clear text fields after form submission
- [x] Display LLM outputs (score, gaps, rewrites) in a clean, readable format
- [ ] Add functionality to directly generate and write tailored PDF resumes
- [ ] Show before and after match score comparison
- [ ] Allow edits to LLM suggestions before generating the final PDF
- [ ] Design indexing logic for storing and referencing tailored PDFs
- [ ] Add flag for job postings that mention no visa sponsorship
- [ ] Add validation to warn if resume exceeds one page

### Project

- [ ] Write `setup.sh` for one-command environment setup
- [ ] Determine evaluation strategy for LLM quality:
  - Resume scoring accuracy
  - Relevance and faithfulness of tailoring suggestions
- [ ] Decide on deployment strategy (Streamlit Cloud?) and how to handle persistent local data remotely
- [ ] Change color theme
