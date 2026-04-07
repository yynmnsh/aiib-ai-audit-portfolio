"""
AI-Assisted Audit Report Generator - PoC Prototype
AIIB Internal Audit Office (IAO) - AI Audit Practices Intern
Portfolio by Yayan Puji Riyanto
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time, json, re
from datetime import datetime

st.set_page_config(page_title="AI Audit Report Generator", page_icon="\U0001f916", layout="wide", initial_sidebar_state="expanded")

# ═══ CSS WITH ANIMATIONS ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-primary: #f8fafc; --bg-card: #ffffff; --bg-sidebar: linear-gradient(170deg,#080e1a 0%,#101d35 50%,#0c1829 100%);
    --text-primary: #0f172a; --text-secondary: #475569; --text-muted: #94a3b8;
    --accent: #2563eb; --accent-light: #dbeafe; --accent-glow: rgba(37,99,235,.12);
    --success: #059669; --warning: #d97706; --danger: #dc2626;
    --border: #e2e8f0; --radius: 14px; --shadow-sm: 0 1px 3px rgba(0,0,0,.04); --shadow-md: 0 4px 16px rgba(0,0,0,.06);
}

.block-container, .block-container * { font-family: 'DM Sans', sans-serif; }
code, pre, .stCodeBlock { font-family: 'JetBrains Mono', monospace !important; }
.block-container { padding-top: 2rem; max-width: 1200px; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--bg-sidebar); backdrop-filter: blur(20px); }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] strong { color: #f1f5f9 !important; }

/* Animations */
@keyframes fadeSlideUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseGlow { 0%,100% { box-shadow: 0 0 0 0 var(--accent-glow); } 50% { box-shadow: 0 0 0 8px transparent; } }
@keyframes countUp { from { opacity:0; transform:scale(.8); } to { opacity:1; transform:scale(1); } }

/* Metric Card */
.mc {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 20px; text-align: center; box-shadow: var(--shadow-sm);
    animation: fadeSlideUp .5s ease-out both; transition: transform .2s, box-shadow .2s;
}
.mc:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.mc h3 { font-size:11px; color:var(--text-muted); margin:0 0 6px; text-transform:uppercase; letter-spacing:1px; font-weight:500; }
.mc .v { font-size:28px; font-weight:700; color:var(--text-primary); margin:0; animation: countUp .6s ease-out both; }
.mc .s { font-size:11px; color:var(--text-muted); margin-top:4px; }

/* Section Header */
.sh {
    background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 60%,#2563eb 100%);
    color:white; padding:14px 22px; border-radius:10px; font-size:17px; font-weight:600;
    margin:28px 0 16px; animation: fadeIn .4s ease-out both;
    position:relative; overflow:hidden;
}
.sh::after {
    content:''; position:absolute; top:0; left:0; right:0; bottom:0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.06), transparent);
    background-size: 200% 100%; animation: shimmer 3s ease-in-out infinite;
}

/* Info Box */
.ib {
    background: linear-gradient(135deg, #f0f9ff, #f8fafc); border-left:4px solid var(--accent);
    padding:18px 22px; border-radius:0 var(--radius) var(--radius) 0; margin:12px 0;
    font-size:14px; color:var(--text-secondary); line-height:1.7;
    animation: fadeSlideUp .5s ease-out both;
}

/* Framework Card */
.fc {
    background: var(--bg-card); border:1px solid var(--border); border-radius:var(--radius);
    padding:24px; height:100%; box-shadow: var(--shadow-sm);
    animation: fadeSlideUp .5s ease-out both; transition: transform .2s, box-shadow .2s;
}
.fc:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.fc h4 { color:var(--text-primary); margin-top:0; font-weight:600; }
.fc p { color:var(--text-secondary); font-size:14px; line-height:1.7; }

/* Report Output */
.report-box {
    background: var(--bg-card); border:1px solid var(--border); border-radius:var(--radius);
    padding:32px 36px; margin:16px 0; box-shadow: var(--shadow-md);
    font-size:14px; color:var(--text-primary); line-height:1.8;
    animation: fadeSlideUp .6s ease-out both;
}
.report-box h1 { font-size:20px; color:#0f172a; border-bottom:2px solid var(--accent); padding-bottom:10px; }
.report-box h2 { font-size:16px; color:#1e3a5f; margin-top:24px; }

/* Efficiency Card */
.eff-card {
    background: linear-gradient(135deg,#f0fdf4,#dcfce7); border:1px solid #bbf7d0;
    border-radius:var(--radius); padding:22px; text-align:center;
    animation: fadeSlideUp .5s ease-out both; transition: transform .2s;
}
.eff-card:hover { transform: translateY(-3px); }
.eff-card .big { font-size:38px; font-weight:800; color:#166534; animation: countUp .8s ease-out both; }
.eff-card .label { font-size:13px; color:#166534; margin-top:4px; }

/* Risk colors */
.risk-badge {
    display:inline-block; padding:4px 14px; border-radius:20px;
    font-weight:600; font-size:12px; letter-spacing:.3px;
}
.risk-low { background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; }
.risk-medium { background:#fefce8; color:#854d0e; border:1px solid #fef08a; }
.risk-high { background:#fff7ed; color:#9a3412; border:1px solid #fed7aa; }
.risk-critical { background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }

/* AIIB Card */
.aiib-card {
    background: linear-gradient(135deg,#eff6ff,#dbeafe); border:1px solid #bfdbfe;
    border-radius:var(--radius); padding:22px; margin:8px 0;
    animation: fadeSlideUp .5s ease-out both; transition: transform .2s;
}
.aiib-card:hover { transform: translateY(-2px); }

/* Finding input card */
.finding-card {
    background: var(--bg-card); border:1px solid var(--border); border-radius:var(--radius);
    padding:20px; margin:8px 0; border-left:4px solid var(--accent);
    animation: fadeSlideUp .4s ease-out both;
}

/* Hide Streamlit defaults */
[data-testid="stKeyboardIcon"] {display:none;} [class*="keyboard"] {display:none !important;} #MainMenu {visibility:hidden;} footer {visibility:hidden;} .stDeployButton {display:none;}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { gap:4px; }
.stTabs [data-baseweb="tab"] { padding:10px 20px; font-weight:500; border-radius:8px 8px 0 0; }
</style>
""", unsafe_allow_html=True)

