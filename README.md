# AI Audit Practices Portfolio — AIIB Internship Application

**Yayan Puji Riyanto**
PhD Candidate, Business Law & Taxation — Monash University ||
MS Business Analytics — University of Colorado Boulder ||
IT Governance & Regulatory Analyst, DG Tax — Ministry of Finance, Indonesia (2019–2022)

---

## About This Portfolio

This portfolio demonstrates AI/ML capabilities and domain knowledge relevant to the **Internal Audit Office (IAO)** pilot initiative exploring how AI can transform audit practices at AIIB. It delivers **working prototypes for all three PoC options** specified in the job description, plus supporting artefacts.

---

## Portfolio Artefacts

### Proof-of-Concept Prototypes (All 3 JD Options Delivered)

| # | PoC Option (from JD) | Artefact | Platform | Link |
|---|----------------------|----------|----------|------|
| 1 | **AI-assisted reporting:** create first-draft audit reports from structured inputs using LLM | AI Audit Report Generator | Streamlit | [Open App](https://aiib-ai-audit-report.streamlit.app/) |
| 2 | **Structured Audit Knowledge Base:** centralized repo enabling knowledge-based Q&A across audit lifecycle | Audit Knowledge Base Q&A (RAG) | Streamlit | [Open App](https://aiib-audit-knowledge-base.streamlit.app/) |
| 3 | **Risk Intelligence Dashboard:** visualizing key indicators, anomalies, trends, and alerts for audit planning | Risk Intelligence Dashboard | Streamlit | [Open App](https://aiib-risk-intelligence.streamlit.app/) |

### Supporting Artefacts

| # | Artefact | Purpose | Platform | Link |
|---|----------|---------|----------|------|
| 4 | **ML Anomaly Detection Pipeline** | Complete ML pipeline: data ingestion → feature engineering → 3-model ensemble → auditor-ready flagging report | Google Colab | [Open Notebook](https://colab.research.google.com/drive/1NCZ0_vCpOfctWgHWlYvgPNWopSieco1Q?usp=sharing) |
| 5 | **Methodology & Governance Note** | Draft governance framework for AI use in AIIB Internal Audit (embedded in Artefact #1, Tab 3) | Streamlit | [Open Tab](https://aiib-ai-audit-report.streamlit.app/) |

---

## JD Coverage Map

### Responsibilities

| JD Responsibility | Artefact(s) |
|---|---|
| Develop a PoC: AI-assisted reporting | AI Audit Report Generator — LLM generates first-draft audit reports from structured CCCE findings |
| Develop a PoC: Structured Audit Knowledge Base | Audit Knowledge Base Q&A — RAG pipeline with 13 indexed AIIB audit documents |
| Develop a PoC: Risk Intelligence Dashboard | Risk Intelligence Dashboard — KRI monitoring, ML anomaly detection, audit planning intelligence |
| Prepare a methodology & governance note | Embedded in AI Audit Report Generator (Tab 3): principles, permitted/prohibited uses, QA framework, AI risk register, implementation roadmap |
| Present completed prototype, findings, and recommendations | All apps include "About" tabs with architecture, limitations, and JD mapping |

### Requirements

| JD Requirement | Evidence |
|---|---|
| Enrolled in Masters/MBA/PhD in relevant field | PhD in Business Law & Taxation (Monash University) + MS Business Analytics (CU Boulder) |
| Strong academic record & interest in applying technology to audit | 4 publications (2024–2026); 6+ years experience in regulatory framework design at Indonesia Ministry of Finance |
| Basic understanding of ML, LLMs, and data analysis | Isolation Forest, LOF, Z-Score ensemble, TF-IDF retrieval, RAG architecture, prompt engineering — demonstrated across all artefacts |
| Experience with Python | All artefacts built in Python (Streamlit, scikit-learn, pandas, numpy, plotly, anthropic SDK) |
| Excellent communication skills | Professional UI/UX across all apps; methodology notes; structured reporting |
| Great team player | Cross-institutional negotiation experience (DG Tax ↔ DG Treasury, 516 offices — see OR portfolio) |
| Fluent in English | IELTS 8.5; all artefacts in English; PhD publications in English-language journals |

---

## Artefact Details

### 1. AI Audit Report Generator
**JD Option 1 — AI-assisted reporting**

- **Input:** Structured audit data — engagement info + findings in CCCE format (Condition, Criteria, Cause, Effect)
- **Output:** Complete professional audit report following IIA Standard 2400
- **LLM:** Claude Sonnet 4 (Anthropic API)
- **Features:** 2 pre-loaded AIIB demo scenarios (Procurement, IT General Controls), editable findings, efficiency metrics, downloadable output
- **Methodology Tab:** Complete governance note — guiding principles, permitted/prohibited uses, 3-stage QA, AI risk register, implementation roadmap

### 2. Audit Knowledge Base Q&A
**JD Option 2 — Structured knowledge base**

- **Knowledge Base:** 13 AIIB audit documents across 6 categories (policies, frameworks, standards, procedures, historical reports)
- **Retrieval:** TF-IDF vectorization + cosine similarity (PoC); production path: dense embeddings + vector DB
- **Generation:** Claude with source-grounded prompting — cites document IDs in every answer
- **Interface:** Chat-style Q&A with 10 clickable sample questions, source citation chips, conversation history

### 3. Risk Intelligence Dashboard
**JD Option 3 — Dashboard & audit assistance**

- **Data:** 600 synthetic operational risk events (3 years, 8 departments)
- **KRI Monitoring:** 4-panel monthly dashboard with automated amber/red threshold breach alerts
- **ML Anomaly Detection:** Isolation Forest with adjustable sensitivity, interactive scatter plot, flagged items table
- **Audit Planning:** Composite department risk scorecard, suggested annual audit plan with frequency and hour budget, risk concentration heatmap
- **Trend Analysis:** Multi-year trends, category evolution, Pareto analysis, Z-score time-series anomaly detection

### 4. ML Anomaly Detection Pipeline
**Supporting — ML/analytics demonstration**

- **Data:** 5,000 synthetic MDB transactions with 5% injected anomalies (5 types: large amount, weekend, round number, threshold splitting, velocity)
- **Features:** 9 engineered audit-relevant features (amount z-score, vendor velocity, threshold proximity, off-hours, round number, department deviation)
- **Models:** Isolation Forest + Local Outlier Factor + Z-Score Ensemble → 2-of-3 voting ensemble
- **Output:** Prioritised auditor flagging report with per-transaction investigation reasons
- **Explainability:** Permutation-based feature importance

---

## Technical Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Web Framework** | Streamlit |
| **ML/AI** | scikit-learn (Isolation Forest, LOF), Anthropic Claude API (LLM), TF-IDF (retrieval) |
| **Data & Viz** | pandas, numpy, Plotly, matplotlib |
| **Concepts** | RAG (Retrieval-Augmented Generation), prompt engineering, unsupervised anomaly detection, ensemble methods, CCCE audit framework |
| **Deployment** | Streamlit Cloud, Google Colab |

---

## Repository Structure

```
aiib-ai-audit-portfolio/
├── README.md                              ← This file (portfolio hub)
├── ai_audit_report/
│   ├── app.py                             ← AI Audit Report Generator
│   └── requirements.txt
├── audit_knowledge_base/
│   ├── app.py                             ← Audit Knowledge Base Q&A (RAG)
│   └── requirements.txt
├── risk_intelligence/
│   ├── app.py                             ← Risk Intelligence Dashboard
│   └── requirements.txt
└── notebooks/
    └── ml_anomaly_detection_audit.ipynb    ← ML Anomaly Detection Pipeline
```

---

## Key Differentiator

Most candidates will propose a PoC idea. **This portfolio delivers all three PoC options as working prototypes:**

1. An AI report generator that produces IIA-compliant audit reports in seconds
2. A RAG-powered knowledge base that answers audit questions with source citations
3. A risk intelligence dashboard with ML anomaly detection and audit planning intelligence

Plus a comprehensive methodology & governance note addressing AI risks, quality assurance, and implementation roadmap — demonstrating not just technical capability but also the **governance maturity** needed for responsible AI adoption in internal audit.

---

## Contact

- **Email:** yayan.riyanto@monash.edu
- **Phone:** +61 402 460 353
- **LinkedIn:** [linkedin.com/in/yayan-riyanto-a06481b2](https://linkedin.com/in/yayan-riyanto-a06481b2/)

---

*This portfolio was prepared for the AIIB AI Audit Practices Intern position*
*Internal Audit Office — Asian Infrastructure Investment Bank, Beijing*
