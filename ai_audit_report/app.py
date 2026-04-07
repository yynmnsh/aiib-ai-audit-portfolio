"""
AI-Assisted Audit Report Generator — PoC Prototype
AIIB Internal Audit Office (IAO) — AI Audit Practices Intern
Portfolio by Yayan Puji Riyanto

Demonstrates LLM-powered generation of first-draft audit reports
from structured inputs, showcasing efficiency gains for IAO.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import time
from datetime import datetime

st.set_page_config(page_title="AI Audit Report Generator — AIIB IAO", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .block-container{padding-top:2.5rem;max-width:1200px;}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#0a1628,#1a2744);}
    [data-testid="stSidebar"] *{color:#cbd5e1!important;}
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] strong{color:#f1f5f9!important;}
    .mc{background:linear-gradient(135deg,#f8fafc,#e2e8f0);border-radius:12px;padding:18px;text-align:center;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,.06);}
    .mc h3{font-size:11px;color:#64748b;margin:0 0 4px;text-transform:uppercase;letter-spacing:.5px;}.mc .v{font-size:24px;font-weight:700;color:#1e293b;margin:0;}.mc .s{font-size:11px;color:#94a3b8;margin-top:3px;}
    .sh{background:linear-gradient(90deg,#0f172a,#1e3a5f);color:white;padding:12px 20px;border-radius:8px;font-size:17px;font-weight:600;margin:22px 0 14px;}
    .ib{background:#f8fafc;border-left:4px solid #3b82f6;padding:14px 18px;border-radius:0 8px 8px 0;margin:10px 0;font-size:14px;color:#334155;line-height:1.6;}
    .fc{background:white;border:1px solid #e2e8f0;border-radius:12px;padding:22px;height:100%;box-shadow:0 1px 3px rgba(0,0,0,.04);}
    .fc h4{color:#1e293b;margin-top:0;}.fc p{color:#475569;font-size:14px;line-height:1.6;}
    .report-box{background:white;border:1px solid #e2e8f0;border-radius:12px;padding:28px 32px;margin:12px 0;box-shadow:0 2px 8px rgba(0,0,0,.06);font-size:14px;color:#1e293b;line-height:1.7;}
    .report-box h1{font-size:20px;color:#0f172a;border-bottom:2px solid #2563eb;padding-bottom:8px;}
    .report-box h2{font-size:16px;color:#1e3a5f;margin-top:20px;}
    .report-box h3{font-size:14px;color:#334155;}
    .finding-input{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin:8px 0;border-left:4px solid #2563eb;}
    .aiib-card{background:linear-gradient(135deg,#eff6ff,#dbeafe);border:1px solid #bfdbfe;border-radius:12px;padding:20px;margin:8px 0;}
    .efficiency-card{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1px solid #bbf7d0;border-radius:12px;padding:20px;text-align:center;}
    .efficiency-card .big{font-size:36px;font-weight:800;color:#166534;}
    #MainMenu{visibility:hidden;}footer{visibility:hidden;}.stDeployButton{display:none;}
</style>
""", unsafe_allow_html=True)

RISK_RATINGS = ["Low", "Medium", "High", "Critical"]
RISK_COLORS = {"Low":"#22c55e","Medium":"#eab308","High":"#ea580c","Critical":"#dc2626"}
AUDIT_AREAS = [
    "Procurement & Vendor Management",
    "Treasury Operations",
    "Loan Disbursement Process",
    "IT General Controls",
    "HR & Payroll",
    "Financial Reporting",
    "Environmental & Social Framework Compliance",
    "AML/CFT & Sanctions Compliance",
    "Project Portfolio Management",
    "Business Continuity Planning",
    "Data Governance & Privacy",
    "Travel & Expense Management",
]
CONTROL_RATINGS = ["Effective", "Needs Improvement", "Ineffective"]