# ═══ CONSTANTS ═══
RISK_RATINGS = ["Low","Medium","High","Critical"]
RISK_COLORS = {"Low":"#22c55e","Medium":"#eab308","High":"#ea580c","Critical":"#dc2626"}
AUDIT_AREAS = ["Procurement & Vendor Management","Treasury Operations","Loan Disbursement Process",
    "IT General Controls","HR & Payroll","Financial Reporting","ESF Compliance",
    "AML/CFT & Sanctions","Project Portfolio Management","Business Continuity","Data Governance","Travel & Expense"]
CONTROL_RATINGS = ["Effective","Needs Improvement","Ineffective"]

DEMOS = {
    "Procurement \u2014 Vendor Due Diligence Gaps": {
        "engagement_title":"Audit of Procurement & Vendor Management Processes",
        "audit_area":"Procurement & Vendor Management","period":"January \u2013 December 2024",
        "department":"Corporate Services",
        "objective":"Assess the design and operating effectiveness of controls over vendor onboarding, due diligence, contract management, and payment processing.",
        "scope":"All vendor contracts >USD 100K executed during audit period. Sample of 45 contracts from population of 182.",
        "findings":[
            {"title":"Incomplete vendor due diligence for 7 of 45 sampled contracts","risk":"High",
             "condition":"7 vendor files (16%) lacked completed integrity due diligence questionnaires. 3 exceeded USD 500K. In 2 cases, onboarding completed before due diligence was finalised.",
             "criteria":"AIIB Procurement Policy Section 4.3 requires completed integrity due diligence prior to contract execution. Enhanced DD required for contracts >USD 250K.",
             "cause":"Procurement team cited time pressure. Current workflow allows contract execution before DD is marked complete in the system.",
             "effect":"Increased exposure to integrity, reputational, and sanctions risk.",
             "recommendation":"Implement system-enforced control: block contract execution until DD status = Complete. Add automated alert for contracts >USD 250K missing enhanced DD.",
             "control_rating":"Ineffective"},
            {"title":"Segregation of duties weakness in contract approval","risk":"Medium",
             "condition":"In 4 instances, the same individual initiated purchase request and approved vendor selection.",
             "criteria":"AIIB Internal Control Framework requires segregation between requisition, selection, and approval for procurement >USD 50K.",
             "cause":"System role configuration allows Procurement Officer role to both initiate and approve. No compensating control exists.",
             "effect":"Increased risk of favouritism or fraud in vendor selection.",
             "recommendation":"Reconfigure system roles to enforce maker-checker. Implement quarterly post-approval review for contracts >USD 250K.",
             "control_rating":"Needs Improvement"},
            {"title":"Contract expiry monitoring gaps","risk":"Low",
             "condition":"12 contracts (7%) operating on expired terms without formal extension.",
             "criteria":"AIIB Procurement Policy Section 6.1 requires valid terms. Extensions must be approved 30 days before expiry.",
             "cause":"No automated contract expiry alert system.",
             "effect":"Services rendered without valid contractual terms may lack legal protection.",
             "recommendation":"Implement automated expiry alerts at 90, 60, and 30 days.",
             "control_rating":"Needs Improvement"},
        ],
        "overall_opinion":"Needs Improvement",
    },
    "IT General Controls \u2014 Access Management": {
        "engagement_title":"Audit of IT General Controls \u2014 Logical Access Management",
        "audit_area":"IT General Controls","period":"July \u2013 December 2024","department":"Information Technology",
        "objective":"Evaluate design and operating effectiveness of logical access controls across core banking, SWIFT, HR, and financial reporting systems.",
        "scope":"Logical access controls for 4 core systems. 200 user accounts, 35 privileged accounts, and JML (joiners-movers-leavers) testing.",
        "findings":[
            {"title":"18 orphaned accounts across core banking and SWIFT","risk":"High",
             "condition":"18 active accounts belonged to departed or transferred staff. 4 were privileged. Longest active: 8 months post-departure.",
             "criteria":"AIIB IT Security Policy Section 3.2 mandates deactivation within 24 hours of departure and review within 5 days of transfer.",
             "cause":"HR departure notifications to IT are manual (email-based). No automated HR-to-IAM feed. Quarterly access reviews did not flag these.",
             "effect":"Orphaned privileged accounts are a significant cybersecurity risk \u2014 difficult to detect through normal monitoring.",
             "recommendation":"Implement automated HR-to-IAM integration. Enhance quarterly review with automated reconciliation against staff roster. Immediately deactivate the 18 identified accounts.",
             "control_rating":"Ineffective"},
            {"title":"12 users with unnecessary admin rights from completed project","risk":"Medium",
             "condition":"12 non-IT users retained system admin privileges from a migration project completed 6 months ago.",
             "criteria":"AIIB IT Security Policy Section 3.4 requires privileged access on time-limited, need-to-have basis with 90-day review.",
             "cause":"No automated expiry for temporary privileged access. 90-day review checks role appropriateness but not temporal validity.",
             "effect":"Excessive privileged access increases blast radius of any compromise and violates least privilege principle.",
             "recommendation":"Implement automated expiry for temporary privileged access (default 90 days). Add temporal validity check to review checklist.",
             "control_rating":"Needs Improvement"},
        ],
        "overall_opinion":"Needs Improvement",
    },
}

