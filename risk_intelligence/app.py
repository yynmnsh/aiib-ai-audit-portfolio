"""
Risk Intelligence Dashboard & Audit Assistance Interface
AIIB Internal Audit Office (IAO) - AI Audit Practices Intern PoC
Portfolio by Yayan Puji Riyanto
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Risk Intelligence Dashboard", page_icon="\U0001f9e0", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500;9..40,700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="stApp"] { font-family: 'DM Sans', sans-serif; }
p,span,h1,h2,h3,h4,h5,h6,label,div,button,input,textarea,select { font-family: 'DM Sans', sans-serif; }
.stIconMaterial,.material-icons,.material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
code,pre,.stCodeBlock { font-family: 'JetBrains Mono', monospace !important; }

:root { --accent:#2563eb; --success:#059669; --warning:#d97706; --danger:#dc2626; --border:#e2e8f0; --radius:14px; }
.block-container { padding-top:2.5rem; max-width:1200px; }
[data-testid="stSidebar"] { background:linear-gradient(170deg,#080e1a,#101d35,#0c1829); }
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] strong { color:#f1f5f9 !important; }

@keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }

.mc { background:white; border:1px solid var(--border); border-radius:var(--radius); padding:18px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.04); animation:fadeUp .5s ease-out both; transition:transform .2s,box-shadow .2s; }
.mc:hover { transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,.08); }
.mc h3 { font-size:11px; color:#94a3b8; margin:0 0 5px; text-transform:uppercase; letter-spacing:.8px; }
.mc .v { font-size:26px; font-weight:700; color:#0f172a; margin:0; }
.mc .s { font-size:11px; color:#94a3b8; margin-top:3px; }
.sh { background:linear-gradient(135deg,#0f172a,#1e3a5f,#2563eb); color:white; padding:13px 22px; border-radius:10px; font-size:17px; font-weight:600; margin:26px 0 14px; }
.ib { background:#f0f9ff; border-left:4px solid var(--accent); padding:16px 20px; border-radius:0 var(--radius) var(--radius) 0; margin:10px 0; font-size:14px; color:#334155; line-height:1.7; }
.fc { background:white; border:1px solid var(--border); border-radius:var(--radius); padding:22px; height:100%; box-shadow:0 1px 3px rgba(0,0,0,.04); }
.fc h4 { color:#0f172a; margin-top:0; font-weight:600; } .fc p { color:#475569; font-size:14px; line-height:1.6; }
.alert-card { border-radius:10px; padding:14px 18px; margin:6px 0; font-size:13px; animation:fadeUp .4s ease-out both; }
.alert-red { background:#fef2f2; border-left:4px solid #dc2626; color:#991b1b; }
.alert-amber { background:#fffbeb; border-left:4px solid #d97706; color:#92400e; }
.alert-green { background:#f0fdf4; border-left:4px solid #059669; color:#065f46; }
.aiib-card { background:linear-gradient(135deg,#eff6ff,#dbeafe); border:1px solid #bfdbfe; border-radius:var(--radius); padding:22px; margin:8px 0; }
#MainMenu{visibility:hidden;} footer{visibility:hidden;} .stDeployButton{display:none;}
</style>
""", unsafe_allow_html=True)