# Pre-loaded demo scenarios
DEMO_SCENARIOS = {
    "Procurement — Vendor Due Diligence Gaps": {
        "engagement_title": "Audit of Procurement & Vendor Management Processes",
        "audit_area": "Procurement & Vendor Management",
        "period": "January – December 2024",
        "department": "Corporate Services",
        "objective": "Assess the design and operating effectiveness of controls over vendor onboarding, due diligence, contract management, and payment processing.",
        "scope": "All vendor contracts >USD 100K executed during the audit period. Sample of 45 contracts from a population of 182. Included review of vendor due diligence files, contract approval workflows, and payment records.",
        "findings": [
            {"title": "Incomplete vendor due diligence for 7 of 45 sampled contracts", "risk": "High",
             "condition": "7 vendor files (16%) lacked completed integrity due diligence questionnaires. 3 of these were contracts exceeding USD 500K. In 2 cases, vendor onboarding was completed before due diligence was finalised.",
             "criteria": "AIIB Procurement Policy Section 4.3 requires completed integrity due diligence prior to contract execution for all vendors. Enhanced due diligence is required for contracts >USD 250K.",
             "cause": "Procurement team cited time pressure from business units as the primary reason. The current workflow allows contract execution before due diligence is marked as 'complete' in the system.",
             "effect": "Increased exposure to integrity, reputational, and sanctions risk. AIIB could inadvertently engage vendors with undisclosed conflicts of interest, sanctions exposure, or adverse media.",
             "recommendation": "Implement system-enforced control: contract execution should be blocked until due diligence status = 'Complete' in the vendor management system. Add automated alert for contracts >USD 250K missing enhanced DD.",
             "control_rating": "Ineffective"},
            {"title": "Segregation of duties weakness in contract approval workflow", "risk": "Medium",
             "condition": "In 4 instances, the same individual initiated the purchase request and approved the vendor selection. The system does not enforce different approvers at each stage.",
             "criteria": "AIIB Internal Control Framework requires segregation of duties between requisition, vendor selection, and approval for all procurement above USD 50K.",
             "cause": "System role configuration allows users with 'Procurement Officer' role to both initiate and approve. No compensating control (e.g., post-approval review) exists.",
             "effect": "Increased risk of favouritism or fraud in vendor selection. Weakens the integrity of the competitive bidding process.",
             "recommendation": "Reconfigure system roles to enforce maker-checker at each procurement stage. Implement quarterly post-approval review by Internal Audit for contracts >USD 250K as compensating control.",
             "control_rating": "Needs Improvement"},
            {"title": "Contract expiry monitoring gaps", "risk": "Low",
             "condition": "12 contracts (7% of population) were operating on expired terms — services continued beyond contract end date without formal extension or renewal.",
             "criteria": "AIIB Procurement Policy Section 6.1 requires all contracts to have valid terms. Extensions must be approved 30 days before expiry.",
             "cause": "No automated contract expiry alert system. Contract owners rely on manual calendar reminders.",
             "effect": "Services rendered without valid contractual terms may lack adequate legal protection and could result in unfavourable terms for AIIB.",
             "recommendation": "Implement automated contract expiry alerts at 90, 60, and 30 days before expiry. Assign contract lifecycle management responsibility to a dedicated Procurement Operations role.",
             "control_rating": "Needs Improvement"},
        ],
        "overall_opinion": "Needs Improvement",
    },
    "IT General Controls — Access Management": {
        "engagement_title": "Audit of IT General Controls — Logical Access Management",
        "audit_area": "IT General Controls",
        "period": "July – December 2024",
        "department": "Information Technology",
        "objective": "Evaluate the design and operating effectiveness of logical access controls across AIIB's core systems including core banking, SWIFT, HR system, and financial reporting platform.",
        "scope": "Logical access controls for 4 core systems. Review of 200 user accounts, 35 privileged accounts, and access provisioning/deprovisioning records for the audit period. Included joiners, movers, and leavers testing.",
        "findings": [
            {"title": "18 orphaned accounts detected across core banking and SWIFT systems", "risk": "High",
             "condition": "18 active user accounts belonged to staff who had left AIIB or transferred to different departments. 4 of these were privileged accounts with elevated system access. The longest active orphaned account was 8 months post-departure.",
             "criteria": "AIIB IT Security Policy Section 3.2 mandates account deactivation within 24 hours of staff departure and access review within 5 business days of internal transfer.",
             "cause": "HR departure notifications to IT are manual (email-based) and inconsistent. No automated feed between HR system and identity management platform. Quarterly access reviews are conducted but did not flag these accounts.",
             "effect": "Orphaned privileged accounts represent a significant cybersecurity risk. Compromised dormant accounts are difficult to detect through normal monitoring and could be exploited for unauthorized access to sensitive financial data.",
             "recommendation": "Implement automated HR-to-IAM integration: staff departure/transfer triggers automatic account suspension. Enhance quarterly access review to include automated reconciliation of active accounts against current staff roster. Immediately deactivate the 18 identified accounts.",
             "control_rating": "Ineffective"},
            {"title": "Excessive privileged access — 12 users with unnecessary admin rights", "risk": "Medium",
             "condition": "12 non-IT users retained system administrator privileges beyond their project-based need. Access was provisioned for a specific system migration project (completed 6 months ago) but never revoked.",
             "criteria": "AIIB IT Security Policy Section 3.4 requires privileged access to be granted on a time-limited, need-to-have basis with mandatory review every 90 days.",
             "cause": "No automated expiry mechanism for temporary privileged access. 90-day review process exists but did not identify these accounts because the review focuses on role appropriateness, not temporal validity.",
             "effect": "Excessive privileged access increases the blast radius of any account compromise and violates the principle of least privilege.",
             "recommendation": "Implement automated expiry for all temporary privileged access (default 90 days, extendable with re-approval). Add temporal validity check to quarterly access review checklist.",
             "control_rating": "Needs Improvement"},
        ],
        "overall_opinion": "Needs Improvement",
    },
}