SYSTEM_PROMPT = """You are an expert internal auditor at AIIB (Asian Infrastructure Investment Bank).
You generate professional first-draft audit reports following IIA Standards and AIIB internal audit methodology.
Reports must be: professional, objective, evidence-based, structured per IIA Standard 2400,
using formal audit language (condition, criteria, cause, effect), balanced, and actionable.
Format in clean Markdown with clear headers. Do NOT use the word "I" - use "Internal Audit" or "the audit team" instead."""

def build_prompt(data):
    findings_text = ""
    for i, f in enumerate(data["findings"], 1):
        findings_text += f"""
### Finding {i}: {f["title"]}
- **Risk Rating:** {f["risk"]}
- **Condition:** {f["condition"]}
- **Criteria:** {f["criteria"]}
- **Cause:** {f["cause"]}
- **Effect:** {f["effect"]}
- **Recommendation:** {f["recommendation"]}
- **Control Rating:** {f["control_rating"]}
"""
    return f"""Generate a complete professional internal audit report for AIIB:

## Engagement
- **Title:** {data["engagement_title"]}
- **Area:** {data["audit_area"]}
- **Period:** {data["period"]}
- **Department:** {data["department"]}
- **Objective:** {data["objective"]}
- **Scope:** {data["scope"]}
- **Overall Opinion:** {data["overall_opinion"]}

## Findings
{findings_text}

## Required Sections
1. Executive Summary (1 paragraph: opinion, finding count by risk, key themes)
2. Audit Objective & Scope
3. Background (brief context about the area within AIIB)
4. Summary of Findings (table: ID, title, risk rating, control rating)
5. Detailed Findings (full condition-criteria-cause-effect-recommendation per finding)
6. Overall Assessment
7. Management Action Plan (table: finding, action, owner, target date)
8. Appendix: Rating Definitions

Use professional audit language. Acknowledge effective controls where relevant.
Make it ready for Head of IAO review and Audit & Risk Committee presentation."""

def call_llm(prompt, api_key):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=4000,
        system=SYSTEM_PROMPT, messages=[{"role":"user","content":prompt}])
    return msg.content[0].text

def mc(l,v,s="",delay=0):
    st.markdown(f"""<div class="mc" style="animation-delay:{delay}s;">
        <h3>{l}</h3><p class="v">{v}</p><p class="s">{s}</p></div>""", unsafe_allow_html=True)

def count_by_risk(findings):
    c = {"Critical":0,"High":0,"Medium":0,"Low":0}
    for f in findings:
        r = f.get("risk","Medium")
        if r in c: c[r] += 1
    return c