# ═══ DATA GENERATION ═══
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 600
    dates = pd.date_range("2022-01-01","2024-12-31",periods=n).sort_values()
    
    DEPTS = ["Treasury","Investment Operations","IT","Corporate Services","Finance & Accounting","HR","Legal","Risk Management"]
    CATS = ["Execution & Process","System Failures","External Fraud","Internal Fraud","Clients & Products","Employment","Physical Assets"]
    TYPES = ["Disbursement Error","System Outage","Phishing Attack","Expense Fraud","ESF Non-Compliance",
             "Access Control Breach","Payment Delay","Data Entry Error","Vendor Invoice Duplicate",
             "Reconciliation Exception","Unauthorized Access","Contract Expiry","Reporting Error",
             "Sanctions Screening Gap","Staff Grievance","Document Misfile"]
    
    dept_w = [.15,.25,.20,.12,.10,.06,.05,.07]
    cat_w = [.37,.22,.10,.05,.15,.08,.03]
    
    dept = np.random.choice(DEPTS, n, p=dept_w)
    cat = np.random.choice(CATS, n, p=cat_w)
    inc_type = np.random.choice(TYPES, n)
    severity = np.random.choice([1,2,3,4], n, p=[.30,.40,.22,.08])
    
    # Financial impact correlated with severity
    fin = np.where(severity==1, np.random.uniform(0,5000,n),
          np.where(severity==2, np.random.uniform(1000,50000,n),
          np.where(severity==3, np.random.uniform(10000,500000,n),
                               np.random.uniform(100000,5000000,n))))
    fin = np.where(np.random.random(n)<.4, 0, fin)
    
    # Resolution days
    res_days = np.where(severity==1, np.random.lognormal(2.5,.5,n),
               np.where(severity==2, np.random.lognormal(3,.5,n),
               np.where(severity==3, np.random.lognormal(3.5,.5,n),
                                     np.random.lognormal(4,.4,n)))).astype(int).clip(1,200)
    
    # Transaction data for anomaly detection
    tx_amount = np.random.lognormal(10, 1.5, n).clip(1000, 50000000)
    tx_count = np.random.poisson(50, n).clip(1, 500)
    
    # Inject anomalies (5% of data)
    anomaly_idx = np.random.choice(n, int(n*.05), replace=False)
    tx_amount[anomaly_idx] *= np.random.uniform(5, 20, len(anomaly_idx))
    tx_count[anomaly_idx] = np.random.poisson(200, len(anomaly_idx))
    fin[anomaly_idx] = np.random.uniform(500000, 10000000, len(anomaly_idx))
    
    df = pd.DataFrame({
        "date": dates, "department": dept, "category": cat, "incident_type": inc_type,
        "severity": severity, "severity_label": pd.Categorical(severity, categories=[1,2,3,4]).map({1:"Low",2:"Medium",3:"High",4:"Critical"}),
        "financial_impact": fin.round(2), "resolution_days": res_days,
        "tx_amount": tx_amount.round(2), "tx_count": tx_count,
    })
    df["month"] = df.date.dt.to_period("M").astype(str)
    df["quarter"] = df.date.dt.to_period("Q").astype(str)
    df["year"] = df.date.dt.year
    return df, anomaly_idx

df, true_anomalies = generate_data()

SEV_COLORS = {1:"#22c55e",2:"#eab308",3:"#ea580c",4:"#dc2626"}
SEV_LABELS = {1:"Low",2:"Medium",3:"High",4:"Critical"}