def mc_render(l,v,s=""):
    st.markdown(f'<div class="mc"><h3>{l}</h3><p class="v">{v}</p><p class="s">{s}</p></div>',unsafe_allow_html=True)

SYSTEM_PROMPT = """You are an expert internal auditor at AIIB (Asian Infrastructure Investment Bank), a multilateral development bank.
You generate professional first-draft audit reports following IIA (Institute of Internal Auditors) standards and AIIB's internal audit methodology.

Your reports must be:
- Professional, objective, and evidence-based
- Structured following IIA Standard 2400 (Communicating Results)
- Using formal audit language (condition, criteria, cause, effect)
- Balanced — acknowledging management strengths alongside findings
- Actionable — recommendations must be specific, measurable, and time-bound

Format the report in clean Markdown with clear section headers.
"""

def build_prompt(data):
    """Build the LLM prompt from structured audit inputs."""
    findings_text = ""
    for i, f in enumerate(data["findings"], 1):
        findings_text += f"""
### Finding {i}: {f['title']}
- **Risk Rating:** {f['risk']}
- **Condition (What we found):** {f['condition']}
- **Criteria (What should be):** {f['criteria']}
- **Cause (Why it happened):** {f['cause']}
- **Effect (Why it matters):** {f['effect']}
- **Recommendation:** {f['recommendation']}
- **Control Rating:** {f['control_rating']}
"""

    prompt = f"""Generate a complete, professional internal audit report for AIIB based on the following structured inputs.

## Engagement Information
- **Title:** {data['engagement_title']}
- **Audit Area:** {data['audit_area']}
- **Audit Period:** {data['period']}
- **Department/Function:** {data['department']}
- **Audit Objective:** {data['objective']}
- **Scope:** {data['scope']}
- **Overall Opinion:** {data['overall_opinion']}

## Findings (Structured Inputs)
{findings_text}

## Instructions for Report Generation
1. Write a complete audit report with these sections:
   - **Executive Summary** (1 paragraph: overall opinion, number of findings by risk rating, key themes)
   - **Audit Objective & Scope**
   - **Background** (brief context about the audit area within AIIB)
   - **Summary of Findings** (overview table of all findings with risk ratings)
   - **Detailed Findings** (each finding with full condition-criteria-cause-effect-recommendation structure, formatted professionally)
   - **Overall Assessment** (opinion on control environment with rationale)
   - **Management Action Plan** (table: finding, agreed action, responsible owner, target date)
   - **Appendix: Rating Definitions** (brief definitions of risk ratings and control ratings used)

2. Use professional, objective audit language throughout.
3. Acknowledge any areas where controls were found to be operating effectively.
4. Make the report ready for review by the Head of IAO and presentation to the Audit & Risk Committee.
5. Format in clean Markdown.
"""
    return prompt

def call_llm(prompt, api_key):
    """Call Claude API to generate report."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:10px 0 18px;'>
        <div style='font-size:36px;margin-bottom:4px;'>🤖</div>
        <div style='font-size:17px;font-weight:700;color:#f1f5f9!important;'>AI Audit Report</div>
        <div style='font-size:12px;color:#94a3b8!important;margin-top:4px;'>Generator — AIIB IAO PoC</div>
    </div>""",unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("Anthropic API Key", type="password", help="Required for AI generation. Get yours at console.anthropic.com")
    if api_key:
        st.success("API key provided ✓")
    else:
        st.warning("Enter API key to enable AI generation")

    st.divider()
    st.markdown("""<div style='font-size:11px;color:#64748b;line-height:1.6;'>
        <strong style='color:#94a3b8!important;'>How it works</strong><br>
        1. Enter structured audit data (findings, risks, controls)<br>
        2. AI generates professional first-draft report following IIA standards<br>
        3. Auditor reviews, edits, and finalises<br><br>
        <strong style='color:#94a3b8!important;'>Model</strong><br>Claude Sonnet 4 (Anthropic)<br><br>
        <strong style='color:#94a3b8!important;'>Portfolio by</strong><br>Yayan Puji Riyanto<br>PhD Candidate — Monash University
    </div>""",unsafe_allow_html=True)

# ═══ TABS ═══
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Generate Report", "📊 Efficiency Analysis", "📐 Methodology & Governance", "📖 About This PoC"])

