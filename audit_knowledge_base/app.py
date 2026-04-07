"""
Structured Audit Knowledge Base — RAG-Powered Q&A
AIIB Internal Audit Office (IAO) — AI Audit Practices Intern PoC
Portfolio by Yayan Puji Riyanto

Retrieval-Augmented Generation (RAG) prototype enabling
knowledge-based Q&A across the audit lifecycle using
TF-IDF retrieval + Claude LLM generation.
"""
import streamlit as st
import numpy as np
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Audit Knowledge Base Q&A", page_icon="\U0001f4da", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500;9..40,700&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="stApp"] { font-family:'DM Sans',sans-serif; }
p,span,h1,h2,h3,h4,h5,h6,label,div,button,input,textarea,select { font-family:'DM Sans',sans-serif; }
.stIconMaterial,.material-icons,.material-symbols-rounded { font-family:'Material Symbols Rounded' !important; }
code,pre,.stCodeBlock { font-family:'JetBrains Mono',monospace !important; }

:root { --accent:#2563eb; --border:#e2e8f0; --radius:14px; }
.block-container { padding-top:2.5rem; max-width:1200px; }
[data-testid="stSidebar"] { background:linear-gradient(170deg,#080e1a,#101d35,#0c1829); }
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] strong { color:#f1f5f9 !important; }

@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
.mc { background:white; border:1px solid var(--border); border-radius:var(--radius); padding:18px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.04); animation:fadeUp .5s ease-out both; transition:transform .2s; }
.mc:hover { transform:translateY(-2px); }
.mc h3 { font-size:11px; color:#94a3b8; margin:0 0 5px; text-transform:uppercase; letter-spacing:.8px; }
.mc .v { font-size:24px; font-weight:700; color:#0f172a; margin:0; }
.mc .s { font-size:11px; color:#94a3b8; margin-top:3px; }
.sh { background:linear-gradient(135deg,#0f172a,#1e3a5f,#2563eb); color:white; padding:13px 22px; border-radius:10px; font-size:17px; font-weight:600; margin:26px 0 14px; }
.ib { background:#f0f9ff; border-left:4px solid var(--accent); padding:16px 20px; border-radius:0 var(--radius) var(--radius) 0; margin:10px 0; font-size:14px; color:#334155; line-height:1.7; }
.fc { background:white; border:1px solid var(--border); border-radius:var(--radius); padding:22px; height:100%; box-shadow:0 1px 3px rgba(0,0,0,.04); }
.fc h4 { color:#0f172a; margin-top:0; font-weight:600; } .fc p { color:#475569; font-size:14px; line-height:1.6; }
.chat-q { background:linear-gradient(135deg,#2563eb,#1d4ed8); color:white; padding:16px 20px; border-radius:16px 16px 4px 16px; margin:8px 0; font-size:14px; max-width:80%; margin-left:auto; }
.chat-a { background:#f8fafc; border:1px solid #e2e8f0; padding:18px 22px; border-radius:16px 16px 16px 4px; margin:8px 0; font-size:14px; line-height:1.7; color:#1e293b; }
.source-chip { display:inline-block; background:#eff6ff; border:1px solid #bfdbfe; padding:4px 12px; border-radius:16px; font-size:11px; color:#1e40af; margin:3px; font-weight:500; }
.doc-card { background:white; border:1px solid var(--border); border-radius:10px; padding:14px 18px; margin:6px 0; transition:box-shadow .2s; }
.doc-card:hover { box-shadow:0 4px 12px rgba(0,0,0,.08); }
.aiib-card { background:linear-gradient(135deg,#eff6ff,#dbeafe); border:1px solid #bfdbfe; border-radius:var(--radius); padding:22px; margin:8px 0; }
#MainMenu{visibility:hidden;} footer{visibility:hidden;} .stDeployButton{display:none;}
</style>
""", unsafe_allow_html=True)

# ═══ KNOWLEDGE BASE DOCUMENTS ═══
DOCUMENTS = [
    {"id":"POL-001","title":"AIIB Internal Audit Charter","category":"Governance","doc_type":"Policy",
     "content":"""The Internal Audit Office (IAO) provides independent and objective assurance and advisory services to the Board of Directors through the Audit and Risk Committee. IAO operates under a Charter approved by the Board that defines its purpose, authority, and responsibility. The Head of IAO reports functionally to the Audit and Risk Committee and administratively to the President. IAO has unrestricted access to all records, personnel, and physical properties relevant to the performance of audit engagements. IAO staff must maintain objectivity, integrity, confidentiality, and competency in accordance with IIA Standards. The annual audit plan is developed using a risk-based methodology and approved by the Audit and Risk Committee. IAO coordinates with the external auditor to ensure proper coverage and minimise duplication of effort. IAO follows up on the implementation of agreed management actions and reports the status to the Audit and Risk Committee quarterly. The quality assurance and improvement program ensures conformance with IIA Standards through both internal and external assessments."""},
    {"id":"POL-002","title":"AIIB Risk Management Framework","category":"Risk Management","doc_type":"Framework",
     "content":"""The Risk Management Framework provides a coherent foundation for effective risk management by outlining methodology and guidelines for governing key risks. The Bank adopts a Three Lines of Defense model: first line (business units owning risk), second line (Risk Management Department providing oversight), and third line (Internal Audit providing independent assurance). The framework covers credit risk, market risk, liquidity risk, operational risk, compliance risk, and strategic risk. Key Risk Indicators (KRIs) are defined at Board, President, and CRO levels. The Board evaluates Risk Appetite at least annually. The Risk Committee oversees risk-taking activities and ensures alignment with corporate strategy. Operational risk is managed by the Compliance and Operational Risk (COR) unit within the Risk Management Department. COR conducts Risk and Control Self-Assessments (RCSAs), scenario analysis, incident management, and risk reporting. The framework requires all material risks to be identified, assessed, managed, and reported."""},
    {"id":"POL-003","title":"AIIB Procurement Policy","category":"Operations","doc_type":"Policy",
     "content":"""The Procurement Policy governs all procurement activities of the Bank. All procurement must follow principles of economy, efficiency, transparency, and fairness. Contracts above USD 50,000 require competitive bidding. Contracts above USD 250,000 require enhanced due diligence and Procurement Review Committee approval. Vendor onboarding requires integrity due diligence including sanctions screening, beneficial ownership verification, and adverse media checks. The policy mandates segregation of duties between requisition, vendor selection, approval, and payment processing. Contract management includes monitoring of deliverables, performance evaluation, and timely renewal or extension. Extensions must be approved 30 days before expiry. Single-source procurement requires written justification approved by the relevant Vice President. All procurement decisions must be documented and retained for audit purposes. The Procurement Review Committee reviews contracts above threshold and reports to the Head of Corporate Services."""},
    {"id":"POL-004","title":"AIIB IT Security Policy","category":"Information Technology","doc_type":"Policy",
     "content":"""The IT Security Policy establishes the security requirements for protecting AIIB information assets. All users must authenticate using multi-factor authentication (MFA). Privileged access is granted on a time-limited, need-to-have basis with mandatory review every 90 days. Account deactivation must occur within 24 hours of staff departure. Access reviews must be conducted quarterly, reconciling active accounts against the current staff roster. Data is classified into four levels: Public, Internal, Confidential, and Restricted. Confidential and Restricted data must be encrypted at rest and in transit. Incident response follows a defined playbook: detection, containment, eradication, recovery, and lessons learned. Security awareness training is mandatory annually for all staff. Phishing simulations are conducted quarterly. The IT Security team operates a 24/7 Security Operations Center (SOC). Vulnerability assessments are performed monthly and penetration testing annually. Third-party applications must complete a security assessment before deployment."""},
    {"id":"POL-005","title":"AIIB AML/CFT Policy","category":"Compliance","doc_type":"Policy",
     "content":"""The Anti-Money Laundering and Countering the Financing of Terrorism (AML/CFT) Policy aligns with FATF Recommendations and relevant UN Security Council Resolutions. All counterparties must be screened against OFAC SDN, UN Consolidated, and EU sanctions lists before engagement. Ongoing monitoring includes periodic re-screening of active counterparties. Enhanced due diligence is required for high-risk jurisdictions identified by FATF. Suspicious Activity Reports (SARs) must be filed with the Head of COR within 24 hours of detection. Know Your Customer (KYC) procedures apply to all borrowers, co-financing partners, and project counterparties. Politically Exposed Persons (PEPs) require senior management approval for engagement. The policy covers anti-bribery and corruption, requiring all staff to declare conflicts of interest annually. Gifts and hospitality above USD 100 must be reported. Training on AML/CFT is mandatory for all staff annually, with enhanced training for high-risk functions (Treasury, Investment Operations, Procurement)."""},
    {"id":"POL-006","title":"AIIB Environmental and Social Framework (ESF)","category":"Operations","doc_type":"Framework",
     "content":"""The Environmental and Social Framework establishes mandatory requirements for AIIB-financed projects. Environmental and Social Impact Assessments (ESIAs) are required at project appraisal. The framework includes standards on: Environmental and Social Assessment (ES1), Involuntary Resettlement (ES2), Indigenous Peoples (ES3), and Labor and Working Conditions (ES4). Projects are categorised as A (significant impact), B (moderate), C (minimal), or FI (financial intermediary). Category A projects require full ESIA and public consultation. Borrowers must establish grievance redress mechanisms accessible to project-affected communities. The Project-affected People Mechanism (PPM) serves as an independent accountability mechanism for complaints. AIIB conducts supervision missions during project implementation to verify ESF compliance. Non-compliance may trigger remedial actions including suspension of disbursement. All projects must be assessed for Paris Agreement alignment since July 2023."""},
    {"id":"STD-001","title":"IIA Standard 2400 - Communicating Results","category":"Standards","doc_type":"Standard",
     "content":"""IIA Standard 2400 requires that communications include the engagement objectives, scope, and results. Results must include applicable conclusions, recommendations, and action plans. The chief audit executive must communicate results to the appropriate parties. Communications must be accurate, objective, clear, concise, constructive, complete, and timely. Errors and omissions must be communicated to all parties who received the original communication. Engagement communications must include: criteria, condition, cause, and effect for each finding. The overall opinion must be supported by sufficient, reliable, relevant, and useful information. Dissemination of results outside the organisation requires approval of senior management or the board, after considering potential risk. When non-conformance with the Standards impacts a specific engagement, communication of results must disclose the non-conformance and its impact."""},
    {"id":"STD-002","title":"IIA Standard 2300 - Performing the Engagement","category":"Standards","doc_type":"Standard",
     "content":"""Internal auditors must identify, analyse, evaluate, and document sufficient information to achieve the engagement objectives. Engagement supervision must be provided to ensure objectives are achieved, quality is assured, and staff is developed. Internal auditors must identify sufficient, reliable, relevant, and useful information to achieve engagement objectives. Engagement conclusions and results must be based on appropriate analyses and evaluations. Information must be documented to support conclusions and engagement results. The chief audit executive must control access to engagement records and obtain approval before releasing records to external parties. Retention requirements must be consistent with organisation guidelines and any pertinent regulatory or other requirements. Working papers must be prepared by audit staff and reviewed by audit supervisors."""},
    {"id":"PROC-001","title":"Audit Planning Procedure","category":"Methodology","doc_type":"Procedure",
     "content":"""The annual audit plan is developed through a risk-based approach. The audit universe comprises all auditable entities, functions, and processes within AIIB. Risk assessment considers: financial materiality, regulatory significance, complexity, management concerns, prior audit results, and time since last audit. Each auditable area receives a composite risk score determining audit frequency: Critical (quarterly), High (semi-annual), Medium (annual), Low (biennial). The plan includes mandatory coverage areas: financial reporting, IT general controls, procurement, and compliance. Resource allocation is based on risk priority and available audit hours (approximately 15,000 productive hours per year for the IAO team). The plan reserves 15% of capacity for ad-hoc requests and investigations. The plan is presented to the Audit and Risk Committee for approval before the start of each fiscal year. Quarterly progress reports are provided to the Committee."""},
    {"id":"PROC-002","title":"Audit Fieldwork Procedure","category":"Methodology","doc_type":"Procedure",
     "content":"""Audit fieldwork follows a structured methodology. An opening meeting is held with the auditee to discuss scope, timing, and logistics. The audit team prepares an engagement work program detailing tests and procedures. Testing includes: inquiry, observation, inspection, re-performance, and analytical procedures. Sample sizes are determined using statistical or judgmental sampling methods based on population size, expected error rate, and desired confidence level. Findings are documented using the condition-criteria-cause-effect (CCCE) framework. Each finding receives a risk rating (Critical, High, Medium, Low) and a control rating (Effective, Needs Improvement, Ineffective). Draft findings are discussed with management to verify factual accuracy. Management provides action plans with responsible owners and target dates. A closing meeting presents final findings and overall assessment. The engagement report is issued within 15 business days of the closing meeting."""},
    {"id":"PROC-003","title":"Audit Follow-Up Procedure","category":"Methodology","doc_type":"Procedure",
     "content":"""Management is responsible for implementing agreed actions within the target timeframe. IAO tracks implementation status through a centralised action tracking system. Follow-up reviews are conducted at least quarterly. Management provides status updates on each open action: Implemented, In Progress, Not Started, or Revised Timeline. IAO verifies implementation through re-testing of the relevant control or process. Actions not implemented within the original timeline require a revised target date and escalation to the Head of IAO. Actions overdue by more than 90 days are reported to the Audit and Risk Committee. Recurring findings (same issue in consecutive audits) trigger enhanced monitoring and mandatory root cause analysis. The overall closure rate target is 85% within original timelines. Statistics on action implementation are included in the quarterly report to the Audit and Risk Committee."""},
    {"id":"RPT-001","title":"Q3 2024 IAO Quarterly Report (Summary)","category":"Reports","doc_type":"Historical Report",
     "content":"""In Q3 2024, IAO completed 6 audit engagements and 2 advisory assignments. Total findings: 24 (3 Critical, 8 High, 10 Medium, 3 Low). Key themes: IT access management weaknesses, procurement due diligence gaps, and ESF supervision challenges. The overall control environment is assessed as Needs Improvement. Action implementation rate: 78% within original timelines (below 85% target). Overdue actions: 12 (5 from IT, 4 from Procurement, 3 from Investment Operations). The IT General Controls audit identified 18 orphaned accounts including 4 privileged accounts. The Procurement audit found 16% of sampled vendor files lacked completed due diligence. A PPM complaint was received regarding an infrastructure project ESF non-compliance. The Head of IAO recommends focused management attention on IT access management and procurement due diligence as priority remediation areas for Q4 2024."""},
    {"id":"RPT-002","title":"2023 Annual IAO Report (Summary)","category":"Reports","doc_type":"Historical Report",
     "content":"""In 2023, IAO completed 22 audit engagements, 5 advisory assignments, and 2 investigations. Total findings: 89 (8 Critical, 28 High, 39 Medium, 14 Low). Year-over-year, finding volume increased 15%, primarily in IT and Compliance areas reflecting growing organisational complexity. Annual action implementation rate: 82%. Three repeat findings were identified: password policy non-compliance, contract expiry monitoring, and segregation of duties in procurement. The external quality assessment (conducted every 5 years per IIA Standards) confirmed general conformance with IIA Standards. Key recommendations for 2024: invest in data analytics capabilities for continuous auditing, enhance IT audit specialisation, and strengthen ESF audit methodology. IAO headcount increased from 10 to 12 to support expanded coverage. The approved 2024 audit plan includes 25 planned engagements."""},
]

# ═══ RAG ENGINE ═══
@st.cache_resource
def build_index(docs):
    """Build TF-IDF index for document retrieval."""
    corpus = [d["content"] for d in docs]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return vectorizer, tfidf_matrix

def retrieve(query, vectorizer, tfidf_matrix, docs, top_k=3):
    """Retrieve top-k relevant document chunks for a query."""
    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, tfidf_matrix).flatten()
    top_idx = scores.argsort()[-top_k:][::-1]
    results = []
    for idx in top_idx:
        if scores[idx] > 0.05:
            results.append({"doc": docs[idx], "score": float(scores[idx])})
    return results

def generate_answer(query, context_docs, api_key):
    """Generate answer using Claude with retrieved context."""
    import anthropic
    
    context = "\n\n---\n\n".join([
        f"[Source: {d['doc']['id']} - {d['doc']['title']}]\n{d['doc']['content']}"
        for d in context_docs
    ])
    
    system = """You are an AI audit assistant for AIIB (Asian Infrastructure Investment Bank) Internal Audit Office.
Answer questions based ONLY on the provided knowledge base documents. If the answer is not in the documents, say so clearly.
Always cite the source document ID (e.g., POL-001) when referencing specific information.
Be precise, professional, and helpful. Format responses clearly with bullet points where appropriate."""

    prompt = f"""Based on the following knowledge base documents, answer the user question.

## Knowledge Base Context
{context}

## User Question
{query}

## Instructions
- Answer based ONLY on the provided documents
- Cite source document IDs in your answer
- If information is not available in the documents, state this clearly
- Be concise but thorough"""

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=2000,
        system=system, messages=[{"role":"user","content":prompt}])
    return msg.content[0].text

vectorizer, tfidf_matrix = build_index(DOCUMENTS)

def mc(l,v,s=""):
    st.markdown(f'<div class="mc"><h3>{l}</h3><p class="v">{v}</p><p class="s">{s}</p></div>',unsafe_allow_html=True)

SAMPLE_QUESTIONS = [
    "What are the procurement thresholds requiring competitive bidding?",
    "How quickly must accounts be deactivated when staff leave AIIB?",
    "What is the IIA Standard for communicating audit results?",
    "What were the key findings in the Q3 2024 IAO report?",
    "What is the audit follow-up procedure for overdue actions?",
    "How does AIIB screen counterparties for sanctions?",
    "What is the Three Lines of Defense model at AIIB?",
    "What ESF standards apply to involuntary resettlement?",
    "What is the target action implementation rate for IAO?",
    "How are audit engagements prioritised in the annual plan?",
]

# ═══ SESSION STATE ═══
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "qa_count" not in st.session_state:
    st.session_state.qa_count = 0

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:10px 0 18px;">
        <div style="font-size:38px;margin-bottom:4px;">\U0001f4da</div>
        <div style="font-size:17px;font-weight:700;color:#f1f5f9!important;">Audit Knowledge Base</div>
        <div style="font-size:12px;color:#94a3b8!important;margin-top:4px;">RAG-Powered Q&A</div>
    </div>""",unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("Anthropic API Key", type="password")
    if api_key:
        st.success("API key provided", icon="\u2705")
    else:
        st.info("Required for AI answers", icon="\U0001f511")
    
    st.divider()
    st.markdown(f"""<div style="font-size:12px;padding:4px 0;">
        <div style="color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Knowledge Base</div>
        <div style="display:flex;justify-content:space-between;margin:4px 0;"><span>Documents</span><span style="font-weight:600;color:#f1f5f9!important;">{len(DOCUMENTS)}</span></div>
        <div style="display:flex;justify-content:space-between;margin:4px 0;"><span>Categories</span><span style="font-weight:600;color:#f1f5f9!important;">{len(set(d['category'] for d in DOCUMENTS))}</span></div>
        <div style="display:flex;justify-content:space-between;margin:4px 0;"><span>Questions Asked</span><span style="font-weight:600;color:#93c5fd!important;">{st.session_state.qa_count}</span></div>
    </div>""",unsafe_allow_html=True)
    
    st.divider()
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.qa_count = 0
        st.rerun()
    
    st.divider()
    st.markdown("""<div style="font-size:11px;color:#64748b;line-height:1.6;">
        <strong style="color:#94a3b8!important;">How RAG works</strong><br>
        1. Query hits TF-IDF index<br>
        2. Top-3 relevant docs retrieved<br>
        3. Claude generates answer from context<br>
        4. Sources cited in response<br><br>
        <strong style="color:#94a3b8!important;">Portfolio by</strong><br>Yayan Puji Riyanto<br>PhD Candidate \u2014 Monash University
    </div>""",unsafe_allow_html=True)

# ═══ TABS ═══
tab1,tab2,tab3,tab4 = st.tabs(["\U0001f4ac Ask the Knowledge Base","\U0001f4c2 Document Library","\U0001f527 RAG Architecture","\U0001f4d6 About"])

# ═══ TAB 1: Q&A ═══
with tab1:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Audit Knowledge Base Q&A</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Ask questions about AIIB audit policies, procedures, standards, and historical reports</p>""",unsafe_allow_html=True)

    # Sample questions
    st.markdown('<div class="sh">\U0001f4a1 Sample Questions</div>',unsafe_allow_html=True)
    cols = st.columns(2)
    for i, q in enumerate(SAMPLE_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                st.session_state.pending_question = q

    st.markdown('<div class="sh">\U0001f4ac Conversation</div>',unsafe_allow_html=True)

    # Display chat history
    for entry in st.session_state.chat_history:
        st.markdown(f'<div class="chat-q">{entry["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-a">{entry["answer"]}</div>', unsafe_allow_html=True)
        if entry.get("sources"):
            chips = "".join(f'<span class="source-chip">{s["doc"]["id"]}: {s["doc"]["title"]} (score: {s["score"]:.2f})</span>' for s in entry["sources"])
            st.markdown(f'<div style="margin:4px 0 16px;">{chips}</div>', unsafe_allow_html=True)

    # Input
    pending = st.session_state.pop("pending_question", None)
    query = st.chat_input("Ask about AIIB audit policies, procedures, or standards...") or pending

    if query:
        if not api_key:
            st.warning("Enter your Anthropic API key in the sidebar to get AI-generated answers.")
            # Still show retrieval results
            results = retrieve(query, vectorizer, tfidf_matrix, DOCUMENTS, top_k=3)
            st.markdown(f'<div class="chat-q">{query}</div>', unsafe_allow_html=True)
            if results:
                st.markdown("**Retrieved documents (no AI answer without API key):**")
                for r in results:
                    st.markdown(f'<span class="source-chip">{r["doc"]["id"]}: {r["doc"]["title"]} (score: {r["score"]:.2f})</span>', unsafe_allow_html=True)
        else:
            results = retrieve(query, vectorizer, tfidf_matrix, DOCUMENTS, top_k=3)
            with st.spinner("Searching knowledge base and generating answer..."):
                t0 = time.time()
                answer = generate_answer(query, results, api_key)
                elapsed = time.time() - t0
            
            st.session_state.chat_history.append({
                "question": query, "answer": answer,
                "sources": results, "time": elapsed
            })
            st.session_state.qa_count += 1
            st.rerun()

# ═══ TAB 2: DOCUMENT LIBRARY ═══
with tab2:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Document Library</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">All documents indexed in the knowledge base</p>""",unsafe_allow_html=True)

    # Stats
    cats = {}
    types = {}
    for d in DOCUMENTS:
        cats[d["category"]] = cats.get(d["category"],0)+1
        types[d["doc_type"]] = types.get(d["doc_type"],0)+1
    
    c1,c2,c3,c4 = st.columns(4)
    with c1: mc("Total Documents",str(len(DOCUMENTS)),"In knowledge base")
    with c2: mc("Categories",str(len(cats)),"Distinct areas")
    with c3: mc("Document Types",str(len(types)),"Policy, Standard, etc.")
    with c4: mc("Total Words",f"{sum(len(d['content'].split()) for d in DOCUMENTS):,}","Indexed content")

    # Filter
    cat_filter = st.multiselect("Filter by Category", list(cats.keys()), default=list(cats.keys()))
    
    for doc in DOCUMENTS:
        if doc["category"] not in cat_filter:
            continue
        type_colors = {"Policy":"#2563eb","Framework":"#7c3aed","Standard":"#059669","Procedure":"#d97706","Historical Report":"#dc2626"}
        tc = type_colors.get(doc["doc_type"],"#475569")
        word_count = len(doc["content"].split())
        st.markdown(f"""<div class="doc-card" style="border-left:4px solid {tc};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-weight:600;color:#0f172a;">{doc["id"]}</span>
                    <span style="color:#64748b;margin:0 6px;">\u2014</span>
                    <span style="font-weight:500;color:#334155;">{doc["title"]}</span>
                </div>
                <div style="display:flex;gap:6px;">
                    <span style="background:{tc};color:white;padding:2px 10px;border-radius:10px;font-size:11px;font-weight:600;">{doc["doc_type"]}</span>
                    <span style="background:#f1f5f9;color:#64748b;padding:2px 10px;border-radius:10px;font-size:11px;">{doc["category"]}</span>
                    <span style="background:#f1f5f9;color:#64748b;padding:2px 10px;border-radius:10px;font-size:11px;">{word_count} words</span>
                </div>
            </div>
            <div style="font-size:13px;color:#475569;margin-top:8px;line-height:1.5;">{doc["content"][:200]}...</div>
        </div>""",unsafe_allow_html=True)

# ═══ TAB 3: ARCHITECTURE ═══
with tab3:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">RAG Architecture</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">How the Retrieval-Augmented Generation pipeline works</p>""",unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        <strong>RAG</strong> (Retrieval-Augmented Generation) combines information retrieval with LLM generation.
        Instead of relying solely on the LLM, the system first <strong>retrieves relevant documents</strong>
        from the knowledge base, then passes them as context to the LLM for answer generation.
        This ensures answers are <strong>grounded in authoritative source documents</strong> and reduces hallucination.
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">Pipeline Steps</div>',unsafe_allow_html=True)
    steps = [
        ("\U0001f4dd","Ingest","Documents (policies, standards, procedures, reports) are loaded into the knowledge base and preprocessed."),
        ("\U0001f50d","Index","TF-IDF vectorizer converts document text into numerical vectors. In production, this would use dense embeddings (e.g., OpenAI ada-002 or Cohere embed)."),
        ("\u2753","Query","User asks a question in natural language. The query is vectorized using the same TF-IDF model."),
        ("\U0001f3af","Retrieve","Cosine similarity identifies the top-3 most relevant documents from the index. Only documents above a minimum relevance threshold (0.05) are returned."),
        ("\U0001f916","Generate","Retrieved documents are passed as context to Claude (LLM). A system prompt instructs Claude to answer ONLY from the provided context and cite source document IDs."),
        ("\u2705","Respond","The answer is displayed with source citations, allowing the auditor to verify against the original documents."),
    ]
    cols = st.columns(3)
    for i,(icon,title,desc) in enumerate(steps):
        with cols[i%3]:
            st.markdown(f"""<div class="fc" style="text-align:center;margin-bottom:12px;">
                <div style="font-size:28px;margin-bottom:6px;">{icon}</div>
                <h4>Step {i+1}: {title}</h4><p style="font-size:13px;">{desc}</p></div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">PoC vs Production</div>',unsafe_allow_html=True)
    p1,p2 = st.columns(2)
    with p1:
        st.markdown("""<div class="fc" style="border-top:4px solid #d97706;"><h4>This PoC</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Retrieval:</strong> TF-IDF + cosine similarity (sparse vectors)</li>
            <li><strong>Documents:</strong> 13 pre-loaded synthetic AIIB documents</li>
            <li><strong>Chunking:</strong> Whole-document (no chunking)</li>
            <li><strong>LLM:</strong> Claude Sonnet 4 via external API</li>
            <li><strong>Storage:</strong> In-memory (session-only)</li>
        </ul></div>""",unsafe_allow_html=True)
    with p2:
        st.markdown("""<div class="fc" style="border-top:4px solid #059669;"><h4>Production Version</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Retrieval:</strong> Dense embeddings (ada-002/Cohere) + vector DB (Pinecone/Weaviate)</li>
            <li><strong>Documents:</strong> Full AIIB policy library + historical reports (thousands of docs)</li>
            <li><strong>Chunking:</strong> Semantic chunking with overlap (512 tokens, 50 overlap)</li>
            <li><strong>LLM:</strong> AIIB-hosted or enterprise AI with DPA</li>
            <li><strong>Storage:</strong> Persistent vector database with versioning</li>
        </ul></div>""",unsafe_allow_html=True)

# ═══ TAB 4: ABOUT ═══
with tab4:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">About This PoC</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Context, JD mapping, and limitations</p>""",unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        This prototype addresses JD PoC option 2: <em>"Structured Audit Knowledge Base: build a centralized repo
        of policies, procedures, historical reports, and supporting data dictionaries, enabling knowledge-based
        Q&A across audit life cycle."</em>
    </div>""",unsafe_allow_html=True)

    r1,r2,r3 = st.columns(3)
    with r1:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f4da</div>
            <h4 style="color:#1e40af;margin-top:0;">Centralised Repository</h4>
            <p style="font-size:13px;color:#334155;">13 documents indexed across 6 categories: policies, frameworks,
            standards, procedures, and historical reports \u2014 covering the full audit lifecycle.</p></div>""",unsafe_allow_html=True)
    with r2:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f50d</div>
            <h4 style="color:#1e40af;margin-top:0;">Knowledge-Based Q&A</h4>
            <p style="font-size:13px;color:#334155;">RAG pipeline ensures answers are grounded in source documents
            with citations \u2014 auditors can verify every claim against the original policy.</p></div>""",unsafe_allow_html=True)
    with r3:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f504</div>
            <h4 style="color:#1e40af;margin-top:0;">Audit Lifecycle Coverage</h4>
            <p style="font-size:13px;color:#334155;">Supports planning (policy lookup), fieldwork (criteria verification),
            reporting (standards reference), and follow-up (procedure guidance).</p></div>""",unsafe_allow_html=True)

# FOOTER
st.divider()
st.markdown("""<div style="text-align:center;color:#94a3b8;font-size:12px;padding:8px 0 16px;line-height:1.8;">
    Structured Audit Knowledge Base \u2014 RAG PoC Prototype<br>
    Portfolio by <strong>Yayan Puji Riyanto</strong> \u00b7 PhD Candidate, Monash University \u00b7 MS Business Analytics, CU Boulder<br>
    <em>Prepared for AIIB AI Audit Practices Intern</em>
</div>""",unsafe_allow_html=True)