# ═══ SESSION STATE ═══
if "findings" not in st.session_state:
    st.session_state.findings = []
if "generated_report" not in st.session_state:
    st.session_state.generated_report = None
if "gen_meta" not in st.session_state:
    st.session_state.gen_meta = {}

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:12px 0 20px;">
        <div style="font-size:42px;margin-bottom:6px;">\U0001f916</div>
        <div style="font-size:18px;font-weight:700;color:#f1f5f9!important;letter-spacing:-.3px;">AI Audit Report</div>
        <div style="font-size:12px;color:#64748b!important;margin-top:4px;">Generator \u2014 AIIB IAO PoC</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("Anthropic API Key", type="password",
        help="Required for AI generation. Get yours at console.anthropic.com")
    if api_key:
        st.success("API key provided \u2713", icon="\u2705")
    else:
        st.info("Enter API key to enable AI generation", icon="\U0001f511")

    st.divider()

    # Live stats from findings
    findings = st.session_state.findings
    rc = count_by_risk(findings)
    st.markdown(f"""<div style="padding:6px 0;font-size:12px;">
        <div style="color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-weight:600;">Current Input</div>
        <div style="display:flex;justify-content:space-between;margin:5px 0;"><span>Findings</span><span style="font-weight:600;color:#f1f5f9!important;">{len(findings)}</span></div>
        <div style="display:flex;justify-content:space-between;margin:5px 0;"><span>\U0001f534 Critical</span><span style="font-weight:600;color:#fca5a5!important;">{rc["Critical"]}</span></div>
        <div style="display:flex;justify-content:space-between;margin:5px 0;"><span>\U0001f7e0 High</span><span style="font-weight:600;color:#fdba74!important;">{rc["High"]}</span></div>
        <div style="display:flex;justify-content:space-between;margin:5px 0;"><span>\U0001f7e1 Medium</span><span style="font-weight:600;color:#fde047!important;">{rc["Medium"]}</span></div>
        <div style="display:flex;justify-content:space-between;margin:5px 0;"><span>\U0001f7e2 Low</span><span style="font-weight:600;color:#86efac!important;">{rc["Low"]}</span></div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""<div style="font-size:11px;color:#64748b;line-height:1.6;">
        <strong style="color:#94a3b8!important;">How it works</strong><br>
        1. Input structured audit data<br>
        2. AI generates first-draft report (IIA Standards)<br>
        3. Auditor reviews, edits, finalises<br><br>
        <strong style="color:#94a3b8!important;">Model</strong><br>Claude Sonnet 4 (Anthropic)<br><br>
        <strong style="color:#94a3b8!important;">Portfolio by</strong><br>Yayan Puji Riyanto<br>PhD Candidate \u2014 Monash University
    </div>""", unsafe_allow_html=True)

# ═══ TABS ═══
tab1, tab2, tab3, tab4 = st.tabs(["\U0001f916 Generate Report", "\U0001f4ca Efficiency Analysis",
    "\U0001f4d0 Methodology & Governance", "\U0001f4d6 About This PoC"])