# ═══ TAB 1: GENERATOR ═══
with tab1:
    st.markdown('<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">AI-Assisted Audit Report Generator</h1><p style="font-size:15px;color:#64748b;margin-top:0;">Input structured audit data → AI generates professional first-draft report</p>',unsafe_allow_html=True)

    # Demo loader
    st.markdown('<div class="sh">📂 Quick Start: Load Demo Scenario</div>',unsafe_allow_html=True)
    demo_choice = st.selectbox("Select a pre-loaded audit scenario (or build your own below)", 
                                ["— Build from scratch —"] + list(DEMO_SCENARIOS.keys()))

    if demo_choice != "— Build from scratch —":
        demo = DEMO_SCENARIOS[demo_choice]
        st.success(f"Loaded: **{demo['engagement_title']}** — {len(demo['findings'])} findings pre-populated below.")
    else:
        demo = None

    # Input form
    st.markdown('<div class="sh">📋 Engagement Information</div>',unsafe_allow_html=True)

    e1,e2 = st.columns(2)
    with e1:
        eng_title = st.text_input("Engagement Title", value=demo["engagement_title"] if demo else "", placeholder="e.g., Audit of Procurement & Vendor Management")
        audit_area = st.selectbox("Audit Area", AUDIT_AREAS, index=AUDIT_AREAS.index(demo["audit_area"]) if demo and demo["audit_area"] in AUDIT_AREAS else 0)
        department = st.text_input("Department/Function", value=demo["department"] if demo else "", placeholder="e.g., Corporate Services")
        period = st.text_input("Audit Period", value=demo["period"] if demo else "", placeholder="e.g., January – December 2024")
    with e2:
        objective = st.text_area("Audit Objective", value=demo["objective"] if demo else "", height=80, placeholder="Describe the objective of this audit engagement...")
        scope = st.text_area("Scope", value=demo["scope"] if demo else "", height=80, placeholder="Describe the scope: population, sample, systems reviewed...")
        overall_opinion = st.selectbox("Overall Opinion", ["Effective", "Needs Improvement", "Ineffective"],
                                       index=["Effective","Needs Improvement","Ineffective"].index(demo["overall_opinion"]) if demo else 1)

    # Findings
    st.markdown('<div class="sh">🔍 Audit Findings</div>',unsafe_allow_html=True)

    if "findings" not in st.session_state:
        if demo:
            st.session_state.findings = [dict(f) for f in demo["findings"]]
        else:
            st.session_state.findings = []

    # Reset findings when demo changes
    if demo and (not st.session_state.findings or st.session_state.findings[0].get("title","") != demo["findings"][0]["title"]):
        st.session_state.findings = [dict(f) for f in demo["findings"]]

    for i, finding in enumerate(st.session_state.findings):
        with st.expander(f"Finding {i+1}: {finding.get('title','New Finding')}", expanded=(i==0)):
            fc1,fc2 = st.columns([3,1])
            with fc1:
                finding["title"] = st.text_input("Finding Title", value=finding.get("title",""), key=f"ft_{i}")
                finding["condition"] = st.text_area("Condition (What we found)", value=finding.get("condition",""), height=80, key=f"fcond_{i}")
                finding["criteria"] = st.text_area("Criteria (What should be)", value=finding.get("criteria",""), height=60, key=f"fcrit_{i}")
                finding["cause"] = st.text_area("Cause (Why it happened)", value=finding.get("cause",""), height=60, key=f"fcause_{i}")
                finding["effect"] = st.text_area("Effect (Why it matters)", value=finding.get("effect",""), height=60, key=f"feff_{i}")
                finding["recommendation"] = st.text_area("Recommendation", value=finding.get("recommendation",""), height=60, key=f"frec_{i}")
            with fc2:
                finding["risk"] = st.selectbox("Risk Rating", RISK_RATINGS, index=RISK_RATINGS.index(finding.get("risk","Medium")), key=f"frisk_{i}")
                finding["control_rating"] = st.selectbox("Control Rating", CONTROL_RATINGS, index=CONTROL_RATINGS.index(finding.get("control_rating","Needs Improvement")), key=f"fctrl_{i}")
                st.markdown(f'<div style="background:{RISK_COLORS[finding["risk"]]};color:white;padding:8px;border-radius:8px;text-align:center;font-weight:600;margin-top:12px;">{finding["risk"]}</div>',unsafe_allow_html=True)

    bc1,bc2,bc3 = st.columns([1,1,4])
    with bc1:
        if st.button("➕ Add Finding", use_container_width=True):
            st.session_state.findings.append({"title":"","condition":"","criteria":"","cause":"","effect":"","recommendation":"","risk":"Medium","control_rating":"Needs Improvement"})
            st.rerun()
    with bc2:
        if st.session_state.findings and st.button("🗑️ Remove Last", use_container_width=True):
            st.session_state.findings.pop()
            st.rerun()

    # Generate
    st.markdown('<div class="sh">🚀 Generate Report</div>',unsafe_allow_html=True)

    valid_findings = [f for f in st.session_state.findings if f.get("title")]

    if not valid_findings:
        st.info("Add at least one finding to generate a report.")
    elif not api_key:
        st.warning("Enter your Anthropic API key in the sidebar to enable AI generation.")
        st.markdown("""<div class="ib">
            <strong>No API key?</strong> You can still explore the input interface and demo scenarios above.
            The report generation requires a valid Anthropic API key — get one free at
            <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>.
        </div>""", unsafe_allow_html=True)
    else:
        if st.button("🤖 Generate AI Audit Report", type="primary", use_container_width=True):
            audit_data = {
                "engagement_title": eng_title, "audit_area": audit_area, "department": department,
                "period": period, "objective": objective, "scope": scope,
                "overall_opinion": overall_opinion, "findings": valid_findings,
            }
            prompt = build_prompt(audit_data)

            start_time = time.time()
            with st.spinner("AI is drafting your audit report... (typically 15-30 seconds)"):
                try:
                    report = call_llm(prompt, api_key)
                    gen_time = time.time() - start_time
                    st.session_state.generated_report = report
                    st.session_state.gen_time = gen_time
                    st.session_state.gen_findings = len(valid_findings)
                    st.session_state.gen_words = len(report.split())
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
                    st.stop()

    # Display generated report
    if "generated_report" in st.session_state:
        st.markdown("---")
        gt = st.session_state.gen_time
        gw = st.session_state.gen_words

        e1,e2,e3,e4 = st.columns(4)
        with e1:
            st.markdown(f'<div class="efficiency-card"><div class="big">{gt:.0f}s</div><div style="font-size:13px;color:#166534;">Generation Time</div></div>',unsafe_allow_html=True)
        with e2:
            st.markdown(f'<div class="efficiency-card"><div class="big">{gw:,}</div><div style="font-size:13px;color:#166534;">Words Generated</div></div>',unsafe_allow_html=True)
        with e3:
            manual_est = max(120, gw // 8)  # ~8 words/min for careful writing
            st.markdown(f'<div class="efficiency-card"><div class="big">{manual_est}m</div><div style="font-size:13px;color:#166534;">Est. Manual Time</div></div>',unsafe_allow_html=True)
        with e4:
            savings = max(0, (manual_est*60 - gt) / (manual_est*60) * 100)
            st.markdown(f'<div class="efficiency-card"><div class="big">{savings:.0f}%</div><div style="font-size:13px;color:#166534;">Time Saved</div></div>',unsafe_allow_html=True)

        st.markdown('<div class="sh">📄 Generated Audit Report (First Draft)</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="report-box">{st.session_state.generated_report}</div>', unsafe_allow_html=True)

        # Also show as editable markdown
        with st.expander("📝 Edit Report (Markdown)"):
            edited = st.text_area("Edit the generated report:", value=st.session_state.generated_report, height=500)

        # Export
        ec1,ec2 = st.columns(2)
        with ec1:
            st.download_button("📥 Download Report (Markdown)", data=st.session_state.generated_report,
                              file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md", mime="text/markdown", use_container_width=True)
        with ec2:
            st.download_button("📥 Download Report (Text)", data=st.session_state.generated_report,
                              file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)

# ═══ TAB 2: EFFICIENCY ═══
with tab2:
    st.markdown('<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Efficiency Analysis</h1><p style="font-size:15px;color:#64748b;margin-top:0;">Quantifying time savings from AI-assisted audit reporting</p>',unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        The primary value proposition of AI-assisted audit reporting is <strong>efficiency gain in first-draft creation</strong>.
        Auditors spend significant time transforming structured findings (captured during fieldwork) into narrative report format.
        AI can reduce this drafting time by 70-90%, allowing auditors to focus on <strong>analysis, judgment, and stakeholder engagement</strong>
        — the high-value activities that cannot be automated.
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">⏱️ Time Allocation: Before vs After AI</div>',unsafe_allow_html=True)

    # Waterfall
    tasks = ["Finding Documentation", "Report Drafting", "Review & Editing", "Management Discussion", "Finalisation"]
    before_hrs = [8, 16, 6, 4, 3]
    after_hrs = [8, 2, 8, 4, 2]

    fig_eff = go.Figure()
    fig_eff.add_trace(go.Bar(name="Before AI", x=tasks, y=before_hrs, marker_color="#dc2626", text=before_hrs, textposition="outside", opacity=0.8))
    fig_eff.add_trace(go.Bar(name="After AI", x=tasks, y=after_hrs, marker_color="#22c55e", text=after_hrs, textposition="outside", opacity=0.8))
    fig_eff.update_layout(barmode="group", height=350, margin=dict(t=30,b=30), plot_bgcolor="white",
                          yaxis=dict(title="Hours", gridcolor="#f1f5f9"),
                          legend=dict(orientation="h",y=1.08,x=.5,xanchor="center"),
                          title="Audit Reporting Time per Engagement",title_font_size=14)
    st.plotly_chart(fig_eff, use_container_width=True)

    s1,s2,s3 = st.columns(3)
    with s1: mc_render("Before AI", f"{sum(before_hrs)}h", "Per engagement")
    with s2: mc_render("After AI", f"{sum(after_hrs)}h", "Per engagement")
    with s3: mc_render("Time Saved", f"{sum(before_hrs)-sum(after_hrs)}h", f"{(sum(before_hrs)-sum(after_hrs))/sum(before_hrs)*100:.0f}% reduction")

    st.markdown("""<div class="ib">
        <strong>Key insight:</strong> AI doesn't just reduce drafting time — it <strong>shifts time allocation</strong> from
        mechanical drafting to higher-value review and editing. Notice that "Review & Editing" time <em>increases</em> after
        AI adoption because auditors invest more time in quality review of AI-generated content, ensuring accuracy and
        professional judgment are properly reflected. This is the <strong>human-in-the-loop</strong> principle in action.
    </div>""",unsafe_allow_html=True)

    # Annual impact projection
    st.markdown('<div class="sh">📈 Annual Impact Projection (AIIB IAO)</div>',unsafe_allow_html=True)
    engagements = st.slider("Estimated audit engagements per year", 10, 50, 25)
    hrs_saved_per = sum(before_hrs) - sum(after_hrs)
    total_saved = engagements * hrs_saved_per
    fte_equivalent = total_saved / 1800  # ~1800 productive hours/year

    p1,p2,p3 = st.columns(3)
    with p1: mc_render("Annual Hours Saved", f"{total_saved:,}", f"Across {engagements} engagements")
    with p2: mc_render("FTE Equivalent", f"{fte_equivalent:.1f}", "Productive staff-years")
    with p3: mc_render("Cost Savings", f"${total_saved * 150:,.0f}", "At $150/hr loaded cost")

# ═══ TAB 3: METHODOLOGY & GOVERNANCE ═══
with tab3:
    st.markdown('<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Methodology & Governance Note</h1><p style="font-size:15px;color:#64748b;margin-top:0;">Draft governance framework for AI use in AIIB Internal Audit</p>',unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        This section provides a draft <strong>Methodology & Governance Note</strong> for the use of AI/LLM tools in
        AIIB's Internal Audit Office — addressing data governance, quality assurance, ethical considerations, and
        human oversight requirements. This directly addresses the JD deliverable: <em>"prepare a methodology & governance note."</em>
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">1. Guiding Principles</div>',unsafe_allow_html=True)
    pr1,pr2,pr3,pr4 = st.columns(4)
    with pr1: st.markdown('<div class="fc" style="text-align:center;border-top:4px solid #2563eb;"><div style="font-size:28px;">🧑‍⚖️</div><h4>Human-in-the-Loop</h4><p>AI generates drafts; <strong>auditors own the output</strong>. All AI-generated content must be reviewed, validated, and approved by a qualified auditor before issuance.</p></div>',unsafe_allow_html=True)
    with pr2: st.markdown('<div class="fc" style="text-align:center;border-top:4px solid #059669;"><div style="font-size:28px;">🔒</div><h4>Data Confidentiality</h4><p>Audit data is <strong>highly sensitive</strong>. AI processing must comply with AIIB's data classification policy. No audit data should be sent to external AI services without encryption and DPA.</p></div>',unsafe_allow_html=True)
    with pr3: st.markdown('<div class="fc" style="text-align:center;border-top:4px solid #d97706;"><div style="font-size:28px;">📋</div><h4>Audit Trail</h4><p>All AI-assisted work must be <strong>documented</strong>: prompt used, model version, timestamp, and reviewer identity. This ensures reproducibility and accountability.</p></div>',unsafe_allow_html=True)
    with pr4: st.markdown('<div class="fc" style="text-align:center;border-top:4px solid #dc2626;"><div style="font-size:28px;">⚠️</div><h4>Hallucination Risk</h4><p>LLMs can generate plausible but <strong>incorrect information</strong>. Auditors must verify all facts, figures, and regulatory references in AI-generated reports against source evidence.</p></div>',unsafe_allow_html=True)

    st.markdown('<div class="sh">2. Permitted & Prohibited Uses</div>',unsafe_allow_html=True)
    u1,u2 = st.columns(2)
    with u1:
        st.markdown("""<div class="fc" style="border-left:4px solid #22c55e;">
            <h4 style="color:#166534;">✅ Permitted Uses</h4>
            <ul style="font-size:13px;color:#475569;line-height:1.8;">
                <li>Drafting audit reports from structured findings</li>
                <li>Summarising lengthy policy documents for audit planning</li>
                <li>Generating data analysis code (Python/SQL) for audit testing</li>
                <li>Translating audit findings between languages</li>
                <li>Creating presentation materials from finalised reports</li>
                <li>Anomaly detection on structured financial/operational data</li>
            </ul>
        </div>""",unsafe_allow_html=True)
    with u2:
        st.markdown("""<div class="fc" style="border-left:4px solid #dc2626;">
            <h4 style="color:#991b1b;">❌ Prohibited Uses</h4>
            <ul style="font-size:13px;color:#475569;line-height:1.8;">
                <li>Making audit opinions or professional judgments</li>
                <li>Processing personal data of AIIB staff without DPA</li>
                <li>Sending classified or restricted audit workpapers to external AI APIs</li>
                <li>Replacing auditor evidence gathering or interview processes</li>
                <li>Auto-publishing AI-generated content without human review</li>
                <li>Using AI outputs as sole basis for audit ratings</li>
            </ul>
        </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">3. Quality Assurance Framework</div>',unsafe_allow_html=True)
    st.markdown("""<div class="fc">
        <h4>Three-Stage QA for AI-Generated Reports</h4>
        <p><strong>Stage 1 — Automated Checks:</strong> Verify structural completeness (all required sections present),
        check for known hallucination patterns (fabricated policy references, invented statistics),
        validate finding IDs and cross-references.</p>
        <p><strong>Stage 2 — Auditor Review:</strong> Qualified auditor reviews AI output against source evidence
        (workpapers, interview notes, system screenshots). Auditor corrects inaccuracies, adds professional
        judgment, and refines language. Minimum review time: 2 hours per report (enforced).</p>
        <p><strong>Stage 3 — Engagement Lead Sign-off:</strong> Engagement lead reviews final report for
        accuracy, completeness, tone, and alignment with IIA Standards. Confirms all AI-generated content
        has been validated. Signs off with notation: "AI-assisted draft, reviewed and approved by [Name]."</p>
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">4. Risk Register — AI in Audit</div>',unsafe_allow_html=True)
    ai_risks = [
        {"risk":"LLM Hallucination","desc":"AI generates plausible but factually incorrect statements in audit report","likelihood":"Likely","impact":"High","mitigation":"Mandatory human review; fact-checking against workpapers; no auto-publish"},
        {"risk":"Data Leakage","desc":"Sensitive audit data sent to external AI API is intercepted or retained","likelihood":"Unlikely","impact":"Critical","mitigation":"Use AIIB-hosted or contractually bound AI service; encryption in transit; DPA with provider"},
        {"risk":"Over-reliance on AI","desc":"Auditors reduce professional skepticism, deferring judgment to AI outputs","likelihood":"Possible","impact":"High","mitigation":"Mandatory minimum review time; AI output flagged as 'draft'; training on AI limitations"},
        {"risk":"Bias in AI Outputs","desc":"AI reproduces biases from training data, affecting audit objectivity","likelihood":"Possible","impact":"Medium","mitigation":"Diverse review team; bias awareness training; periodic output auditing"},
        {"risk":"Inconsistent Quality","desc":"AI output quality varies by prompt quality and input completeness","likelihood":"Likely","impact":"Medium","mitigation":"Standardised prompt templates; input completeness checks; QA checklist"},
    ]
    df_risk = pd.DataFrame(ai_risks)
    def risk_style(v):
        m={"Critical":"background-color:#fef2f2;color:#991b1b;font-weight:600","High":"background-color:#fff7ed;color:#9a3412;font-weight:600",
           "Medium":"background-color:#fefce8;color:#854d0e","Low":"background-color:#f0fdf4;color:#166534",
           "Likely":"background-color:#fff7ed;color:#9a3412","Possible":"background-color:#fefce8;color:#854d0e",
           "Unlikely":"background-color:#f0fdf4;color:#166534"}
        return m.get(v,"")
    st.dataframe(df_risk.style.map(risk_style,subset=["likelihood","impact"]),use_container_width=True,hide_index=True)

    st.markdown('<div class="sh">5. Implementation Roadmap</div>',unsafe_allow_html=True)
    phases = [
        ("Phase 1: Pilot (Q1-Q2)","Deploy PoC with 3-5 volunteer auditors on low-risk engagements. Measure time savings, quality metrics, and user feedback. Refine prompt templates and QA process."),
        ("Phase 2: Controlled Rollout (Q3)","Extend to all IAO staff with mandatory training. Establish AI Audit Working Group for ongoing governance. Integrate with AIIB's audit management system."),
        ("Phase 3: Expansion (Q4+)","Expand AI use cases: knowledge base Q&A, risk intelligence dashboard, continuous monitoring. Publish internal methodology note and share with peer MDB audit functions."),
    ]
    for phase,desc in phases:
        st.markdown(f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;margin:6px 0;border-left:4px solid #2563eb;">
            <div style="font-size:14px;font-weight:600;color:#1e293b;">{phase}</div>
            <div style="font-size:13px;color:#475569;margin-top:4px;">{desc}</div>
        </div>""",unsafe_allow_html=True)

# ═══ TAB 4: ABOUT ═══
with tab4:
    st.markdown('<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">About This PoC</h1><p style="font-size:15px;color:#64748b;margin-top:0;">Technical architecture, limitations, and AIIB context</p>',unsafe_allow_html=True)

    st.markdown('<div class="sh">🏛️ AIIB Internal Audit Office (IAO) Context</div>',unsafe_allow_html=True)
    st.markdown("""<div class="ib">
        The <strong>Internal Audit Office (IAO)</strong> is AIIB's <strong>third line of defense</strong>, providing independent
        and objective assurance to the Board of Directors on the adequacy and effectiveness of governance, risk management,
        and internal controls. IAO reports to the <strong>Audit & Risk Committee</strong> of the Board.<br><br>
        This PoC is part of IAO's pilot initiative exploring how AI can transform audit practices — specifically focusing
        on LLM-powered first-draft report generation as the first use case.
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">🔧 Technical Architecture</div>',unsafe_allow_html=True)
    a1,a2=st.columns(2)
    with a1:
        st.markdown("""<div class="fc">
            <h4>Components</h4>
            <ul style="font-size:13px;color:#475569;line-height:1.8;">
                <li><strong>Frontend:</strong> Streamlit (Python web framework)</li>
                <li><strong>LLM:</strong> Claude Sonnet 4 via Anthropic API</li>
                <li><strong>Prompt Engineering:</strong> System prompt with IIA Standards context + structured user prompt from form inputs</li>
                <li><strong>Output:</strong> Markdown-formatted audit report with all IIA-required sections</li>
            </ul>
        </div>""",unsafe_allow_html=True)
    with a2:
        st.markdown("""<div class="fc">
            <h4>Production Considerations</h4>
            <ul style="font-size:13px;color:#475569;line-height:1.8;">
                <li><strong>Deployment:</strong> Self-hosted on AIIB infrastructure (not public cloud) for data security</li>
                <li><strong>API:</strong> Anthropic Enterprise or Azure OpenAI with AIIB DPA</li>
                <li><strong>Integration:</strong> Connect to audit management system (TeamMate, AuditBoard, etc.)</li>
                <li><strong>Authentication:</strong> AIIB SSO with role-based access control</li>
            </ul>
        </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">⚠️ Limitations of This PoC</div>',unsafe_allow_html=True)
    st.markdown("""<div class="fc">
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Data sensitivity:</strong> This PoC uses external API (Anthropic) — production deployment would require AIIB-hosted or contractually bound AI service</li>
            <li><strong>No document ingestion:</strong> Current version requires manual input of findings — future version could ingest workpapers directly</li>
            <li><strong>No version control:</strong> Report edits are not tracked — production version needs audit trail</li>
            <li><strong>Single model:</strong> Uses Claude only — production could ensemble multiple models for robustness</li>
            <li><strong>No fine-tuning:</strong> Uses general-purpose LLM — fine-tuning on AIIB's historical audit reports would improve quality significantly</li>
        </ul>
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">🏛️ Relevance to JD</div>',unsafe_allow_html=True)
    r1,r2,r3=st.columns(3)
    with r1:
        st.markdown("""<div class="aiib-card">
            <div style="font-size:24px;margin-bottom:6px;">🤖</div>
            <h4 style="color:#1e40af;margin-top:0;">PoC Delivery</h4>
            <p style="font-size:13px;color:#334155;">This app IS the PoC deliverable — "AI-assisted reporting: create first-draft audit reports from structured inputs using LLM, showcasing efficiency gains." Working prototype, not just a slide deck.</p>
        </div>""",unsafe_allow_html=True)
    with r2:
        st.markdown("""<div class="aiib-card">
            <div style="font-size:24px;margin-bottom:6px;">📐</div>
            <h4 style="color:#1e40af;margin-top:0;">Methodology Note</h4>
            <p style="font-size:13px;color:#334155;">Tab 3 contains a draft Methodology & Governance Note covering principles, permitted/prohibited uses, QA framework, risk register, and implementation roadmap — ready for IAO review.</p>
        </div>""",unsafe_allow_html=True)
    with r3:
        st.markdown("""<div class="aiib-card">
            <div style="font-size:24px;margin-bottom:6px;">📊</div>
            <h4 style="color:#1e40af;margin-top:0;">Efficiency Quantification</h4>
            <p style="font-size:13px;color:#334155;">Tab 2 provides quantified efficiency analysis with time savings per engagement and annual impact projection for AIIB IAO — the "showcasing efficiency gains" deliverable.</p>
        </div>""",unsafe_allow_html=True)

# FOOTER
st.divider()
st.markdown("""<div style="text-align:center;color:#94a3b8;font-size:12px;padding:8px 0 16px;line-height:1.8;">
    AI-Assisted Audit Report Generator — PoC Prototype<br>
    Portfolio by <strong>Yayan Puji Riyanto</strong> · PhD Candidate, Business Law & Taxation — Monash University<br>
    MS Business Analytics — University of Colorado Boulder<br>
    <em>Prepared for AIIB AI Audit Practices Intern</em>
</div>""",unsafe_allow_html=True)