def mc(l,v,s=""):
    st.markdown(f'<div class="mc"><h3>{l}</h3><p class="v">{v}</p><p class="s">{s}</p></div>',unsafe_allow_html=True)

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:10px 0 18px;">
        <div style="font-size:38px;margin-bottom:4px;">\U0001f9e0</div>
        <div style="font-size:17px;font-weight:700;color:#f1f5f9!important;">Risk Intelligence</div>
        <div style="font-size:12px;color:#94a3b8!important;margin-top:4px;">Dashboard & Audit Assistance</div>
    </div>""",unsafe_allow_html=True)
    st.divider()
    
    yr = st.selectbox("Year", [2024,2023,2022], index=0)
    dept_filter = st.multiselect("Department", df.department.unique().tolist(), default=df.department.unique().tolist())
    sev_filter = st.multiselect("Severity", [1,2,3,4], default=[1,2,3,4], format_func=lambda x:SEV_LABELS[x])
    
    filt = df[(df.year==yr) & (df.department.isin(dept_filter)) & (df.severity.isin(sev_filter))]
    
    st.divider()
    n_filt = len(filt)
    st.markdown(f"""<div style="font-size:12px;padding:4px 0;">
        <div style="color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Filtered View</div>
        <div style="display:flex;justify-content:space-between;margin:4px 0;"><span>Records</span><span style="font-weight:600;color:#f1f5f9!important;">{n_filt}</span></div>
        <div style="display:flex;justify-content:space-between;margin:4px 0;"><span>High+Critical</span><span style="font-weight:600;color:#fca5a5!important;">{(filt.severity>=3).sum()}</span></div>
        <div style="display:flex;justify-content:space-between;margin:4px 0;"><span>Total Loss</span><span style="font-weight:600;color:#fdba74!important;">${filt.financial_impact.sum()/1e6:.1f}M</span></div>
    </div>""",unsafe_allow_html=True)
    
    st.divider()
    st.markdown("""<div style="font-size:11px;color:#64748b;line-height:1.6;">
        <strong style="color:#94a3b8!important;">PoC Context</strong><br>
        Risk intelligence dashboard supporting audit planning, fieldwork, and continuous monitoring. Uses ML-based anomaly detection (Isolation Forest) on operational data.<br><br>
        <strong style="color:#94a3b8!important;">Portfolio by</strong><br>Yayan Puji Riyanto<br>PhD Candidate \u2014 Monash University
    </div>""",unsafe_allow_html=True)

# ═══ TABS ═══
tab1,tab2,tab3,tab4,tab5 = st.tabs(["\U0001f4ca KRI Monitoring","\U0001f6a8 Anomaly Detection","\U0001f50d Audit Planning","\U0001f4c8 Trend Analysis","\U0001f4d6 About"])

# ═══ TAB 1: KRI MONITORING ═══
with tab1:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Key Risk Indicator Monitoring</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Real-time KRI tracking with automated threshold breach detection</p>""",unsafe_allow_html=True)

    # Summary metrics
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    avg_res = filt.resolution_days.mean()
    with c1: mc("Incidents",f"{n_filt}",f"Year {yr}")
    with c2: mc("High/Critical",f"{(filt.severity>=3).sum()}",f"{(filt.severity>=3).mean():.0%} of total")
    with c3: mc("Financial Loss",f"${filt.financial_impact.sum()/1e6:.1f}M","Total reported")
    with c4: mc("Avg Resolution",f"{avg_res:.0f}d","Days to close")
    with c5: mc("Max Single Loss",f"${filt.financial_impact.max()/1e6:.1f}M","Largest incident")
    with c6: mc("Departments",f"{filt.department.nunique()}","With incidents")

    # KRI dashboard with thresholds
    st.markdown('<div class="sh">\U0001f4ca Monthly KRI Dashboard</div>',unsafe_allow_html=True)
    
    monthly = filt.groupby("month").agg(
        incidents=("severity","count"), high_crit=("severity",lambda x:(x>=3).sum()),
        total_loss=("financial_impact","sum"), avg_res=("resolution_days","mean")
    ).reset_index()
    
    THRESHOLDS = {"incidents":{"amber":18,"red":25},"high_crit":{"amber":4,"red":7},
                  "total_loss":{"amber":300000,"red":700000},"avg_res":{"amber":30,"red":45}}
    
    fig = go.Figure()
    metrics_kri = [("incidents","Total Incidents","#2563eb"),("high_crit","High+Critical","#dc2626"),
                   ("total_loss","Financial Loss (USD)","#d97706"),("avg_res","Avg Resolution (days)","#7c3aed")]
    
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2,cols=2,subplot_titles=[m[1] for m in metrics_kri],vertical_spacing=.12,horizontal_spacing=.08)
    
    for idx,(key,title,color) in enumerate(metrics_kri):
        r,c = idx//2+1, idx%2+1
        thresh = THRESHOLDS[key]
        vals = monthly[key].fillna(0)
        bar_colors = [("#dc2626" if v>=thresh["red"] else "#d97706" if v>=thresh["amber"] else color) for v in vals]
        fig.add_trace(go.Bar(x=monthly.month,y=vals,marker_color=bar_colors,showlegend=False,
            hovertemplate=f"{title}: %{{y:,.0f}}<extra></extra>"),row=r,col=c)
        fig.add_hline(y=thresh["amber"],line_dash="dash",line_color="#d97706",opacity=.5,row=r,col=c)
        fig.add_hline(y=thresh["red"],line_dash="dash",line_color="#dc2626",opacity=.5,row=r,col=c)
    
    fig.update_layout(height=750,margin=dict(t=40,b=30),plot_bgcolor="white",showlegend=False)
    fig.update_yaxes(gridcolor="#f1f5f9")
    fig.update_xaxes(tickangle=45,tickfont=dict(size=8))
    st.plotly_chart(fig,use_container_width=True)
    
    # Automated alerts
    st.markdown('<div class="sh">\U0001f6a8 Automated Alerts (Latest Month)</div>',unsafe_allow_html=True)
    if not monthly.empty:
        latest = monthly.iloc[-1]
        for key,title,_ in metrics_kri:
            thresh = THRESHOLDS[key]
            val = latest[key]
            if val >= thresh["red"]:
                st.markdown(f'<div class="alert-card alert-red">\U0001f534 <strong>RED BREACH:</strong> {title} = {val:,.0f} (threshold: {thresh["red"]:,})</div>',unsafe_allow_html=True)
            elif val >= thresh["amber"]:
                st.markdown(f'<div class="alert-card alert-amber">\U0001f7e1 <strong>AMBER WARNING:</strong> {title} = {val:,.0f} (threshold: {thresh["amber"]:,})</div>',unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-card alert-green">\U0001f7e2 <strong>Within Appetite:</strong> {title} = {val:,.0f} (threshold: {thresh["amber"]:,})</div>',unsafe_allow_html=True)

# ═══ TAB 2: ANOMALY DETECTION ═══
with tab2:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">ML-Powered Anomaly Detection</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Isolation Forest algorithm identifies unusual patterns for auditor review</p>""",unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        <strong>How it works:</strong> An Isolation Forest model analyses transaction amounts, transaction counts,
        and financial impact simultaneously. Data points that are "easy to isolate" (far from normal patterns)
        are flagged as anomalies. Auditors review flagged items \u2014 the AI <strong>assists</strong> but does not
        make audit decisions.
    </div>""",unsafe_allow_html=True)

    # ML parameters
    mc1,mc2 = st.columns([1,3])
    with mc1:
        contamination = st.slider("Anomaly Sensitivity",0.01,0.15,0.05,0.01,
            help="Expected proportion of anomalies (lower = fewer flags, higher confidence)")
        n_estimators = st.slider("Model Trees",50,300,100,50)
        
        if st.button("Run Anomaly Detection",type="primary",use_container_width=True):
            st.session_state.run_anomaly = True
    
    with mc2:
        if st.session_state.get("run_anomaly"):
            with st.spinner("Running Isolation Forest..."):
                features = filt[["tx_amount","tx_count","financial_impact"]].copy()
                scaler = StandardScaler()
                X = scaler.fit_transform(features)
                
                model = IsolationForest(contamination=contamination, n_estimators=n_estimators, random_state=42)
                model.fit(X)
                filt_copy = filt.copy()
                filt_copy["anomaly_score"] = model.decision_function(X)
                filt_copy["is_anomaly"] = model.predict(X) == -1
                
                anomalies = filt_copy[filt_copy.is_anomaly].sort_values("anomaly_score")
                normal = filt_copy[~filt_copy.is_anomaly]
                
                st.session_state.anomaly_results = {"anomalies":anomalies,"normal":normal,"total":len(filt_copy)}
        
        if "anomaly_results" in st.session_state:
            res = st.session_state.anomaly_results
            anom = res["anomalies"]
            norm = res["normal"]
            
            a1,a2,a3 = st.columns(3)
            with a1: mc("Anomalies Detected",f"{len(anom)}",f"{len(anom)/res['total']:.1%} of transactions")
            with a2: mc("Anomaly Loss",f"${anom.financial_impact.sum()/1e6:.1f}M","Flagged items total")
            with a3: mc("Avg Anomaly Score",f"{anom.anomaly_score.mean():.3f}","Lower = more anomalous")
            
            # Scatter plot
            fig_anom = go.Figure()
            fig_anom.add_trace(go.Scatter(x=norm.tx_amount,y=norm.financial_impact,mode="markers",name="Normal",
                marker=dict(size=5,color="#2563eb",opacity=.3),hovertemplate="Amount: $%{x:,.0f}<br>Loss: $%{y:,.0f}<extra>Normal</extra>"))
            fig_anom.add_trace(go.Scatter(x=anom.tx_amount,y=anom.financial_impact,mode="markers",name="Anomaly",
                marker=dict(size=10,color="#dc2626",symbol="x",line=dict(width=2,color="white")),
                hovertemplate="Amount: $%{x:,.0f}<br>Loss: $%{y:,.0f}<br>Dept: %{text}<br>Score: %{customdata:.3f}<extra>ANOMALY</extra>",
                text=anom.department,customdata=anom.anomaly_score))
            fig_anom.update_layout(title="Transaction Amount vs Financial Impact (Anomalies Highlighted)",
                xaxis=dict(title="Transaction Amount (USD)",type="log"),yaxis=dict(title="Financial Impact (USD)",type="log"),
                height=400,margin=dict(t=40,b=30),plot_bgcolor="white",
                legend=dict(orientation="h",y=1.08,x=.5,xanchor="center"))
            st.plotly_chart(fig_anom,use_container_width=True)
            
            # Anomaly table
            st.markdown('<div class="sh">\U0001f6a9 Flagged Items for Auditor Review</div>',unsafe_allow_html=True)
            display_anom = anom[["date","department","incident_type","severity_label","tx_amount","financial_impact","anomaly_score"]].copy()
            display_anom["tx_amount"] = display_anom["tx_amount"].apply(lambda x:f"${x:,.0f}")
            display_anom["financial_impact"] = display_anom["financial_impact"].apply(lambda x:f"${x:,.0f}")
            display_anom["anomaly_score"] = display_anom["anomaly_score"].apply(lambda x:f"{x:.3f}")
            display_anom["date"] = display_anom["date"].dt.strftime("%Y-%m-%d")
            display_anom.columns = ["Date","Department","Type","Severity","Tx Amount","Loss","Score"]
            st.dataframe(display_anom.head(20),use_container_width=True,hide_index=True,height=400)
        else:
            st.info("Click 'Run Anomaly Detection' to analyse the data.")

# ═══ TAB 3: AUDIT PLANNING ═══
with tab3:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Audit Planning Intelligence</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Data-driven audit universe prioritisation and resource allocation</p>""",unsafe_allow_html=True)

    st.markdown("""<div class="ib">
        The dashboard calculates a <strong>composite risk score</strong> per department using weighted factors:
        incident frequency (20%), severity concentration (30%), financial exposure (25%), and resolution efficiency (25%).
        This supports the annual audit planning process by identifying which areas warrant priority attention.
    </div>""",unsafe_allow_html=True)

    # Department risk scorecard
    st.markdown('<div class="sh">\U0001f3af Department Risk Scorecard</div>',unsafe_allow_html=True)
    
    dept_sc = filt.groupby("department").agg(
        total=("severity","count"), high_crit=("severity",lambda x:(x>=3).sum()),
        pct_high=("severity",lambda x:(x>=3).mean()), total_loss=("financial_impact","sum"),
        avg_loss=("financial_impact","mean"), avg_res=("resolution_days","mean"),
        max_sev=("severity","max"),
    ).round(2)
    
    # Normalise for composite score
    for col in ["total","pct_high","total_loss","avg_res"]:
        mn,mx = dept_sc[col].min(), dept_sc[col].max()
        dept_sc[f"{col}_n"] = (dept_sc[col]-mn)/(mx-mn) if mx>mn else 0
    
    dept_sc["risk_score"] = (dept_sc.total_n*.20 + dept_sc.pct_high_n*.30 + dept_sc.total_loss_n*.25 + dept_sc.avg_res_n*.25).round(3)
    dept_sc = dept_sc.sort_values("risk_score",ascending=False)
    
    # Priority classification
    dept_sc["priority"] = dept_sc.risk_score.apply(lambda x:"Critical" if x>.7 else "High" if x>.4 else "Medium" if x>.2 else "Low")
    pri_colors = {"Critical":"#dc2626","High":"#ea580c","Medium":"#eab308","Low":"#22c55e"}
    
    dc1,dc2 = st.columns([2,3])
    with dc1:
        fig_score = go.Figure(go.Bar(
            y=dept_sc.index, x=dept_sc.risk_score, orientation="h",
            marker_color=[pri_colors[p] for p in dept_sc.priority],
            text=[f"{s:.2f} ({p})" for s,p in zip(dept_sc.risk_score,dept_sc.priority)],
            textposition="auto", textfont=dict(size=10)))
        fig_score.add_vline(x=.7,line_dash="dash",line_color="#dc2626",opacity=.4)
        fig_score.add_vline(x=.4,line_dash="dash",line_color="#ea580c",opacity=.4)
        fig_score.update_layout(title="Composite Risk Score by Department",title_font_size=14,
            height=350,margin=dict(t=40,b=20,l=10,r=10),plot_bgcolor="white",xaxis=dict(title="Risk Score (0-1)"))
        fig_score.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_score,use_container_width=True)
    
    with dc2:
        # Suggested audit plan
        st.markdown("#### Suggested Annual Audit Plan")
        for dept in dept_sc.index:
            row = dept_sc.loc[dept]
            pri = row.priority
            color = pri_colors[pri]
            freq = {"Critical":"Quarterly","High":"Semi-annual","Medium":"Annual","Low":"Biennial"}[pri]
            hours = {"Critical":"120-160h","High":"80-120h","Medium":"40-80h","Low":"20-40h"}[pri]
            st.markdown(f"""<div style="background:white;border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin:5px 0;border-left:4px solid {color};">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div><span style="font-weight:600;color:#0f172a;">{dept}</span>
                        <span style="background:{color};color:white;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;margin-left:8px;">{pri}</span></div>
                    <div style="font-size:12px;color:#64748b;">Frequency: <strong>{freq}</strong> | Budget: <strong>{hours}</strong></div>
                </div>
                <div style="font-size:12px;color:#64748b;margin-top:4px;">Incidents: {int(row.total)} | High/Crit: {row.pct_high:.0%} | Exposure: ${row.total_loss:,.0f} | Avg Resolution: {row.avg_res:.0f}d</div>
            </div>""",unsafe_allow_html=True)

    # Risk concentration heatmap
    st.markdown('<div class="sh">\U0001f5fa\ufe0f Risk Concentration: Department x Category</div>',unsafe_allow_html=True)
    pivot = filt.pivot_table(values="financial_impact",index="department",columns="category",aggfunc="sum",fill_value=0)
    fig_heat = px.imshow(pivot, color_continuous_scale="RdYlGn_r", aspect="auto",
        labels=dict(x="Risk Category",y="Department",color="Financial Loss (USD)"))
    fig_heat.update_layout(height=350,margin=dict(t=20,b=20))
    st.plotly_chart(fig_heat,use_container_width=True)