# ═══ TAB 1: GENERATOR ═══
with tab1:
    st.markdown("""<div style="animation:fadeSlideUp .5s ease-out both;">
        <h1 style="font-size:30px;font-weight:700;color:#0f172a;margin-bottom:4px;letter-spacing:-.5px;">
        AI-Assisted Audit Report Generator</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">
        Input structured audit findings \u2192 AI generates professional first-draft report</p>
    </div>""", unsafe_allow_html=True)

    # Demo loader
    st.markdown('<div class="sh">\U0001f4c2 Quick Start</div>', unsafe_allow_html=True)
    demo_choice = st.selectbox("Load a demo scenario or build from scratch",
        ["\u2014 Build from scratch \u2014"] + list(DEMOS.keys()))

    if demo_choice != "\u2014 Build from scratch \u2014":
        demo = DEMOS[demo_choice]
        if not st.session_state.findings or st.session_state.findings[0].get("title","") != demo["findings"][0]["title"]:
            st.session_state.findings = [dict(f) for f in demo["findings"]]
        st.success(f"Loaded: **{demo['engagement_title']}** \u2014 {len(demo['findings'])} findings")
    else:
        demo = None

    # Engagement info
    st.markdown('<div class="sh">\U0001f4cb Engagement Information</div>', unsafe_allow_html=True)
    e1,e2 = st.columns(2)
    with e1:
        eng_title = st.text_input("Engagement Title", value=demo["engagement_title"] if demo else "")
        audit_area = st.selectbox("Audit Area", AUDIT_AREAS,
            index=AUDIT_AREAS.index(demo["audit_area"]) if demo and demo["audit_area"] in AUDIT_AREAS else 0)
        department = st.text_input("Department", value=demo["department"] if demo else "")
        period = st.text_input("Audit Period", value=demo["period"] if demo else "")
    with e2:
        objective = st.text_area("Objective", value=demo["objective"] if demo else "", height=80)
        scope = st.text_area("Scope", value=demo["scope"] if demo else "", height=80)
        overall_opinion = st.selectbox("Overall Opinion", ["Effective","Needs Improvement","Ineffective"],
            index=["Effective","Needs Improvement","Ineffective"].index(demo["overall_opinion"]) if demo else 1)

    # Findings
    st.markdown('<div class="sh">\U0001f50d Audit Findings</div>', unsafe_allow_html=True)

    for i, f in enumerate(st.session_state.findings):
        risk_col = RISK_COLORS.get(f.get("risk","Medium"), "#eab308")
        with st.expander(f"Finding {i+1}: {f.get('title','New Finding')}", expanded=(i==0)):
            fc1,fc2 = st.columns([3,1])
            with fc1:
                f["title"] = st.text_input("Title", value=f.get("title",""), key=f"ft_{i}")
                f["condition"] = st.text_area("Condition (What we found)", value=f.get("condition",""), height=70, key=f"fc_{i}")
                f["criteria"] = st.text_area("Criteria (What should be)", value=f.get("criteria",""), height=55, key=f"fcr_{i}")
                f["cause"] = st.text_area("Cause (Why it happened)", value=f.get("cause",""), height=55, key=f"fca_{i}")
                f["effect"] = st.text_area("Effect (Why it matters)", value=f.get("effect",""), height=55, key=f"fe_{i}")
                f["recommendation"] = st.text_area("Recommendation", value=f.get("recommendation",""), height=55, key=f"fr_{i}")
            with fc2:
                f["risk"] = st.selectbox("Risk", RISK_RATINGS,
                    index=RISK_RATINGS.index(f.get("risk","Medium")), key=f"frk_{i}")
                f["control_rating"] = st.selectbox("Control Rating", CONTROL_RATINGS,
                    index=CONTROL_RATINGS.index(f.get("control_rating","Needs Improvement")), key=f"fct_{i}")
                risk_col = RISK_COLORS.get(f["risk"], "#eab308")
                st.markdown(f"""<div style="background:{risk_col};color:white;padding:10px;border-radius:10px;
                    text-align:center;font-weight:700;font-size:14px;margin-top:12px;
                    animation:pulseGlow 2s ease-in-out infinite;">{f["risk"]}</div>""", unsafe_allow_html=True)

    bc1,bc2,_ = st.columns([1,1,4])
    with bc1:
        if st.button("\u2795 Add Finding", use_container_width=True):
            st.session_state.findings.append({"title":"","condition":"","criteria":"","cause":"","effect":"",
                "recommendation":"","risk":"Medium","control_rating":"Needs Improvement"})
            st.rerun()
    with bc2:
        if st.session_state.findings and st.button("\U0001f5d1\ufe0f Remove Last", use_container_width=True):
            st.session_state.findings.pop()
            st.rerun()

    # Generate button
    st.markdown('<div class="sh">\U0001f680 Generate Report</div>', unsafe_allow_html=True)

    valid = [f for f in st.session_state.findings if f.get("title")]
    if not valid:
        st.info("Add at least one finding to generate a report.")
    elif not api_key:
        st.warning("Enter your Anthropic API key in the sidebar to enable generation.")
        st.markdown("""<div class="ib">
            <strong>No API key?</strong> You can still explore the input interface and demo scenarios.
            Get a free key at <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>.
        </div>""", unsafe_allow_html=True)
    else:
        if st.button("\U0001f916 Generate AI Audit Report", type="primary", use_container_width=True):
            audit_data = {"engagement_title":eng_title,"audit_area":audit_area,"department":department,
                "period":period,"objective":objective,"scope":scope,
                "overall_opinion":overall_opinion,"findings":valid}
            prompt = build_prompt(audit_data)
            t0 = time.time()
            with st.spinner("AI is drafting your audit report\u2026"):
                try:
                    report = call_llm(prompt, api_key)
                    gen_time = time.time() - t0
                    st.session_state.generated_report = report
                    st.session_state.gen_meta = {
                        "time": gen_time, "words": len(report.split()),
                        "findings": len(valid), "risk_counts": count_by_risk(valid),
                        "title": eng_title, "opinion": overall_opinion,
                    }
                except Exception as e:
                    st.error(f"API Error: {e}")

    # ═══ DISPLAY REPORT ═══
    if st.session_state.generated_report:
        st.markdown("---")
        meta = st.session_state.gen_meta
        words = meta.get("words", 0)
        gen_time = meta.get("time", 0)
        manual_est = max(120, words // 8)
        savings = max(0, (manual_est*60 - gen_time) / (manual_est*60) * 100)

        e1,e2,e3,e4 = st.columns(4)
        with e1:
            st.markdown(f"""<div class="eff-card" style="animation-delay:0s;">
                <div class="big">{gen_time:.0f}s</div><div class="label">Generation Time</div></div>""", unsafe_allow_html=True)
        with e2:
            st.markdown(f"""<div class="eff-card" style="animation-delay:.1s;">
                <div class="big">{words:,}</div><div class="label">Words Generated</div></div>""", unsafe_allow_html=True)
        with e3:
            st.markdown(f"""<div class="eff-card" style="animation-delay:.2s;">
                <div class="big">{manual_est}m</div><div class="label">Est. Manual Drafting</div></div>""", unsafe_allow_html=True)
        with e4:
            st.markdown(f"""<div class="eff-card" style="animation-delay:.3s;">
                <div class="big">{savings:.0f}%</div><div class="label">Time Saved</div></div>""", unsafe_allow_html=True)

        # Consistency panel: shows live sync between input and report
        rc = meta.get("risk_counts", {})
        st.markdown(f"""<div class="ib">
            <strong>\U0001f504 Consistency Check:</strong> Report generated from
            <strong>{meta.get("findings",0)} findings</strong>
            ({rc.get("Critical",0)} Critical, {rc.get("High",0)} High,
            {rc.get("Medium",0)} Medium, {rc.get("Low",0)} Low) \u2014
            Overall Opinion: <strong>{meta.get("opinion","")}</strong>.
            <em>Edit findings above and re-generate to cascade changes throughout the report.</em>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sh">\U0001f4c4 Generated Audit Report (First Draft)</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_report)

        with st.expander("\U0001f4dd Edit Report (Markdown)"):
            edited = st.text_area("", value=st.session_state.generated_report, height=500, label_visibility="collapsed")
            if edited != st.session_state.generated_report:
                st.session_state.generated_report = edited

        ec1,ec2 = st.columns(2)
        with ec1:
            st.download_button("\U0001f4e5 Download (.md)", data=st.session_state.generated_report,
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md", mime="text/markdown", use_container_width=True)
        with ec2:
            st.download_button("\U0001f4e5 Download (.txt)", data=st.session_state.generated_report,
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)

# ═══ TAB 2: EFFICIENCY ═══
with tab2:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Efficiency Analysis</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Quantifying time savings from AI-assisted audit reporting</p>""", unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        AI-assisted reporting shifts auditor time from <strong>mechanical drafting</strong> to
        <strong>analysis, judgment, and stakeholder engagement</strong>.
        Notice that Review & Editing time <em>increases</em> after AI adoption \u2014
        the <strong>human-in-the-loop</strong> principle ensures quality.
    </div>""", unsafe_allow_html=True)

    tasks = ["Finding\nDocumentation","Report\nDrafting","Review &\nEditing","Management\nDiscussion","Finalisation"]
    before = [8,16,6,4,3]
    after = [8,2,8,4,2]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Before AI",x=tasks,y=before,marker_color="#dc2626",text=before,textposition="outside",opacity=.8))
    fig.add_trace(go.Bar(name="After AI",x=tasks,y=after,marker_color="#22c55e",text=after,textposition="outside",opacity=.8))
    fig.update_layout(barmode="group",height=380,margin=dict(t=30,b=50),plot_bgcolor="white",
        yaxis=dict(title="Hours",gridcolor="#f1f5f9"),legend=dict(orientation="h",y=1.08,x=.5,xanchor="center"),
        title="Audit Reporting Time per Engagement",title_font_size=14)
    st.plotly_chart(fig,use_container_width=True)

    s1,s2,s3=st.columns(3)
    with s1: mc("Before AI",f"{sum(before)}h","Per engagement",.1)
    with s2: mc("After AI",f"{sum(after)}h","Per engagement",.2)
    with s3: mc("Time Saved",f"{sum(before)-sum(after)}h",f"{(sum(before)-sum(after))/sum(before)*100:.0f}% reduction",.3)

    st.markdown('<div class="sh">\U0001f4c8 Annual Impact Projection (AIIB IAO)</div>', unsafe_allow_html=True)
    engagements = st.slider("Estimated audit engagements per year",10,50,25)
    hrs_saved = engagements * (sum(before)-sum(after))
    fte = hrs_saved / 1800

    p1,p2,p3=st.columns(3)
    with p1: mc("Annual Hours Saved",f"{hrs_saved:,}",f"Across {engagements} engagements")
    with p2: mc("FTE Equivalent",f"{fte:.1f}","Productive staff-years")
    with p3: mc("Cost Savings",f"${hrs_saved*150:,.0f}","At $150/hr loaded cost")

# ═══ TAB 3: METHODOLOGY ═══
with tab3:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Methodology & Governance Note</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Draft governance framework for AI use in AIIB Internal Audit</p>""", unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        This draft <strong>Methodology & Governance Note</strong> covers data governance, quality assurance,
        ethical considerations, and human oversight for AI/LLM tools in AIIB Internal Audit \u2014
        directly addressing the JD deliverable.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">1. Guiding Principles</div>', unsafe_allow_html=True)
    pr1,pr2,pr3,pr4=st.columns(4)
    with pr1: st.markdown("""<div class="fc" style="text-align:center;border-top:4px solid #2563eb;animation-delay:.1s;">
        <div style="font-size:28px;">\U0001f9d1\u200d\u2696\ufe0f</div><h4>Human-in-the-Loop</h4>
        <p>AI generates drafts; <strong>auditors own the output</strong>. All content must be reviewed and approved before issuance.</p></div>""", unsafe_allow_html=True)
    with pr2: st.markdown("""<div class="fc" style="text-align:center;border-top:4px solid #059669;animation-delay:.2s;">
        <div style="font-size:28px;">\U0001f512</div><h4>Data Confidentiality</h4>
        <p>Audit data is <strong>highly sensitive</strong>. AI processing must comply with AIIB data classification policy.</p></div>""", unsafe_allow_html=True)
    with pr3: st.markdown("""<div class="fc" style="text-align:center;border-top:4px solid #d97706;animation-delay:.3s;">
        <div style="font-size:28px;">\U0001f4cb</div><h4>Audit Trail</h4>
        <p>All AI work must be <strong>documented</strong>: prompt, model version, timestamp, reviewer identity.</p></div>""", unsafe_allow_html=True)
    with pr4: st.markdown("""<div class="fc" style="text-align:center;border-top:4px solid #dc2626;animation-delay:.4s;">
        <div style="font-size:28px;">\u26a0\ufe0f</div><h4>Hallucination Risk</h4>
        <p>LLMs can generate <strong>incorrect information</strong>. Auditors must verify all facts against source evidence.</p></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">2. Permitted & Prohibited Uses</div>', unsafe_allow_html=True)
    u1,u2=st.columns(2)
    with u1:
        st.markdown("""<div class="fc" style="border-left:4px solid #22c55e;"><h4 style="color:#166534;">\u2705 Permitted</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li>Drafting audit reports from structured findings</li>
            <li>Summarising policy documents for planning</li>
            <li>Generating data analysis code (Python/SQL)</li>
            <li>Translating findings between languages</li>
            <li>Creating presentations from finalised reports</li>
            <li>Anomaly detection on structured data</li>
        </ul></div>""", unsafe_allow_html=True)
    with u2:
        st.markdown("""<div class="fc" style="border-left:4px solid #dc2626;"><h4 style="color:#991b1b;">\u274c Prohibited</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li>Making audit opinions or professional judgments</li>
            <li>Processing personal data without DPA</li>
            <li>Sending classified workpapers to external APIs</li>
            <li>Replacing evidence gathering or interviews</li>
            <li>Auto-publishing without human review</li>
            <li>Using AI as sole basis for audit ratings</li>
        </ul></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">3. Three-Stage QA Framework</div>', unsafe_allow_html=True)
    st.markdown("""<div class="fc"><h4>Quality Assurance for AI-Generated Reports</h4>
        <p><strong>Stage 1 \u2014 Automated Checks:</strong> Verify structural completeness, check for hallucination patterns,
        validate finding IDs and cross-references.</p>
        <p><strong>Stage 2 \u2014 Auditor Review:</strong> Review against source evidence (workpapers, notes, screenshots).
        Correct inaccuracies, add professional judgment. Minimum 2 hours per report (enforced).</p>
        <p><strong>Stage 3 \u2014 Engagement Lead Sign-off:</strong> Final review for accuracy, completeness, and tone.
        Notation: "AI-assisted draft, reviewed and approved by [Name]."</p></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">4. AI Risk Register</div>', unsafe_allow_html=True)
    ai_risks = pd.DataFrame([
        {"Risk":"LLM Hallucination","Likelihood":"Likely","Impact":"High","Mitigation":"Mandatory human review; fact-checking against workpapers"},
        {"Risk":"Data Leakage","Likelihood":"Unlikely","Impact":"Critical","Mitigation":"AIIB-hosted AI service; encryption; DPA with provider"},
        {"Risk":"Over-reliance","Likelihood":"Possible","Impact":"High","Mitigation":"Mandatory minimum review time; AI output flagged as draft"},
        {"Risk":"Bias in Outputs","Likelihood":"Possible","Impact":"Medium","Mitigation":"Diverse review team; bias awareness training"},
        {"Risk":"Inconsistent Quality","Likelihood":"Likely","Impact":"Medium","Mitigation":"Standardised prompt templates; input completeness checks"},
    ])
    def rs(v):
        m={"Critical":"background-color:#fef2f2;color:#991b1b;font-weight:600","High":"background-color:#fff7ed;color:#9a3412;font-weight:600",
           "Medium":"background-color:#fefce8;color:#854d0e","Likely":"background-color:#fff7ed;color:#9a3412",
           "Possible":"background-color:#fefce8;color:#854d0e","Unlikely":"background-color:#f0fdf4;color:#166534"}
        return m.get(v,"")
    st.dataframe(ai_risks.style.map(rs,subset=["Likelihood","Impact"]),use_container_width=True,hide_index=True)

    st.markdown('<div class="sh">5. Implementation Roadmap</div>', unsafe_allow_html=True)
    for phase,desc,delay in [
        ("Phase 1: Pilot (Q1-Q2)","Deploy PoC with 3-5 auditors on low-risk engagements. Measure time savings and quality.",.1),
        ("Phase 2: Controlled Rollout (Q3)","Extend to all IAO staff with training. Establish AI Audit Working Group.",.2),
        ("Phase 3: Expansion (Q4+)","Add knowledge base Q&A, risk intelligence dashboard, continuous monitoring.",.3),
    ]:
        st.markdown(f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:16px 20px;
            margin:8px 0;border-left:4px solid #2563eb;animation:fadeSlideUp .5s ease-out {delay}s both;">
            <div style="font-size:14px;font-weight:600;color:#1e293b;">{phase}</div>
            <div style="font-size:13px;color:#475569;margin-top:4px;">{desc}</div></div>""", unsafe_allow_html=True)

# ═══ TAB 4: ABOUT ═══
with tab4:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">About This PoC</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Architecture, limitations, and AIIB context</p>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">\U0001f3db\ufe0f AIIB Internal Audit Office Context</div>', unsafe_allow_html=True)
    st.markdown("""<div class="ib">
        <strong>IAO</strong> is AIIB\'s <strong>third line of defense</strong>, providing independent assurance
        to the Board on governance, risk management, and internal controls.
        This PoC is part of IAO\'s pilot initiative exploring AI transformation of audit practices.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">\U0001f527 Technical Architecture</div>', unsafe_allow_html=True)
    a1,a2=st.columns(2)
    with a1:
        st.markdown("""<div class="fc"><h4>Components</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Frontend:</strong> Streamlit</li>
            <li><strong>LLM:</strong> Claude Sonnet 4 via Anthropic API</li>
            <li><strong>Prompt:</strong> IIA Standards system prompt + structured user data</li>
            <li><strong>Output:</strong> Markdown audit report with all IIA sections</li>
        </ul></div>""", unsafe_allow_html=True)
    with a2:
        st.markdown("""<div class="fc"><h4>Production Path</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Deploy:</strong> Self-hosted on AIIB infrastructure</li>
            <li><strong>API:</strong> Anthropic Enterprise or Azure OpenAI with DPA</li>
            <li><strong>Integration:</strong> Audit management system (TeamMate, AuditBoard)</li>
            <li><strong>Auth:</strong> AIIB SSO with role-based access</li>
        </ul></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">\U0001f3db\ufe0f JD Mapping</div>', unsafe_allow_html=True)
    r1,r2,r3=st.columns(3)
    with r1:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f916</div>
            <h4 style="color:#1e40af;margin-top:0;">PoC Delivery</h4>
            <p style="font-size:13px;color:#334155;">This app IS the deliverable \u2014 working prototype of
            "AI-assisted reporting from structured inputs using LLM."</p></div>""", unsafe_allow_html=True)
    with r2:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f4d0</div>
            <h4 style="color:#1e40af;margin-top:0;">Methodology Note</h4>
            <p style="font-size:13px;color:#334155;">Tab 3 contains the governance framework covering principles,
            uses, QA, risk register, and roadmap.</p></div>""", unsafe_allow_html=True)
    with r3:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f4ca</div>
            <h4 style="color:#1e40af;margin-top:0;">Efficiency Proof</h4>
            <p style="font-size:13px;color:#334155;">Tab 2 quantifies time savings with annual projections
            for AIIB IAO.</p></div>""", unsafe_allow_html=True)

# FOOTER
st.divider()
st.markdown("""<div style="text-align:center;color:#94a3b8;font-size:12px;padding:8px 0 16px;line-height:1.8;">
    AI-Assisted Audit Report Generator \u2014 PoC Prototype<br>
    Portfolio by <strong>Yayan Puji Riyanto</strong> \u00b7 PhD Candidate, Monash University \u00b7 MS Business Analytics, CU Boulder<br>
    <em>Prepared for AIIB AI Audit Practices Intern</em>
</div>""", unsafe_allow_html=True)
