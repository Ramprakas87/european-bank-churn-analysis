import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ECB | Customer Churn Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0e1a; color: #e2e8f0; }
section[data-testid="stSidebar"] { background: #0f1424 !important; border-right: 1px solid #1e2a40; }
section[data-testid="stSidebar"] .stMarkdown h2 { color: #60a5fa; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; padding-top: 0.5rem; }
.kpi-card { background: linear-gradient(135deg, #111827 0%, #1a2235 100%); border: 1px solid #1e2a40; border-radius: 12px; padding: 20px 24px; position: relative; overflow: hidden; margin-bottom: 4px; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: var(--accent); }
.kpi-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #64748b; margin-bottom: 6px; }
.kpi-value { font-size: 2.1rem; font-weight: 700; color: var(--accent); line-height: 1; font-family: 'DM Mono', monospace; }
.kpi-sub { font-size: 0.78rem; color: #64748b; margin-top: 6px; }
.section-header { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #475569; border-bottom: 1px solid #1e2a40; padding-bottom: 10px; margin: 28px 0 16px 0; }
.insight-box { background: #0f1930; border-left: 3px solid #3b82f6; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 8px 0; font-size: 0.87rem; color: #94a3b8; line-height: 1.6; }
.insight-box strong { color: #e2e8f0; }
.alert-box { background: #1a0f0f; border-left: 3px solid #ef4444; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 8px 0; font-size: 0.87rem; color: #94a3b8; }
.alert-box strong { color: #fca5a5; }
.warn-box { background: #1a1400; border-left: 3px solid #f59e0b; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 8px 0; font-size: 0.87rem; color: #94a3b8; }
.warn-box strong { color: #fcd34d; }
.page-title { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-subtitle { font-size: 0.85rem; color: #475569; margin-top: 2px; }
.ecb-badge { display: inline-block; background: #1e3a5f; color: #60a5fa; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 10px; border-radius: 4px; margin-bottom: 8px; }
.valid-pass { background: #0f2a1a; border-left: 3px solid #10b981; border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 6px 0; font-size: 0.83rem; color: #6ee7b7; }
.valid-warn { background: #1a1400; border-left: 3px solid #f59e0b; border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 6px 0; font-size: 0.83rem; color: #fcd34d; }
.valid-fail { background: #1a0f0f; border-left: 3px solid #ef4444; border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 6px 0; font-size: 0.83rem; color: #fca5a5; }
.traffic-card { border-radius: 10px; padding: 16px 20px; text-align: center; margin-bottom: 6px; }
.traffic-label { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.traffic-value { font-size: 1.8rem; font-weight: 700; font-family: 'DM Mono', monospace; }
.traffic-sub { font-size: 0.75rem; margin-top: 4px; opacity: 0.8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#94a3b8", size=12),
    title_font=dict(family="DM Sans", color="#e2e8f0", size=14),
    margin=dict(t=40, b=40, l=40, r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    colorway=["#3b82f6","#f59e0b","#10b981","#ef4444","#8b5cf6","#06b6d4"],
)
GEO_COLORS = {"France": "#3b82f6", "Germany": "#f59e0b", "Spain": "#10b981"}


@st.cache_data
def load_data():
    df = pd.read_csv("European_Bank__1_.csv")
    validation_results = []

    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls == 0:
        validation_results.append(("pass", f"No missing values found across all {len(df.columns)} columns."))
    else:
        cols_with_nulls = null_counts[null_counts > 0].to_dict()
        validation_results.append(("warn", f"Missing values detected: {cols_with_nulls}"))

    dup_ids = df["CustomerId"].duplicated().sum()
    if dup_ids == 0:
        validation_results.append(("pass", f"No duplicate CustomerIds found. All {len(df):,} records are unique."))
    else:
        validation_results.append(("fail", f"{dup_ids:,} duplicate CustomerIds detected."))

    binary_cols = {"HasCrCard": [0, 1], "IsActiveMember": [0, 1], "Exited": [0, 1]}
    for col, expected in binary_cols.items():
        unique_vals = sorted(df[col].unique().tolist())
        if unique_vals == expected:
            validation_results.append(("pass", f"'{col}' contains only valid binary values {expected}."))
        else:
            validation_results.append(("fail", f"'{col}' has unexpected values: {unique_vals}"))

    cr = df["Exited"].mean() * 100
    if 5 <= cr <= 50:
        validation_results.append(("pass", f"Churn label distribution is realistic: {cr:.1f}% churn rate."))
    else:
        validation_results.append(("warn", f"Churn rate of {cr:.1f}% is outside expected 5-50% range."))

    valid_geos = {"France", "Germany", "Spain"}
    actual_geos = set(df["Geography"].unique())
    if actual_geos == valid_geos:
        validation_results.append(("pass", f"Geography values are valid: {sorted(actual_geos)}."))
    else:
        validation_results.append(("warn", f"Unexpected geography values found: {actual_geos - valid_geos}"))

    age_outliers = df[(df["Age"] < 18) | (df["Age"] > 100)].shape[0]
    if age_outliers == 0:
        validation_results.append(("pass", "All age values are within the realistic range of 18-100."))
    else:
        validation_results.append(("warn", f"{age_outliers} customers have ages outside 18-100."))

    cs_outliers = df[(df["CreditScore"] < 300) | (df["CreditScore"] > 850)].shape[0]
    if cs_outliers == 0:
        validation_results.append(("pass", "All credit scores are within the valid 300-850 range."))
    else:
        validation_results.append(("warn", f"{cs_outliers} credit scores are outside 300-850."))

    df.drop(columns=["Surname"], errors="ignore", inplace=True)

    df["AgeGroup"]       = pd.cut(df["Age"], bins=[0,29,45,60,120], labels=["<30","30-45","46-60","60+"])
    df["CreditBand"]     = pd.cut(df["CreditScore"], bins=[0,579,719,850], labels=["Low (<580)","Medium (580-719)","High (720+)"])
    df["TenureGroup"]    = pd.cut(df["Tenure"], bins=[-1,2,6,100], labels=["New (0-2y)","Mid-term (3-6y)","Long-term (7y+)"])
    df["BalanceSegment"] = pd.cut(df["Balance"], bins=[-1,0,100000,1e9], labels=["Zero Balance","Low (1-100K)","High (100K+)"])
    df["SalaryBand"]     = pd.cut(df["EstimatedSalary"], bins=[0,50000,100000,150000,200000], labels=["<50K","50K-100K","100K-150K","150K+"])
    df["IsHighValue"]    = ((df["Balance"] > df["Balance"].quantile(0.75)) & (df["EstimatedSalary"] > df["EstimatedSalary"].quantile(0.75))).astype(int)
    df["ChurnLabel"]     = df["Exited"].map({1:"Churned", 0:"Retained"})
    df["CrCardLabel"]    = df["HasCrCard"].map({1:"Has Card", 0:"No Card"})
    df["ActiveLabel"]    = df["IsActiveMember"].map({1:"Active", 0:"Inactive"})

    return df, validation_results


df_full, validation_results = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="ecb-badge">ECB Analytics</div>', unsafe_allow_html=True)
    st.markdown("## Filters")
    geo_sel    = st.selectbox("Geography", ["All"] + sorted(df_full["Geography"].unique()))
    gender_sel = st.selectbox("Gender", ["All", "Male", "Female"])
    age_sel    = st.multiselect("Age Groups", ["<30","30-45","46-60","60+"], default=["<30","30-45","46-60","60+"])
    credit_sel = st.multiselect("Credit Band", ["Low (<580)","Medium (580-719)","High (720+)"], default=["Low (<580)","Medium (580-719)","High (720+)"])
    active_sel = st.radio("Member Status", ["All","Active","Inactive"])
    crcard_sel = st.radio("Credit Card", ["All","Has Card","No Card"])
    st.markdown("---")
    st.markdown("## Module")
    module = st.radio("View", [
        "📊  Overview",
        "🚦  PM Dashboard",
        "🔍  Data Validation & EDA",
        "🌍  Geographic",
        "👥  Demographics",
        "💰  Financial Profile",
        "💵  Salary Analysis",
        "⭐  High-Value Customers",
        "📋  Executive Summary",
    ])
    module = module.split("  ")[1]

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_full.copy()
if geo_sel != "All":           df = df[df["Geography"] == geo_sel]
if gender_sel != "All":        df = df[df["Gender"] == gender_sel]
if age_sel:                    df = df[df["AgeGroup"].isin(age_sel)]
if credit_sel:                 df = df[df["CreditBand"].isin(credit_sel)]
if active_sel == "Active":     df = df[df["IsActiveMember"] == 1]
elif active_sel == "Inactive": df = df[df["IsActiveMember"] == 0]
if crcard_sel != "All":        df = df[df["CrCardLabel"] == crcard_sel]

# ── Helpers ───────────────────────────────────────────────────────────────────
def churn_rate(data):
    return data["Exited"].mean() * 100 if len(data) > 0 else 0

def kpi_card(label, value, sub, accent="#3b82f6"):
    st.markdown(
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div></div>',
        unsafe_allow_html=True)

def traffic_light(label, value, sub, level):
    # level: "green" / "yellow" / "red"
    bg   = {"green":"#0f2a1a","yellow":"#1a1400","red":"#1a0f0f"}[level]
    col  = {"green":"#10b981","yellow":"#f59e0b","red":"#ef4444"}[level]
    icon = {"green":"▲","yellow":"●","red":"▼"}[level]
    st.markdown(
        f'<div class="traffic-card" style="background:{bg};border:1px solid {col}33">'
        f'<div class="traffic-label" style="color:{col}">{icon} {label}</div>'
        f'<div class="traffic-value" style="color:{col}">{value}</div>'
        f'<div class="traffic-sub" style="color:{col}">{sub}</div></div>',
        unsafe_allow_html=True)

def churn_rate_bar(data, col, title):
    grp = data.groupby(col, observed=True).agg(Total=("Exited","count"), Churned=("Exited","sum")).reset_index()
    grp["ChurnRate"] = (grp["Churned"] / grp["Total"] * 100).round(1)
    grp = grp.sort_values("ChurnRate", ascending=True)
    fig = go.Figure(go.Bar(
        x=grp["ChurnRate"], y=grp[col].astype(str), orientation="h",
        marker=dict(color=grp["ChurnRate"], colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#ef4444"]], showscale=False),
        text=[f"{v:.1f}%" for v in grp["ChurnRate"]], textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
        hovertemplate="<b>%{y}</b><br>Churn Rate: %{x:.1f}%<br>Total: %{customdata[0]}<br>Churned: %{customdata[1]}<extra></extra>",
        customdata=grp[["Total","Churned"]].values))
    fig.update_layout(**PLOT_LAYOUT, title=title,
        xaxis=dict(gridcolor="#1e2a40", title="Churn Rate (%)", range=[0, grp["ChurnRate"].max()*1.3]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        height=max(250, len(grp)*60+80))
    return fig

def contribution_pie(data, col, title):
    grp = data[data["Exited"]==1].groupby(col, observed=True).size().reset_index(name="Churned")
    fig = go.Figure(go.Pie(
        labels=grp[col].astype(str), values=grp["Churned"], hole=0.55,
        marker=dict(colors=["#3b82f6","#f59e0b","#10b981","#ef4444","#8b5cf6"], line=dict(color="#0a0e1a",width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Churned: %{value}<br>Share: %{percent}<extra></extra>"))
    fig.update_layout(**PLOT_LAYOUT, title=title, showlegend=False, height=320)
    return fig

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="ecb-badge">European Central Bank | Commissioned Analytics</div>'
    f'<div class="page-title">Customer Churn Pattern Analytics</div>'
    f'<div class="page-subtitle">European Retail Banking &nbsp;·&nbsp; '
    f'{len(df):,} customers in view &nbsp;·&nbsp; {churn_rate(df):.1f}% churn rate</div>',
    unsafe_allow_html=True)
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# =============================================================================
# MODULE 1 — OVERVIEW
# =============================================================================
if module == "Overview":
    total       = len(df)
    n_churned   = int(df["Exited"].sum())
    rate        = churn_rate(df)
    hv_rate     = churn_rate(df[df["IsHighValue"]==1])
    inactive_cr = churn_rate(df[df["IsActiveMember"]==0])
    active_cr   = churn_rate(df[df["IsActiveMember"]==1])
    eng_drop    = inactive_cr - active_cr
    geo_risk    = df.groupby("Geography", observed=True).apply(lambda x: x["Exited"].mean()*100).max()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi_card("Total Customers",    f"{total:,}",        f"{n_churned:,} exited",                                   "#3b82f6")
    with c2: kpi_card("Overall Churn Rate", f"{rate:.1f}%",      "Baseline: 20.4%",                                         "#f59e0b")
    with c3: kpi_card("High-Value Churn",   f"{hv_rate:.1f}%",   "Top-quartile segment",                                    "#ef4444")
    with c4: kpi_card("Geographic Risk",    f"{geo_risk:.1f}%",  "Highest country churn",                                   "#8b5cf6")
    with c5: kpi_card("Engagement Drop",    f"{eng_drop:.1f}pp", f"Inactive {inactive_cr:.1f}% vs Active {active_cr:.1f}%", "#f472b6")
    with c6: kpi_card("Retained",           f"{100-rate:.1f}%",  f"{total-n_churned:,} customers",                          "#10b981")

    st.markdown("<div class='section-header'>Churn Composition</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1,2])
    with col_a:
        fig = go.Figure(go.Pie(
            values=[total-n_churned, n_churned], labels=["Retained","Churned"], hole=0.72,
            marker=dict(colors=["#1e3a5f","#ef4444"], line=dict(color="#0a0e1a",width=3)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>"))
        fig.add_annotation(text=f"<b>{rate:.1f}%</b>", font=dict(size=28,color="#ef4444",family="DM Mono"), showarrow=False, x=0.5, y=0.52)
        fig.add_annotation(text="Churn Rate", font=dict(size=11,color="#64748b"), showarrow=False, x=0.5, y=0.38)
        fig.update_layout(**PLOT_LAYOUT, title="Overall Churn", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        geo_grp = df.groupby("Geography", observed=True).agg(Total=("Exited","count"), Churned=("Exited","sum")).reset_index()
        geo_grp["ChurnRate"] = geo_grp["Churned"] / geo_grp["Total"] * 100
        fig2 = go.Figure()
        for _, row in geo_grp.iterrows():
            c = GEO_COLORS.get(row["Geography"],"#3b82f6")
            fig2.add_trace(go.Bar(name=row["Geography"], x=[row["Geography"]], y=[row["ChurnRate"]],
                marker_color=c, text=f"{row['ChurnRate']:.1f}%", textposition="outside", textfont=dict(color=c)))
        fig2.update_layout(**PLOT_LAYOUT, title="Churn Rate by Country",
            yaxis=dict(gridcolor="#1e2a40", title="Churn Rate (%)"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False, height=300, bargap=0.45)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Segment Churn Rates</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: st.plotly_chart(churn_rate_bar(df,"AgeGroup","Churn Rate by Age Group"), use_container_width=True)
    with c2: st.plotly_chart(churn_rate_bar(df,"NumOfProducts","Churn Rate by # Products"), use_container_width=True)

    st.markdown("<div class='section-header'>Churn Contribution by Segment (% of Total Churn)</div>", unsafe_allow_html=True)
    c3,c4,c5 = st.columns(3)
    with c3: st.plotly_chart(contribution_pie(df,"AgeGroup","Contribution — Age"), use_container_width=True)
    with c4: st.plotly_chart(contribution_pie(df,"Geography","Contribution — Country"), use_container_width=True)
    with c5: st.plotly_chart(contribution_pie(df,"BalanceSegment","Contribution — Balance"), use_container_width=True)


# =============================================================================
# MODULE 2 — PM DASHBOARD (simple, visual, manager-friendly)
# =============================================================================
elif module == "PM Dashboard":
    st.markdown("<div class='section-header'>🚦 At-a-Glance: Traffic Light Status</div>", unsafe_allow_html=True)
    st.caption("Green = on track · Yellow = monitor · Red = action needed")

    rate        = churn_rate(df)
    hv_rate     = churn_rate(df[df["IsHighValue"]==1])
    inactive_cr = churn_rate(df[df["IsActiveMember"]==0])
    active_cr   = churn_rate(df[df["IsActiveMember"]==1])
    revenue_risk = df[df["Exited"]==1]["Balance"].sum() / 1e6

    tc1,tc2,tc3,tc4,tc5 = st.columns(5)
    with tc1: traffic_light("Overall Churn", f"{rate:.1f}%", "Target < 15%",
                            "red" if rate>20 else ("yellow" if rate>15 else "green"))
    with tc2: traffic_light("High-Value Churn", f"{hv_rate:.1f}%", "Target < 18%",
                            "red" if hv_rate>20 else ("yellow" if hv_rate>18 else "green"))
    with tc3: traffic_light("Inactive Members", f"{inactive_cr:.1f}%", "Churn rate of inactive",
                            "red" if inactive_cr>35 else ("yellow" if inactive_cr>25 else "green"))
    with tc4: traffic_light("Revenue at Risk", f"€{revenue_risk:.0f}M", "Churned balance total",
                            "red" if revenue_risk>50 else ("yellow" if revenue_risk>20 else "green"))
    with tc5:
        geo_rates = df.groupby("Geography", observed=True)["Exited"].mean()*100
        max_geo_rate = geo_rates.max()
        traffic_light("Worst Country", f"{max_geo_rate:.1f}%", geo_rates.idxmax(),
                      "red" if max_geo_rate>25 else ("yellow" if max_geo_rate>20 else "green"))

    # ── TOP 5 RISK SEGMENTS — ranked table ──────────────────────────────────
    st.markdown("<div class='section-header'>🏆 Top 10 Highest-Risk Segments (Ranked)</div>", unsafe_allow_html=True)
    st.caption("The segments your team should act on first, sorted by churn rate")

    seg_rows = []
    for geo in df["Geography"].dropna().unique():
        for age in df["AgeGroup"].dropna().unique():
            sub = df[(df["Geography"]==geo) & (df["AgeGroup"]==age)]
            if len(sub) >= 30:
                seg_rows.append({
                    "Segment": f"{geo} · {age}",
                    "Customers": len(sub),
                    "Churned": int(sub["Exited"].sum()),
                    "Churn Rate": round(sub["Exited"].mean()*100, 1),
                    "Revenue at Risk (EUR)": round(sub[sub["Exited"]==1]["Balance"].sum(), 0),
                })
    seg_df = pd.DataFrame(seg_rows).sort_values("Churn Rate", ascending=False).head(10).reset_index(drop=True)
    seg_df.index += 1

    fig_risk = go.Figure(go.Bar(
        x=seg_df["Churn Rate"], y=seg_df["Segment"], orientation="h",
        marker=dict(color=seg_df["Churn Rate"],
                    colorscale=[[0,"#1e4d2b"],[0.4,"#f59e0b"],[1,"#ef4444"]], showscale=False),
        text=[f"{v}%" for v in seg_df["Churn Rate"]], textposition="outside",
        textfont=dict(color="#e2e8f0", size=12),
        hovertemplate="<b>%{y}</b><br>Churn: %{x}%<extra></extra>"))
    fig_risk.update_layout(**PLOT_LAYOUT, title="Top 10 Risk Segments — Churn Rate",
        xaxis=dict(gridcolor="#1e2a40", title="Churn Rate (%)", range=[0,110]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed"),
        height=420)
    st.plotly_chart(fig_risk, use_container_width=True)

    # ── CHURN FUNNEL — how many customers we lose step by step ───────────────
    st.markdown("<div class='section-header'>📉 Churn Funnel — Where Customers Are Lost</div>", unsafe_allow_html=True)
    st.caption("Read left to right: each bar shows customers remaining after each filter")

    total       = len(df)
    active_cust = len(df[df["IsActiveMember"]==1])
    multi_prod  = len(df[df["NumOfProducts"].isin([1,2])])
    retained    = len(df[df["Exited"]==0])

    funnel_fig = go.Figure(go.Funnel(
        y=["All Customers","Active Members","1-2 Products (Stable)","Retained"],
        x=[total, active_cust, multi_prod, retained],
        textinfo="value+percent initial",
        marker=dict(color=["#3b82f6","#8b5cf6","#f59e0b","#10b981"]),
        connector=dict(line=dict(color="#1e2a40", width=1))))
    funnel_fig.update_layout(**PLOT_LAYOUT, title="Customer Retention Funnel", height=360)
    st.plotly_chart(funnel_fig, use_container_width=True)

    # ── SIDE-BY-SIDE COMPARISON: Churned vs Retained ─────────────────────────
    st.markdown("<div class='section-header'>⚖️ Who Churns vs Who Stays — Simple Comparison</div>", unsafe_allow_html=True)
    st.caption("Average profile of a churned customer vs a retained customer")

    churned_avg  = df[df["Exited"]==1][["Age","CreditScore","Tenure","Balance","EstimatedSalary","NumOfProducts"]].mean()
    retained_avg = df[df["Exited"]==0][["Age","CreditScore","Tenure","Balance","EstimatedSalary","NumOfProducts"]].mean()

    labels  = ["Avg Age","Credit Score","Tenure (yrs)","Balance (EUR)","Salary (EUR)","# Products"]
    c_vals  = [round(churned_avg["Age"],1), round(churned_avg["CreditScore"],0),
               round(churned_avg["Tenure"],1), round(churned_avg["Balance"],0),
               round(churned_avg["EstimatedSalary"],0), round(churned_avg["NumOfProducts"],1)]
    r_vals  = [round(retained_avg["Age"],1), round(retained_avg["CreditScore"],0),
               round(retained_avg["Tenure"],1), round(retained_avg["Balance"],0),
               round(retained_avg["EstimatedSalary"],0), round(retained_avg["NumOfProducts"],1)]

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(name="Churned",  x=labels, y=c_vals, marker_color="#ef4444", text=[str(v) for v in c_vals], textposition="outside"))
    fig_cmp.add_trace(go.Bar(name="Retained", x=labels, y=r_vals, marker_color="#3b82f6", text=[str(v) for v in r_vals], textposition="outside"))
    fig_cmp.update_layout(**PLOT_LAYOUT, barmode="group", title="Churned vs Retained — Average Profile",
        yaxis=dict(gridcolor="#1e2a40"), xaxis=dict(gridcolor="rgba(0,0,0,0)"), height=380)
    st.plotly_chart(fig_cmp, use_container_width=True)

    # ── WATERFALL: Revenue Impact ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>💸 Revenue Impact Waterfall — Balance Lost by Country</div>", unsafe_allow_html=True)
    st.caption("How much total balance walked out the door, broken down by country")

    geo_risk_wf = df[df["Exited"]==1].groupby("Geography", observed=True)["Balance"].sum().reset_index()
    geo_risk_wf["Balance_M"] = (geo_risk_wf["Balance"] / 1e6).round(2)
    total_risk = geo_risk_wf["Balance_M"].sum()

    wf_x      = list(geo_risk_wf["Geography"]) + ["Total Lost"]
    wf_y      = list(geo_risk_wf["Balance_M"]) + [total_risk]
    wf_measure= ["relative"] * len(geo_risk_wf) + ["total"]
    wf_colors = [GEO_COLORS.get(g,"#3b82f6") for g in geo_risk_wf["Geography"]] + ["#ef4444"]

    fig_wf = go.Figure(go.Waterfall(
        x=wf_x, y=wf_y, measure=wf_measure,
        text=[f"€{v:.1f}M" for v in wf_y], textposition="outside",
        connector=dict(line=dict(color="#1e2a40", width=1)),
        increasing=dict(marker_color="#ef4444"),
        totals=dict(marker_color="#ef4444"),
        decreasing=dict(marker_color="#10b981")))
    fig_wf.update_layout(**PLOT_LAYOUT, title="Revenue (Balance) Lost to Churn by Country (EUR M)",
        yaxis=dict(gridcolor="#1e2a40", title="EUR Millions"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"), height=380)
    st.plotly_chart(fig_wf, use_container_width=True)

    # ── RETENTION SCORE GAUGE ─────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🎯 Overall Retention Health Score</div>", unsafe_allow_html=True)
    st.caption("Composite score based on churn rate, engagement drop, and HV churn — 100 = perfect retention")

    score = max(0, round(100 - (rate * 1.5) - (max(0, hv_rate - rate) * 2) - (max(0, inactive_cr - active_cr) * 0.5), 1))
    color = "#10b981" if score >= 70 else ("#f59e0b" if score >= 50 else "#ef4444")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 70, "valueformat": ".1f"},
        gauge={
            "axis": {"range":[0,100], "tickwidth":1, "tickcolor":"#475569"},
            "bar":  {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range":[0,50],  "color":"#1a0f0f"},
                {"range":[50,70], "color":"#1a1400"},
                {"range":[70,100],"color":"#0f2a1a"},
            ],
            "threshold": {"line":{"color":"#ffffff","width":3}, "thickness":0.75, "value":70}
        },
        title={"text":"Retention Health Score<br><span style='font-size:0.8em;color:#64748b'>Target: 70+</span>",
               "font":{"color":"#e2e8f0","size":14}}))
    fig_gauge.update_layout(**PLOT_LAYOUT, height=320)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── SIMPLE ACTION TABLE ───────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📋 Quick-Win Action Priorities</div>", unsafe_allow_html=True)
    st.caption("Top actions ranked by potential impact — for your next sprint planning")

    action_data = {
        "Priority": ["🔴 #1","🔴 #2","🟡 #3","🟡 #4","🟢 #5"],
        "Action": [
            "Reactivate inactive members",
            "Retention campaign: Germany",
            "Personal outreach: 46-60 age group",
            "Review 3-4 product bundles",
            "Cross-sell to zero-balance customers",
        ],
        "Segment Churn Rate": [
            f"{inactive_cr:.1f}%",
            f"{churn_rate(df[df['Geography']=='Germany']):.1f}%",
            f"{churn_rate(df[df['AgeGroup']=='46-60']):.1f}%",
            f"{churn_rate(df[df['NumOfProducts']>=3]):.1f}%",
            f"{churn_rate(df[df['Balance']==0]):.1f}%",
        ],
        "Customers Affected": [
            f"{len(df[df['IsActiveMember']==0]):,}",
            f"{len(df[df['Geography']=='Germany']):,}",
            f"{len(df[df['AgeGroup']=='46-60']):,}",
            f"{len(df[df['NumOfProducts']>=3]):,}",
            f"{len(df[df['Balance']==0]):,}",
        ],
        "Est. Revenue at Risk": [
            f"EUR {df[(df['IsActiveMember']==0)&(df['Exited']==1)]['Balance'].sum()/1e6:.1f}M",
            f"EUR {df[(df['Geography']=='Germany')&(df['Exited']==1)]['Balance'].sum()/1e6:.1f}M",
            f"EUR {df[(df['AgeGroup']=='46-60')&(df['Exited']==1)]['Balance'].sum()/1e6:.1f}M",
            f"EUR {df[(df['NumOfProducts']>=3)&(df['Exited']==1)]['Balance'].sum()/1e6:.1f}M",
            f"EUR {df[(df['Balance']==0)&(df['Exited']==1)]['Balance'].sum()/1e6:.1f}M",
        ],
    }
    st.dataframe(pd.DataFrame(action_data), use_container_width=True, hide_index=True)


# =============================================================================
# MODULE 3 — DATA VALIDATION & EDA
# =============================================================================
elif module == "Data Validation & EDA":
    st.markdown("<div class='section-header'>Data Ingestion & Validation Report</div>", unsafe_allow_html=True)
    for status, msg in validation_results:
        css_class = {"pass":"valid-pass","warn":"valid-warn","fail":"valid-fail"}.get(status,"valid-pass")
        icon      = {"pass":"✓","warn":"⚠","fail":"✗"}.get(status,"✓")
        st.markdown(f'<div class="{css_class}"><strong>{icon}</strong> {msg}</div>', unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Dataset Overview</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Total Records",   f"{len(df_full):,}",               "Raw dataset size",            "#3b82f6")
    with c2: kpi_card("Features",        f"{len(df_full.columns)}",         "Columns in dataset",          "#10b981")
    with c3: kpi_card("Geographies",     f"{df_full['Geography'].nunique()}","France, Germany, Spain",      "#f59e0b")
    with c4: kpi_card("Churn Rate",      f"{df_full['Exited'].mean()*100:.1f}%","Target variable distribution","#ef4444")

    st.markdown("<div class='section-header'>Exploratory Data Analysis — Distributions</div>", unsafe_allow_html=True)
    ca,cb = st.columns(2)
    with ca:
        fig = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig.add_trace(go.Histogram(x=df_full[df_full["ChurnLabel"]==label]["Age"], name=label, nbinsx=30, marker_color=color, opacity=0.75))
        fig.update_layout(**PLOT_LAYOUT, barmode="overlay", title="Age Distribution: Churned vs Retained",
            xaxis=dict(gridcolor="#1e2a40",title="Age"), yaxis=dict(gridcolor="#1e2a40",title="Count"), height=300)
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        fig2 = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            sub = df_full[(df_full["ChurnLabel"]==label) & (df_full["Balance"]>0)]
            fig2.add_trace(go.Histogram(x=sub["Balance"], name=label, nbinsx=35, marker_color=color, opacity=0.7))
        fig2.update_layout(**PLOT_LAYOUT, barmode="overlay", title="Balance Distribution (excl. zero)",
            xaxis=dict(gridcolor="#1e2a40",title="Balance (EUR)"), yaxis=dict(gridcolor="#1e2a40",title="Count"), height=300)
        st.plotly_chart(fig2, use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        fig3 = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig3.add_trace(go.Histogram(x=df_full[df_full["ChurnLabel"]==label]["CreditScore"], name=label, nbinsx=30, marker_color=color, opacity=0.75))
        fig3.update_layout(**PLOT_LAYOUT, barmode="overlay", title="Credit Score Distribution",
            xaxis=dict(gridcolor="#1e2a40",title="Credit Score"), yaxis=dict(gridcolor="#1e2a40",title="Count"), height=300)
        st.plotly_chart(fig3, use_container_width=True)
    with cd:
        fig4 = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig4.add_trace(go.Histogram(x=df_full[df_full["ChurnLabel"]==label]["EstimatedSalary"], name=label, nbinsx=30, marker_color=color, opacity=0.75))
        fig4.update_layout(**PLOT_LAYOUT, barmode="overlay", title="Salary Distribution",
            xaxis=dict(gridcolor="#1e2a40",title="Estimated Salary (EUR)"), yaxis=dict(gridcolor="#1e2a40",title="Count"), height=300)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='section-header'>Descriptive Statistics — Churned vs Retained</div>", unsafe_allow_html=True)
    num_cols = ["CreditScore","Age","Tenure","Balance","NumOfProducts","EstimatedSalary"]
    churned_stats  = df_full[df_full["Exited"]==1][num_cols].describe().T.round(2)
    retained_stats = df_full[df_full["Exited"]==0][num_cols].describe().T.round(2)
    churned_stats.columns  = [f"Churned — {c}" for c in churned_stats.columns]
    retained_stats.columns = [f"Retained — {c}" for c in retained_stats.columns]
    combined = pd.concat([churned_stats[["Churned — mean","Churned — std","Churned — min","Churned — max"]],
                          retained_stats[["Retained — mean","Retained — std","Retained — min","Retained — max"]]], axis=1)
    st.dataframe(combined, use_container_width=True)

    st.markdown("<div class='section-header'>Correlation Heatmap (Numerical Features)</div>", unsafe_allow_html=True)
    corr_cols = ["CreditScore","Age","Tenure","Balance","NumOfProducts","HasCrCard","IsActiveMember","EstimatedSalary","Exited"]
    corr = df_full[corr_cols].corr().round(2)
    fig5 = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.columns.tolist(),
        colorscale=[[0,"#1e3a5f"],[0.5,"#0a0e1a"],[1,"#7f1d1d"]],
        text=corr.values.round(2), texttemplate="%{text}", textfont=dict(size=10),
        hovertemplate="<b>%{y} x %{x}</b><br>Corr: %{z:.2f}<extra></extra>", zmin=-1, zmax=1))
    fig5.update_layout(**PLOT_LAYOUT, title="Feature Correlation Matrix", height=450,
        xaxis=dict(tickangle=-30), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<div class='section-header'>EDA Key Findings</div>", unsafe_allow_html=True)
    eda_insights = [
        ("Age is the strongest churn predictor",
         f"Mean age of churned customers is {df_full[df_full['Exited']==1]['Age'].mean():.1f} vs {df_full[df_full['Exited']==0]['Age'].mean():.1f} for retained."),
        ("Balance bimodality",
         f"{(df_full['Balance']==0).mean()*100:.1f}% of customers hold zero balance. Churned customers with non-zero balances hold higher balances on average."),
        ("Product paradox",
         "Customers with 3-4 products churn at extremely high rates (>80%), while 1-2 product customers form the most stable base."),
        ("Activity is a key protective factor",
         f"Inactive members churn at {churn_rate(df_full[df_full['IsActiveMember']==0]):.1f}% vs {churn_rate(df_full[df_full['IsActiveMember']==1]):.1f}% for active members."),
    ]
    for title_txt,body in eda_insights:
        st.markdown(f'<div class="insight-box"><strong>► {title_txt}</strong><br>{body}</div>', unsafe_allow_html=True)


# =============================================================================
# MODULE 4 — GEOGRAPHIC
# =============================================================================
elif module == "Geographic":
    st.markdown("<div class='section-header'>Country KPIs — Geographic Risk Index</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col,country,accent in zip([c1,c2,c3],["France","Germany","Spain"],["#3b82f6","#f59e0b","#10b981"]):
        sub = df[df["Geography"]==country]
        if len(sub) > 0:
            with col: kpi_card(country, f"{churn_rate(sub):.1f}%", f"{sub['Exited'].sum():,} / {len(sub):,} customers", accent)

    ca,cb = st.columns(2)
    with ca:
        grp = df.groupby(["Geography","ChurnLabel"], observed=True).size().reset_index(name="Count")
        fig = px.bar(grp, x="Geography", y="Count", color="ChurnLabel",
                     color_discrete_map={"Retained":"#1e3a5f","Churned":"#ef4444"},
                     title="Customer Volume by Country & Status", barmode="stack")
        fig.update_layout(**PLOT_LAYOUT, height=360, yaxis=dict(gridcolor="#1e2a40"), xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        grp2 = df.groupby(["Geography","Gender"], observed=True).agg(ChurnRate=("Exited","mean")).reset_index()
        grp2["ChurnRate"] *= 100
        fig2 = px.bar(grp2, x="Geography", y="ChurnRate", color="Gender", barmode="group",
                      color_discrete_map={"Male":"#3b82f6","Female":"#f472b6"},
                      title="Churn Rate: Geography x Gender", text_auto=".1f")
        fig2.update_layout(**PLOT_LAYOUT, height=360, yaxis=dict(gridcolor="#1e2a40",title="Churn Rate (%)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig2, use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        grp3 = df.groupby(["Geography","AgeGroup"], observed=True).agg(ChurnRate=("Exited","mean")).reset_index()
        grp3["ChurnRate"] *= 100
        fig3 = px.line(grp3, x="AgeGroup", y="ChurnRate", color="Geography",
                       color_discrete_map=GEO_COLORS, title="Churn Rate: Age x Country", markers=True)
        fig3.update_layout(**PLOT_LAYOUT, height=340, yaxis=dict(gridcolor="#1e2a40",title="Churn Rate (%)"), xaxis=dict(gridcolor="#1e2a40"))
        st.plotly_chart(fig3, use_container_width=True)
    with cd:
        grp4 = df.groupby(["Geography","ChurnLabel"], observed=True).agg(AvgBalance=("Balance","mean")).reset_index()
        fig4 = px.bar(grp4, x="Geography", y="AvgBalance", color="ChurnLabel", barmode="group",
                      color_discrete_map={"Retained":"#1e3a5f","Churned":"#ef4444"},
                      title="Avg Balance: Churned vs Retained by Country", text_auto=",.0f")
        fig4.update_layout(**PLOT_LAYOUT, height=340, yaxis=dict(gridcolor="#1e2a40",title="Average Balance (EUR)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig4, use_container_width=True)

    # ── PM-FRIENDLY: Bubble chart — country risk vs size ─────────────────────
    st.markdown("<div class='section-header'>🫧 Risk vs Customer Volume — Country Bubble View</div>", unsafe_allow_html=True)
    st.caption("Bigger bubble = more customers. Further right = higher churn risk. Higher up = more revenue at risk.")
    geo_bubble = df.groupby("Geography", observed=True).agg(
        Customers=("Exited","count"), Churned=("Exited","sum"), AvgBalance=("Balance","mean")).reset_index()
    geo_bubble["ChurnRate"]   = geo_bubble["Churned"] / geo_bubble["Customers"] * 100
    geo_bubble["RevenueRisk"] = geo_bubble["Churned"] * geo_bubble["AvgBalance"] / 1e6
    fig_bub = px.scatter(geo_bubble, x="ChurnRate", y="RevenueRisk", size="Customers",
        color="Geography", color_discrete_map=GEO_COLORS, text="Geography",
        title="Country Risk: Churn Rate vs Revenue at Risk (bubble size = customer count)",
        labels={"ChurnRate":"Churn Rate (%)","RevenueRisk":"Revenue at Risk (EUR M)"})
    fig_bub.update_traces(textposition="top center", marker=dict(opacity=0.8))
    fig_bub.update_layout(**PLOT_LAYOUT, height=380, xaxis=dict(gridcolor="#1e2a40"), yaxis=dict(gridcolor="#1e2a40"))
    st.plotly_chart(fig_bub, use_container_width=True)

    st.markdown("<div class='section-header'>Drill-Down: Country Detail</div>", unsafe_allow_html=True)
    selected_country = st.selectbox("Select country to drill down", ["France","Germany","Spain"])
    country_df = df[df["Geography"]==selected_country]
    if len(country_df) > 0:
        d1,d2,d3 = st.columns(3)
        with d1: st.plotly_chart(churn_rate_bar(country_df,"AgeGroup",    f"{selected_country}: Churn by Age"),    use_container_width=True)
        with d2: st.plotly_chart(churn_rate_bar(country_df,"TenureGroup", f"{selected_country}: Churn by Tenure"), use_container_width=True)
        with d3: st.plotly_chart(churn_rate_bar(country_df,"CreditBand",  f"{selected_country}: Churn by Credit"), use_container_width=True)

    st.markdown("<div class='section-header'>Geographic Risk Summary Table</div>", unsafe_allow_html=True)
    geo_risk_tbl = df.groupby("Geography", observed=True).agg(
        Customers=("Exited","count"), Churned=("Exited","sum"), AvgBalance=("Balance","mean")).reset_index()
    geo_risk_tbl["ChurnRate_%"]           = (geo_risk_tbl["Churned"]/geo_risk_tbl["Customers"]*100).round(1)
    geo_risk_tbl["Revenue_at_Risk_EUR_M"] = (geo_risk_tbl["Churned"]*geo_risk_tbl["AvgBalance"]/1e6).round(2)
    geo_risk_tbl["Risk_Index"]            = ((geo_risk_tbl["ChurnRate_%"]/geo_risk_tbl["ChurnRate_%"].max())*100).round(0).astype(int)
    geo_risk_tbl["AvgBalance"]            = geo_risk_tbl["AvgBalance"].round(0)
    st.dataframe(geo_risk_tbl.set_index("Geography"), use_container_width=True)


# =============================================================================
# MODULE 5 — DEMOGRAPHICS
# =============================================================================
elif module == "Demographics":
    st.markdown("<div class='section-header'>Age & Tenure Churn Analysis</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: st.plotly_chart(churn_rate_bar(df,"AgeGroup","Churn Rate by Age Group"), use_container_width=True)
    with c2: st.plotly_chart(churn_rate_bar(df,"TenureGroup","Churn Rate by Tenure"), use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        fig = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig.add_trace(go.Histogram(x=df[df["ChurnLabel"]==label]["Age"], name=label, nbinsx=30, marker_color=color, opacity=0.75))
        fig.update_layout(**PLOT_LAYOUT, barmode="overlay", title="Age Distribution: Churned vs Retained",
            xaxis=dict(gridcolor="#1e2a40",title="Age"), yaxis=dict(gridcolor="#1e2a40",title="Count"), height=320)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        g   = df.groupby(["Gender","ChurnLabel"], observed=True).size().reset_index(name="Count")
        tot = df.groupby("Gender", observed=True)["Exited"].count().reset_index(name="Total")
        g   = g.merge(tot, on="Gender")
        g["Pct"] = g["Count"] / g["Total"] * 100
        fig2 = px.bar(g, x="Gender", y="Pct", color="ChurnLabel",
                      color_discrete_map={"Retained":"#1e3a5f","Churned":"#ef4444"},
                      title="Churn Rate by Gender", barmode="stack", text_auto=".1f")
        fig2.update_layout(**PLOT_LAYOUT, height=320, yaxis=dict(gridcolor="#1e2a40",title="Percentage (%)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── PM-FRIENDLY: Heatmap — Age x Tenure churn grid ───────────────────────
    st.markdown("<div class='section-header'>🗺️ Churn Heatmap — Age Group x Tenure (Instant Risk Map)</div>", unsafe_allow_html=True)
    st.caption("Darker red = highest churn. Use this to instantly spot which customer group needs attention.")
    pivot_at = df.groupby(["AgeGroup","TenureGroup"], observed=True)["Exited"].mean().mul(100).reset_index()
    pivot_at.columns = ["AgeGroup","TenureGroup","ChurnRate"]
    pivot_wide = pivot_at.pivot(index="AgeGroup", columns="TenureGroup", values="ChurnRate").fillna(0)
    fig_hm = go.Figure(go.Heatmap(
        z=pivot_wide.values.round(1), x=pivot_wide.columns.tolist(), y=pivot_wide.index.tolist(),
        colorscale=[[0,"#0f2a1a"],[0.4,"#f59e0b"],[1,"#ef4444"]],
        text=pivot_wide.values.round(1), texttemplate="%{text}%", textfont=dict(size=13, color="white"),
        hovertemplate="Age: %{y}<br>Tenure: %{x}<br>Churn Rate: %{z:.1f}%<extra></extra>"))
    fig_hm.update_layout(**PLOT_LAYOUT, title="Churn Rate (%) — Age x Tenure Grid", height=340)
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("<div class='section-header'>Credit Score Analysis</div>", unsafe_allow_html=True)
    c5,c6 = st.columns(2)
    with c5: st.plotly_chart(churn_rate_bar(df,"CreditBand","Churn Rate by Credit Band"), use_container_width=True)
    with c6:
        fig3 = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig3.add_trace(go.Box(y=df[df["ChurnLabel"]==label]["CreditScore"], name=label, marker_color=color, boxmean=True))
        fig3.update_layout(**PLOT_LAYOUT, title="Credit Score Distribution",
            yaxis=dict(gridcolor="#1e2a40",title="Credit Score"), xaxis=dict(gridcolor="rgba(0,0,0,0)"), height=320)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-header'>Product Engagement, Credit Card & Activity</div>", unsafe_allow_html=True)
    c7,c8,c9 = st.columns(3)
    with c7: st.plotly_chart(churn_rate_bar(df,"NumOfProducts","Churn by # Products"),          use_container_width=True)
    with c8: st.plotly_chart(churn_rate_bar(df,"CrCardLabel","Churn by Credit Card Ownership"),  use_container_width=True)
    with c9: st.plotly_chart(churn_rate_bar(df,"ActiveLabel","Churn by Member Status"),          use_container_width=True)

    st.markdown("<div class='section-header'>Drill-Down: Age Group Detail</div>", unsafe_allow_html=True)
    selected_age = st.selectbox("Select age group to drill down", ["<30","30-45","46-60","60+"])
    age_df = df[df["AgeGroup"]==selected_age]
    if len(age_df) > 0:
        da,db,dc = st.columns(3)
        with da: st.plotly_chart(churn_rate_bar(age_df,"Geography",  f"{selected_age}: Churn by Country"), use_container_width=True)
        with db: st.plotly_chart(churn_rate_bar(age_df,"TenureGroup",f"{selected_age}: Churn by Tenure"),  use_container_width=True)
        with dc: st.plotly_chart(churn_rate_bar(age_df,"CreditBand", f"{selected_age}: Churn by Credit"),  use_container_width=True)

    st.markdown("<div class='section-header'>Churn Contribution by Demographic Segment</div>", unsafe_allow_html=True)
    ca,cb,cc = st.columns(3)
    with ca: st.plotly_chart(contribution_pie(df,"AgeGroup","Contribution — Age"),    use_container_width=True)
    with cb: st.plotly_chart(contribution_pie(df,"TenureGroup","Contribution — Tenure"), use_container_width=True)
    with cc: st.plotly_chart(contribution_pie(df,"CreditBand","Contribution — Credit"), use_container_width=True)


# =============================================================================
# MODULE 6 — FINANCIAL PROFILE
# =============================================================================
elif module == "Financial Profile":
    churned  = df[df["Exited"]==1]
    retained = df[df["Exited"]==0]

    st.markdown("<div class='section-header'>Financial KPIs</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Avg Churned Balance",  f"EUR {churned['Balance'].mean():,.0f}",         "Per churned customer",  "#ef4444")
    with c2: kpi_card("Avg Retained Balance", f"EUR {retained['Balance'].mean():,.0f}",        "Per retained customer", "#10b981")
    with c3: kpi_card("Avg Churned Salary",   f"EUR {churned['EstimatedSalary'].mean():,.0f}", "Estimated annual",      "#f59e0b")
    with c4: kpi_card("Zero-Balance Churners",f"{len(churned[churned['Balance']==0]):,}",      "Left with no balance",  "#8b5cf6")

    ca,cb = st.columns(2)
    with ca: st.plotly_chart(churn_rate_bar(df,"BalanceSegment","Churn Rate by Balance Segment"), use_container_width=True)
    with cb:
        fig = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            sub = df[(df["ChurnLabel"]==label) & (df["Balance"]>0)]
            fig.add_trace(go.Histogram(x=sub["Balance"], name=label, nbinsx=40, marker_color=color, opacity=0.7))
        fig.update_layout(**PLOT_LAYOUT, barmode="overlay", title="Balance Distribution (excl. zero)",
            xaxis=dict(gridcolor="#1e2a40",title="Balance (EUR)"), yaxis=dict(gridcolor="#1e2a40",title="Count"), height=340)
        st.plotly_chart(fig, use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        sample = df.sample(min(2000,len(df)), random_state=42)
        fig2 = px.scatter(sample, x="EstimatedSalary", y="Balance", color="ChurnLabel",
            color_discrete_map={"Retained":"#3b82f6","Churned":"#ef4444"},
            opacity=0.5, title="Salary vs Balance (sample)", hover_data=["Age","Geography"])
        fig2.update_layout(**PLOT_LAYOUT, height=340,
            xaxis=dict(gridcolor="#1e2a40",title="Estimated Salary (EUR)"),
            yaxis=dict(gridcolor="#1e2a40",title="Balance (EUR)"))
        st.plotly_chart(fig2, use_container_width=True)
    with cd:
        risk = df[df["Exited"]==1].groupby("Geography", observed=True).agg(RevenueAtRisk=("Balance","sum")).reset_index()
        risk["RevenueAtRisk"] /= 1e6
        fig3 = px.bar(risk, x="Geography", y="RevenueAtRisk", color="Geography",
            color_discrete_map=GEO_COLORS, title="Balance at Risk by Country (EUR M)")
        fig3.update_traces(texttemplate="%{y:.1f}M", textposition="outside")
        fig3.update_layout(**PLOT_LAYOUT, height=340,
            yaxis=dict(gridcolor="#1e2a40",title="Balance at Risk (EUR M)"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    # ── PM-FRIENDLY: Balance x Activity churn heatmap ────────────────────────
    st.markdown("<div class='section-header'>🗺️ Balance Segment x Activity — Churn Heatmap</div>", unsafe_allow_html=True)
    st.caption("Who is leaving AND what kind of account did they have? Darker = higher churn.")
    pivot_ba = df.groupby(["BalanceSegment","ActiveLabel"], observed=True)["Exited"].mean().mul(100).reset_index()
    pivot_ba.columns = ["BalanceSegment","ActiveLabel","ChurnRate"]
    pivot_wide_ba = pivot_ba.pivot(index="BalanceSegment", columns="ActiveLabel", values="ChurnRate").fillna(0)
    fig_hm2 = go.Figure(go.Heatmap(
        z=pivot_wide_ba.values.round(1), x=pivot_wide_ba.columns.tolist(), y=pivot_wide_ba.index.tolist(),
        colorscale=[[0,"#0f2a1a"],[0.4,"#f59e0b"],[1,"#ef4444"]],
        text=pivot_wide_ba.values.round(1), texttemplate="%{text}%", textfont=dict(size=14, color="white"),
        hovertemplate="Balance: %{y}<br>Status: %{x}<br>Churn Rate: %{z:.1f}%<extra></extra>"))
    fig_hm2.update_layout(**PLOT_LAYOUT, title="Churn Rate (%) — Balance Segment x Member Activity", height=320)
    st.plotly_chart(fig_hm2, use_container_width=True)

    st.markdown("<div class='section-header'>Drill-Down: Balance Segment Detail</div>", unsafe_allow_html=True)
    selected_seg = st.selectbox("Select balance segment to drill down", ["Zero Balance","Low (1-100K)","High (100K+)"])
    seg_df = df[df["BalanceSegment"]==selected_seg]
    if len(seg_df) > 0:
        ds1,ds2,ds3 = st.columns(3)
        with ds1: st.plotly_chart(churn_rate_bar(seg_df,"Geography", f"{selected_seg}: Churn by Country"), use_container_width=True)
        with ds2: st.plotly_chart(churn_rate_bar(seg_df,"AgeGroup",  f"{selected_seg}: Churn by Age"),    use_container_width=True)
        with ds3: st.plotly_chart(churn_rate_bar(seg_df,"ActiveLabel",f"{selected_seg}: By Activity"),    use_container_width=True)

    st.markdown("<div class='section-header'>Churn Contribution — Financial Segments</div>", unsafe_allow_html=True)
    ce,cf = st.columns(2)
    with ce: st.plotly_chart(contribution_pie(df,"BalanceSegment","Contribution — Balance Segment"), use_container_width=True)
    with cf: st.plotly_chart(contribution_pie(df,"Geography","Contribution — Country"),              use_container_width=True)


# =============================================================================
# MODULE 7 — SALARY ANALYSIS
# =============================================================================
elif module == "Salary Analysis":
    st.markdown("<div class='section-header'>Salary Band Churn Analysis</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    churned_sal  = df[df["Exited"]==1]["EstimatedSalary"].mean()
    retained_sal = df[df["Exited"]==0]["EstimatedSalary"].mean()
    sal_gap      = churned_sal - retained_sal
    high_sal_cr  = churn_rate(df[df["EstimatedSalary"] > df["EstimatedSalary"].median()])
    with c1: kpi_card("Avg Churned Salary",  f"EUR {churned_sal:,.0f}",  "Per churned customer",       "#ef4444")
    with c2: kpi_card("Avg Retained Salary", f"EUR {retained_sal:,.0f}", "Per retained customer",      "#10b981")
    with c3: kpi_card("Salary Gap",          f"EUR {abs(sal_gap):,.0f}", "Churned vs retained delta",  "#f59e0b")
    with c4: kpi_card("High-Salary Churn",   f"{high_sal_cr:.1f}%",      "Above-median salary segment","#8b5cf6")

    ca,cb = st.columns(2)
    with ca: st.plotly_chart(churn_rate_bar(df,"SalaryBand","Churn Rate by Salary Band"), use_container_width=True)
    with cb: st.plotly_chart(contribution_pie(df,"SalaryBand","Churn Contribution by Salary Band"), use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        grp = df.groupby(["SalaryBand","Geography"], observed=True).agg(ChurnRate=("Exited","mean")).reset_index()
        grp["ChurnRate"] *= 100
        fig = px.bar(grp, x="SalaryBand", y="ChurnRate", color="Geography", barmode="group",
                     color_discrete_map=GEO_COLORS, title="Salary Band Churn: Geography Interaction", text_auto=".1f")
        fig.update_layout(**PLOT_LAYOUT, height=340, yaxis=dict(gridcolor="#1e2a40",title="Churn Rate (%)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)
    with cd:
        grp2 = df.groupby(["SalaryBand","AgeGroup"], observed=True).agg(ChurnRate=("Exited","mean")).reset_index()
        grp2["ChurnRate"] *= 100
        fig2 = px.line(grp2, x="SalaryBand", y="ChurnRate", color="AgeGroup", markers=True,
                       title="Salary Band Churn: Age Group Interaction")
        fig2.update_layout(**PLOT_LAYOUT, height=340, yaxis=dict(gridcolor="#1e2a40",title="Churn Rate (%)"), xaxis=dict(gridcolor="#1e2a40"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Salary vs Balance: Combined Risk Analysis</div>", unsafe_allow_html=True)
    ce,cf = st.columns(2)
    with ce:
        fig3 = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig3.add_trace(go.Box(y=df[df["ChurnLabel"]==label]["EstimatedSalary"], name=label, marker_color=color, boxmean=True))
        fig3.update_layout(**PLOT_LAYOUT, title="Salary Distribution: Churned vs Retained",
            yaxis=dict(gridcolor="#1e2a40",title="Estimated Salary (EUR)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"), height=340)
        st.plotly_chart(fig3, use_container_width=True)
    with cf:
        pivot = df.groupby(["SalaryBand","BalanceSegment"], observed=True)["Exited"].mean().mul(100).reset_index()
        pivot.columns = ["SalaryBand","BalanceSegment","ChurnRate"]
        pivot_wide = pivot.pivot(index="SalaryBand", columns="BalanceSegment", values="ChurnRate").fillna(0)
        fig4 = go.Figure(go.Heatmap(
            z=pivot_wide.values.round(1), x=pivot_wide.columns.tolist(), y=pivot_wide.index.tolist(),
            colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#ef4444"]],
            text=pivot_wide.values.round(1), texttemplate="%{text}%",
            hovertemplate="Salary: %{y}<br>Balance: %{x}<br>Churn Rate: %{z:.1f}%<extra></extra>"))
        fig4.update_layout(**PLOT_LAYOUT, title="Churn Rate Heatmap: Salary x Balance", height=340)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='section-header'>Salary Analysis Summary Table</div>", unsafe_allow_html=True)
    sal_grp = df.groupby("SalaryBand", observed=True).agg(
        Total=("Exited","count"), Churned=("Exited","sum"),
        AvgSalary=("EstimatedSalary","mean"), AvgBalance=("Balance","mean")).reset_index()
    sal_grp["ChurnRate_%"] = (sal_grp["Churned"]/sal_grp["Total"]*100).round(1)
    sal_grp["AvgSalary"]   = sal_grp["AvgSalary"].round(0)
    sal_grp["AvgBalance"]  = sal_grp["AvgBalance"].round(0)
    st.dataframe(sal_grp.set_index("SalaryBand"), use_container_width=True)


# =============================================================================
# MODULE 8 — HIGH-VALUE CUSTOMERS
# =============================================================================
elif module == "High-Value Customers":
    hv    = df[df["IsHighValue"]==1]
    hv_ch = hv[hv["Exited"]==1]

    st.markdown("<div class='section-header'>High-Value Customer KPIs</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("HV Customers",    f"{len(hv):,}",                          "Top balance+salary quartile",           "#3b82f6")
    with c2: kpi_card("HV Churn Rate",   f"{churn_rate(hv):.1f}%",               f"{len(hv_ch):,} churned HV customers",  "#ef4444")
    with c3: kpi_card("HV Avg Balance",  f"EUR {hv['Balance'].mean():,.0f}",      f"Overall avg EUR {df['Balance'].mean():,.0f}", "#f59e0b")
    with c4: kpi_card("HV Revenue Risk", f"EUR {hv_ch['Balance'].sum()/1e6:.1f}M","Total balance lost from HV churn",      "#8b5cf6")

    ca,cb = st.columns(2)
    with ca:
        grp = hv.groupby("Geography", observed=True).agg(Total=("Exited","count"),Churned=("Exited","sum")).reset_index()
        grp["ChurnRate"] = grp["Churned"]/grp["Total"]*100
        fig = px.bar(grp, x="Geography", y="ChurnRate", color="Geography",
            color_discrete_map=GEO_COLORS, title="HV Churn Rate by Country", text_auto=".1f")
        fig.update_layout(**PLOT_LAYOUT, height=320, yaxis=dict(gridcolor="#1e2a40",title="Churn Rate (%)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        fig2 = go.Figure()
        for label,color in [("Retained","#3b82f6"),("Churned","#ef4444")]:
            fig2.add_trace(go.Box(y=hv[hv["ChurnLabel"]==label]["Balance"], name=label, marker_color=color, boxmean=True))
        fig2.update_layout(**PLOT_LAYOUT, title="HV Balance Distribution: Churned vs Retained",
            yaxis=dict(gridcolor="#1e2a40",title="Balance (EUR)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"), height=320)
        st.plotly_chart(fig2, use_container_width=True)

    cc,cd = st.columns(2)
    with cc: st.plotly_chart(churn_rate_bar(hv,"AgeGroup","HV Churn by Age Group"), use_container_width=True)
    with cd: st.plotly_chart(churn_rate_bar(hv,"TenureGroup","HV Churn by Tenure"), use_container_width=True)

    # ── PM-FRIENDLY: HV vs Non-HV side-by-side ───────────────────────────────
    st.markdown("<div class='section-header'>⚖️ High-Value vs All Customers — Side-by-Side</div>", unsafe_allow_html=True)
    st.caption("Are our most valuable customers churning MORE or LESS than the rest?")
    non_hv = df[df["IsHighValue"]==0]
    compare_labels = ["Churn Rate","Avg Age","Avg Balance (K)","Avg Tenure"]
    hv_vals  = [round(churn_rate(hv),1), round(hv["Age"].mean(),1),
                round(hv["Balance"].mean()/1000,1), round(hv["Tenure"].mean(),1)]
    nv_vals  = [round(churn_rate(non_hv),1), round(non_hv["Age"].mean(),1),
                round(non_hv["Balance"].mean()/1000,1), round(non_hv["Tenure"].mean(),1)]
    fig_cmp2 = go.Figure()
    fig_cmp2.add_trace(go.Bar(name="High-Value",   x=compare_labels, y=hv_vals, marker_color="#f59e0b",
                               text=[str(v) for v in hv_vals], textposition="outside"))
    fig_cmp2.add_trace(go.Bar(name="All Customers", x=compare_labels, y=nv_vals, marker_color="#3b82f6",
                               text=[str(v) for v in nv_vals], textposition="outside"))
    fig_cmp2.update_layout(**PLOT_LAYOUT, barmode="group", title="HV vs All Customers — Key Metrics",
        yaxis=dict(gridcolor="#1e2a40"), xaxis=dict(gridcolor="rgba(0,0,0,0)"), height=360)
    st.plotly_chart(fig_cmp2, use_container_width=True)

    ce,cf = st.columns(2)
    with ce:
        fig3 = px.scatter(hv, x="EstimatedSalary", y="Balance", color="ChurnLabel",
            color_discrete_map={"Retained":"#3b82f6","Churned":"#ef4444"},
            opacity=0.6, title="HV: Salary vs Balance", hover_data=["Age","Geography"])
        fig3.update_layout(**PLOT_LAYOUT, height=320,
            xaxis=dict(gridcolor="#1e2a40",title="Salary (EUR)"),
            yaxis=dict(gridcolor="#1e2a40",title="Balance (EUR)"))
        st.plotly_chart(fig3, use_container_width=True)
    with cf:
        st.plotly_chart(contribution_pie(hv,"Geography","HV Churn Contribution by Country"), use_container_width=True)

    st.markdown("<div class='section-header'>Drill-Down: HV Churned Records — Top 50 by Balance</div>", unsafe_allow_html=True)
    show_cols = ["CustomerId","Geography","Gender","Age","Tenure","CreditScore","Balance","EstimatedSalary","NumOfProducts","IsActiveMember","HasCrCard"]
    st.dataframe(hv_ch[show_cols].sort_values("Balance",ascending=False).head(50), use_container_width=True, height=360)

    st.markdown("<div class='section-header'>HV Drill-Down: Country Analysis</div>", unsafe_allow_html=True)
    hv_country = st.selectbox("Select country for HV detail", ["France","Germany","Spain"])
    hv_c = hv[hv["Geography"]==hv_country]
    if len(hv_c) > 0:
        hc1,hc2,hc3 = st.columns(3)
        with hc1: st.plotly_chart(churn_rate_bar(hv_c,"AgeGroup",   f"HV {hv_country}: Age"),    use_container_width=True)
        with hc2: st.plotly_chart(churn_rate_bar(hv_c,"TenureGroup", f"HV {hv_country}: Tenure"), use_container_width=True)
        with hc3: st.plotly_chart(churn_rate_bar(hv_c,"SalaryBand",  f"HV {hv_country}: Salary"), use_container_width=True)


# =============================================================================
# MODULE 9 — EXECUTIVE SUMMARY
# =============================================================================
elif module == "Executive Summary":
    total        = len(df)
    n_churned    = int(df["Exited"].sum())
    overall_rate = churn_rate(df)
    hv           = df[df["IsHighValue"]==1]
    hv_rate      = churn_rate(hv)
    inactive_cr  = churn_rate(df[df["IsActiveMember"]==0])
    active_cr    = churn_rate(df[df["IsActiveMember"]==1])
    revenue_risk = df[df["Exited"]==1]["Balance"].sum()/1e6
    crcard_cr    = churn_rate(df[df["HasCrCard"]==1])
    nocard_cr    = churn_rate(df[df["HasCrCard"]==0])

    geo_grp = df.groupby("Geography", observed=True).agg(Customers=("Exited","count"),Churned=("Exited","sum")).reset_index()
    geo_grp["Rate"] = geo_grp["Churned"]/geo_grp["Customers"]*100
    top_geo = geo_grp.sort_values("Rate",ascending=False).iloc[0]

    age_grp = df.groupby("AgeGroup", observed=True).agg(Rate=("Exited","mean")).reset_index()
    age_grp["Rate"] *= 100
    top_age = age_grp.sort_values("Rate",ascending=False).iloc[0]

    prod_grp = df.groupby("NumOfProducts", observed=True).agg(Rate=("Exited","mean")).reset_index()
    prod_grp["Rate"] *= 100
    top_prod = prod_grp.sort_values("Rate",ascending=False).iloc[0]

    sal_grp = df.groupby("SalaryBand", observed=True).agg(Rate=("Exited","mean")).reset_index()
    sal_grp["Rate"] *= 100
    top_sal = sal_grp.sort_values("Rate",ascending=False).iloc[0]

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f1930,#111827);border:1px solid #1e2a40;
                border-radius:16px;padding:32px 36px;margin-bottom:24px">
        <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;
                    color:#3b82f6;margin-bottom:8px">Confidential — ECB Internal Report</div>
        <div style="font-size:1.5rem;font-weight:700;color:#f1f5f9;margin-bottom:4px">
            Customer Churn Analytics: Executive Summary</div>
        <div style="font-size:0.85rem;color:#475569">European Retail Banking — Segmentation-Driven Churn Analysis</div>
    </div>""", unsafe_allow_html=True)

    # ── PM-FRIENDLY: Visual KPI summary bar ───────────────────────────────────
    st.markdown("<div class='section-header'>📊 One-Page KPI Snapshot</div>", unsafe_allow_html=True)
    all_segments = {
        "France": churn_rate(df[df["Geography"]=="France"]),
        "Germany": churn_rate(df[df["Geography"]=="Germany"]),
        "Spain": churn_rate(df[df["Geography"]=="Spain"]),
        "Age <30": churn_rate(df[df["AgeGroup"]=="<30"]),
        "Age 30-45": churn_rate(df[df["AgeGroup"]=="30-45"]),
        "Age 46-60": churn_rate(df[df["AgeGroup"]=="46-60"]),
        "Age 60+": churn_rate(df[df["AgeGroup"]=="60+"]),
        "Active": churn_rate(df[df["IsActiveMember"]==1]),
        "Inactive": churn_rate(df[df["IsActiveMember"]==0]),
        "High-Value": hv_rate,
        "Overall": overall_rate,
    }
    snap_df = pd.DataFrame({"Segment": list(all_segments.keys()), "Churn Rate": [round(v,1) for v in all_segments.values()]})
    snap_df = snap_df.sort_values("Churn Rate", ascending=True)
    colors  = ["#ef4444" if v > 25 else ("#f59e0b" if v > 20 else "#10b981") for v in snap_df["Churn Rate"]]
    fig_snap = go.Figure(go.Bar(
        x=snap_df["Churn Rate"], y=snap_df["Segment"], orientation="h",
        marker_color=colors,
        text=[f"{v}%" for v in snap_df["Churn Rate"]], textposition="outside",
        textfont=dict(color="#e2e8f0", size=12)))
    fig_snap.add_vline(x=overall_rate, line_dash="dash", line_color="#64748b",
                       annotation_text=f"Avg {overall_rate:.1f}%", annotation_font_color="#94a3b8")
    fig_snap.update_layout(**PLOT_LAYOUT, title="Churn Rate by Segment — Green < 20% | Yellow 20-25% | Red > 25%",
        xaxis=dict(gridcolor="#1e2a40", title="Churn Rate (%)", range=[0,110]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"), height=440)
    st.plotly_chart(fig_snap, use_container_width=True)

    st.markdown("### Key Findings")
    insights = [
        ("Overall Churn Rate",
         f"The dataset ({total:,} customers) shows a churn rate of <strong>{overall_rate:.1f}%</strong> ({n_churned:,} customers exited). This exceeds industry benchmarks for European retail banking and signals a need for immediate structural intervention."),
        ("Geographic Risk Index",
         f"<strong>{top_geo['Geography']}</strong> has the highest churn rate at <strong>{top_geo['Rate']:.1f}%</strong> ({int(top_geo['Churned'])} churned out of {int(top_geo['Customers'])}). Geo-targeted retention campaigns are the priority action."),
        ("Age-Driven Attrition",
         f"The <strong>{top_age['AgeGroup']}</strong> age group has the highest churn rate at <strong>{top_age['Rate']:.1f}%</strong>. This demographic requires dedicated lifecycle engagement programmes."),
        ("Engagement Drop Indicator",
         f"Inactive members churn at <strong>{inactive_cr:.1f}%</strong> vs. <strong>{active_cr:.1f}%</strong> for active members — a gap of <strong>{inactive_cr-active_cr:.1f} percentage points</strong>. Automated re-engagement triggers should be implemented immediately."),
        ("High-Value Customer Exposure",
         f"High-value customers churn at <strong>{hv_rate:.1f}%</strong>. With an average balance of EUR {hv['Balance'].mean():,.0f}, each churned HV customer represents significant revenue loss."),
        ("Revenue at Risk",
         f"Total balance at risk from churned customers is <strong>EUR {revenue_risk:.1f}M</strong>. Recovery programmes targeting customers above the 75th percentile balance are recommended."),
        ("Product Depth Paradox",
         f"Customers with <strong>{int(top_prod['NumOfProducts'])} products</strong> show the highest churn at <strong>{top_prod['Rate']:.1f}%</strong>. Product bundling strategy needs review."),
        ("Salary Band Churn Pattern",
         f"The <strong>{top_sal['SalaryBand']}</strong> salary band shows the highest churn rate at <strong>{top_sal['Rate']:.1f}%</strong>. Combined financial profiling (salary + balance) is required for effective targeting."),
        ("Credit Card Ownership",
         f"Customers with a credit card churn at <strong>{crcard_cr:.1f}%</strong> vs <strong>{nocard_cr:.1f}%</strong> for those without. This should inform cross-selling strategy."),
    ]
    for title_txt,text in insights:
        st.markdown(f'<div class="insight-box"><strong>► {title_txt}</strong><br>{text}</div>', unsafe_allow_html=True)

    st.markdown("### Priority Alerts")
    alerts = []
    if overall_rate > 20:
        alerts.append(f"Churn rate of {overall_rate:.1f}% exceeds the 20% warning threshold — immediate action required.")
    if hv_rate > overall_rate:
        alerts.append(f"High-value segment churning faster ({hv_rate:.1f}%) than overall average ({overall_rate:.1f}%) — elevated revenue risk.")
    if inactive_cr > 2*active_cr:
        alerts.append(f"Inactive members are {inactive_cr/active_cr:.1f}x more likely to churn — reactivation programme is critical.")
    if not alerts:
        alerts.append("No critical threshold breaches detected in the current filter selection.")
    for a in alerts:
        st.markdown(f'<div class="alert-box"><strong>Warning: </strong>{a}</div>', unsafe_allow_html=True)

    st.markdown("### Strategic Recommendations")
    recs = [
        "Deploy geo-targeted retention campaigns in the highest-risk countries.",
        "Implement automated inactivity alerts and proactive outreach for dormant accounts.",
        "Assign dedicated relationship managers to high-value customers showing early churn signals.",
        "Re-evaluate product bundling strategy — customers with 3-4 products show the highest churn.",
        "Develop age-specific loyalty programmes for the highest-risk age cohort.",
        "Launch salary-band-aware retention offers — combine salary tier and balance segment for targeting.",
        "Review credit card cross-selling strategy relative to its long-term retention impact.",
        "Establish quarterly churn monitoring dashboards for all regional heads.",
        "Run proactive outreach for zero-balance account holders before they exit.",
    ]
    for i,r in enumerate(recs,1):
        st.markdown(f"**{i}.** {r}")

    st.markdown("### Data Quality Summary")
    pass_count = sum(1 for s,_ in validation_results if s=="pass")
    warn_count = sum(1 for s,_ in validation_results if s=="warn")
    fail_count = sum(1 for s,_ in validation_results if s=="fail")
    st.markdown(
        f'<div class="insight-box">Data validation completed on ingestion: '
        f'<strong>{pass_count} checks passed</strong>, <strong>{warn_count} warnings</strong>, '
        f'<strong>{fail_count} failures</strong>. See the <em>Data Validation & EDA</em> module for full details.</div>',
        unsafe_allow_html=True)