# ═══ TAB 4: TREND ANALYSIS ═══
with tab4:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">Trend Analysis</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Historical patterns, seasonality, and emerging risk identification</p>""",unsafe_allow_html=True)

    # Multi-year trend
    all_monthly = df.groupby("month").agg(incidents=("severity","count"),high_crit=("severity",lambda x:(x>=3).sum()),
        loss=("financial_impact","sum")).reset_index()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=all_monthly.month,y=all_monthly.incidents,mode="lines+markers",name="All Incidents",
        line=dict(color="#2563eb",width=2),marker=dict(size=4)))
    fig_trend.add_trace(go.Scatter(x=all_monthly.month,y=all_monthly.high_crit,mode="lines+markers",name="High/Critical",
        line=dict(color="#dc2626",width=2),marker=dict(size=4)))
    # Moving average
    if len(all_monthly)>3:
        fig_trend.add_trace(go.Scatter(x=all_monthly.month,y=all_monthly.incidents.rolling(3).mean(),mode="lines",
            name="3-Month MA",line=dict(color="#94a3b8",width=1.5,dash="dash")))
    fig_trend.update_layout(title="Incident Volume Trend (2022-2024)",title_font_size=14,height=350,
        margin=dict(t=40,b=40),plot_bgcolor="white",yaxis_gridcolor="#f1f5f9",xaxis=dict(tickangle=45,tickfont=dict(size=8)),
        legend=dict(orientation="h",y=1.08,x=.5,xanchor="center"))
    st.plotly_chart(fig_trend,use_container_width=True)

    t1,t2 = st.columns(2)
    with t1:
        # Category evolution
        cat_q = df.groupby(["quarter","category"]).size().unstack(fill_value=0)
        fig_cat = px.bar(cat_q,barmode="stack",title="Risk Category Evolution (Quarterly)",
            color_discrete_sequence=["#dc2626","#ea580c","#d97706","#2563eb","#7c3aed","#059669","#475569"])
        fig_cat.update_layout(height=300,margin=dict(t=40,b=30),plot_bgcolor="white",
            legend=dict(orientation="h",y=-.15,font=dict(size=9)),xaxis=dict(tickfont=dict(size=8)))
        st.plotly_chart(fig_cat,use_container_width=True)
    
    with t2:
        # Root cause pareto
        type_counts = filt.incident_type.value_counts().head(10)
        cum_pct = type_counts.cumsum()/type_counts.sum()*100
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=type_counts.index,y=type_counts.values,marker_color="#2563eb",name="Count"))
        fig_pareto.add_trace(go.Scatter(x=type_counts.index,y=cum_pct.values,mode="lines+markers",
            name="Cumulative %",yaxis="y2",line=dict(color="#dc2626",width=2),marker=dict(size=5)))
        fig_pareto.update_layout(title="Top 10 Incident Types (Pareto)",title_font_size=14,height=300,
            margin=dict(t=40,b=80),plot_bgcolor="white",xaxis=dict(tickangle=45,tickfont=dict(size=8)),
            yaxis2=dict(overlaying="y",side="right",range=[0,105],title="Cumulative %"),
            legend=dict(orientation="h",y=1.08),showlegend=True)
        st.plotly_chart(fig_pareto,use_container_width=True)

    # Z-score anomaly in time series
    st.markdown('<div class="sh">\U0001f4c9 Statistical Anomaly Detection (Time Series)</div>',unsafe_allow_html=True)
    all_monthly["z_score"] = (all_monthly.incidents - all_monthly.incidents.mean()) / all_monthly.incidents.std()
    ts_anomalies = all_monthly[all_monthly.z_score.abs()>1.5]
    
    fig_z = go.Figure()
    fig_z.add_trace(go.Scatter(x=all_monthly.month,y=all_monthly.incidents,mode="lines+markers",name="Incidents",
        line=dict(color="#2563eb",width=2),marker=dict(size=4)))
    mean_val = all_monthly.incidents.mean()
    std_val = all_monthly.incidents.std()
    fig_z.add_hrect(y0=mean_val-1.5*std_val,y1=mean_val+1.5*std_val,fillcolor="#2563eb",opacity=.06,line_width=0)
    fig_z.add_hline(y=mean_val,line_dash="dash",line_color="#94a3b8",opacity=.5)
    for _,row in ts_anomalies.iterrows():
        fig_z.add_trace(go.Scatter(x=[row.month],y=[row.incidents],mode="markers",showlegend=False,
            marker=dict(size=14,color="#dc2626",symbol="diamond",line=dict(width=2,color="white")),
            hovertemplate=f"Month: {row.month}<br>Incidents: {row.incidents:.0f}<br>Z-score: {row.z_score:.2f}<extra>ANOMALY</extra>"))
    fig_z.update_layout(title=f"Anomalous Months (|Z| > 1.5) \u2014 {len(ts_anomalies)} detected",
        title_font_size=14,height=300,margin=dict(t=40,b=40),plot_bgcolor="white",
        xaxis=dict(tickangle=45,tickfont=dict(size=8)),yaxis_gridcolor="#f1f5f9")
    st.plotly_chart(fig_z,use_container_width=True)

# ═══ TAB 5: ABOUT ═══
with tab5:
    st.markdown("""<h1 style="font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;">About This PoC</h1>
        <p style="font-size:15px;color:#64748b;margin-top:0;">Architecture, methodology, and AIIB context</p>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">\U0001f3db\ufe0f AIIB IAO Context</div>',unsafe_allow_html=True)
    st.markdown("""<div class="ib">
        This Risk Intelligence Dashboard is one of three PoC options for AIIB IAO, addressing:
        <em>"Design dashboard/interface visualizing key indicators, anomalies, trends, and alerts,
        supporting audit planning, fieldwork, and continuous monitoring."</em>
        It demonstrates how data analytics and ML can enhance internal audit effectiveness.
    </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">\U0001f527 Technical Stack</div>',unsafe_allow_html=True)
    a1,a2=st.columns(2)
    with a1:
        st.markdown("""<div class="fc"><h4>Components</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Frontend:</strong> Streamlit + Plotly</li>
            <li><strong>ML Engine:</strong> scikit-learn (Isolation Forest)</li>
            <li><strong>Statistics:</strong> Z-score anomaly detection, trend analysis</li>
            <li><strong>Data:</strong> 600 synthetic operational risk events (3 years)</li>
        </ul></div>""",unsafe_allow_html=True)
    with a2:
        st.markdown("""<div class="fc"><h4>ML Methodology</h4>
        <ul style="font-size:13px;color:#475569;line-height:1.8;">
            <li><strong>Algorithm:</strong> Isolation Forest (unsupervised)</li>
            <li><strong>Features:</strong> Transaction amount, count, financial impact</li>
            <li><strong>Why IF:</strong> Works well with high-dimensional data, no labeled training data required \u2014 ideal for audit where anomalies are rare and unlabeled</li>
            <li><strong>Output:</strong> Anomaly score + binary flag for auditor review</li>
        </ul></div>""",unsafe_allow_html=True)

    st.markdown('<div class="sh">\U0001f3db\ufe0f JD Mapping</div>',unsafe_allow_html=True)
    r1,r2,r3=st.columns(3)
    with r1:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f4ca</div>
            <h4 style="color:#1e40af;margin-top:0;">KRI Monitoring</h4>
            <p style="font-size:13px;color:#334155;">Real-time threshold breach detection with automated alerts \u2014 supports continuous monitoring.</p></div>""",unsafe_allow_html=True)
    with r2:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f916</div>
            <h4 style="color:#1e40af;margin-top:0;">ML Anomaly Detection</h4>
            <p style="font-size:13px;color:#334155;">Isolation Forest flags unusual transactions for auditor review \u2014 supports fieldwork.</p></div>""",unsafe_allow_html=True)
    with r3:
        st.markdown("""<div class="aiib-card"><div style="font-size:24px;margin-bottom:6px;">\U0001f3af</div>
            <h4 style="color:#1e40af;margin-top:0;">Audit Planning</h4>
            <p style="font-size:13px;color:#334155;">Data-driven department risk scoring and resource allocation \u2014 supports audit planning.</p></div>""",unsafe_allow_html=True)

# FOOTER
st.divider()
st.markdown("""<div style="text-align:center;color:#94a3b8;font-size:12px;padding:8px 0 16px;line-height:1.8;">
    Risk Intelligence Dashboard & Audit Assistance Interface \u2014 PoC Prototype<br>
    Portfolio by <strong>Yayan Puji Riyanto</strong> \u00b7 PhD Candidate, Monash University \u00b7 MS Business Analytics, CU Boulder<br>
    <em>Prepared for AIIB AI Audit Practices Intern</em>
</div>""",unsafe_allow_html=True)
