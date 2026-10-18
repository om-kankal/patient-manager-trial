import html
import re
import time
from datetime import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="MediTrack | Patient Management",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ constants
DEFAULT_URL = "http://127.0.0.1:8000"
GENDERS = ["Male", "Female", "Other"]
VERDICT_COLORS = {
    "Under Weight": "#3182ce",
    "Normal": "#38a169",
    "Observation required..": "#e53e3e",
}
AGE_LABELS = ["Child", "Teen", "Young adult", "Adult", "Middle-aged", "Senior"]
COLS = ["ID", "Name", "City", "Gender", "Age", "Height (m)", "Weight (kg)", "BMI", "Verdict", "Age Group"]
PAGES = [
    "Overview",
    "Patient Registry",
    "Patient Profile",
    "Add Patient",
    "Update Patient",
    "Delete Patient",
    "Activity Log",
    "System Health",
]

ss = st.session_state
for key, val in {"base_url": DEFAULT_URL, "activity": [], "latency": [], "api_calls": 0, "nonce": 0}.items():
    if key not in ss:
        ss[key] = val

# ------------------------------------------------------------------ styling
st.markdown(
    """
<style>
:root { --bg:#e0e5ec; --dark:#a3b1c6; --light:#ffffff; --ink:#2d3748; --muted:#718096; --accent:#2b6cb0; }
.stApp { background:var(--bg); font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; color:#4a5568; }
[data-testid="stSidebar"] { background:#d6dce6; box-shadow:6px 0 14px rgba(163,177,198,.6); }
h1,h2,h3,h4 { color:var(--ink); font-weight:700; }
.block-container { padding-top:2rem; }

.hero { display:flex; gap:18px; align-items:center; padding:22px 28px; border-left:6px solid var(--accent); margin-bottom:22px; border-radius:22px;
        background:var(--bg); box-shadow:9px 9px 16px var(--dark), -9px -9px 16px var(--light); }
.hero h1 { margin:0; font-size:1.7rem; padding:0; }
.hero p { margin:2px 0 0 0; color:var(--muted); }

.neumorphic-card { background:var(--bg); padding:22px; border-radius:20px; margin-bottom:20px;
                   box-shadow:9px 9px 16px var(--dark), -9px -9px 16px var(--light); }
.neumorphic-card.compact { padding:16px 18px; }
.neumorphic-card p { margin:4px 0; }
.neumorphic-inset { background:var(--bg); padding:14px 16px; border-radius:14px; margin-bottom:14px;
                    box-shadow:inset 4px 4px 8px var(--dark), inset -4px -4px 8px var(--light); }
.card-top { display:flex; gap:12px; align-items:center; margin-bottom:8px; }
.card-top h4 { margin:0; font-size:1.05rem; }
.avatar { width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center;
          font-weight:700; color:var(--accent); box-shadow:inset 3px 3px 6px var(--dark), inset -3px -3px 6px var(--light); }
.idtag { font-size:.78rem; color:var(--muted); }
.pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.8rem; font-weight:600; }

.gauge { position:relative; height:14px; border-radius:10px; margin:14px 0 6px 0;
         background:linear-gradient(90deg,#63b3ed 0 28%,#68d391 28% 67%,#fc8181 67% 100%);
         box-shadow:inset 2px 2px 4px rgba(0,0,0,.18); }
.gauge-marker { position:absolute; top:-6px; width:6px; height:26px; border-radius:4px; background:var(--ink);
                box-shadow:0 0 0 3px var(--bg); transform:translateX(-50%); }
.gauge-labels { display:flex; font-size:.75rem; color:var(--muted); }

.danger { border-left:6px solid #e53e3e; }

.stButton>button, .stDownloadButton>button { background:var(--bg); color:var(--ink); border:none; padding:.6rem 1.4rem;
    border-radius:12px; font-weight:600; box-shadow:6px 6px 12px var(--dark), -6px -6px 12px var(--light); transition:all .2s ease; }
.stButton>button:hover, .stDownloadButton>button:hover { box-shadow:inset 3px 3px 6px var(--dark), inset -3px -3px 6px var(--light); color:#1a202c; }
.stButton>button:disabled { opacity:.5; }

/* Input fields: dark inset surface with light, clearly readable text */
.stApp div[data-baseweb="input"], .stApp div[data-baseweb="base-input"],
.stApp div[data-baseweb="select"] > div, .stApp div[data-baseweb="textarea"] {
    background:#2b3040!important; border:none!important; border-radius:10px!important;
    box-shadow:inset 3px 3px 6px #1b1f2b, inset -3px -3px 6px #3a4155!important; }
.stApp input, .stApp textarea, .stApp [data-baseweb="select"] input,
.stApp [data-baseweb="select"] div[value], .stApp [data-baseweb="select"] span {
    color:#f1f5f9!important; -webkit-text-fill-color:#f1f5f9!important;
    caret-color:#ffffff!important; background:transparent!important; font-weight:500; }
.stApp input::placeholder, .stApp textarea::placeholder {
    color:#9aa7bb!important; -webkit-text-fill-color:#9aa7bb!important; opacity:1; }
.stApp input:disabled { -webkit-text-fill-color:#9aa7bb!important; }
.stApp [data-baseweb="select"] svg, .stNumberInput button svg { fill:#f1f5f9!important; color:#f1f5f9!important; }
.stNumberInput button { background:transparent!important; border:none!important; }
.stNumberInput button:hover { background:#3a4155!important; }
.stApp label, .stApp [data-testid="stWidgetLabel"] p { color:var(--ink)!important; font-weight:600; }
/* dropdown menus open in a separate layer */
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] [role="listbox"] { background:var(--bg)!important; }
div[data-baseweb="popover"] li, div[data-baseweb="popover"] [role="option"] { background:var(--bg)!important; color:var(--ink)!important; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] [aria-selected="true"] { background:#d2d9e4!important; }

[data-testid="stMetric"] { background:var(--bg); padding:14px 16px; border-radius:15px;
    box-shadow:6px 6px 12px var(--dark), -6px -6px 12px var(--light); }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:12px; padding:8px 18px; background:var(--bg);
    box-shadow:4px 4px 8px var(--dark), -4px -4px 8px var(--light); }
.stTabs [aria-selected="true"] { box-shadow:inset 3px 3px 6px var(--dark), inset -3px -3px 6px var(--light); color:var(--accent); }
[data-testid="stExpander"] { border:none; border-radius:14px; box-shadow:5px 5px 10px var(--dark), -5px -5px 10px var(--light); }
[data-testid="stDataFrame"] { border-radius:14px; box-shadow:5px 5px 10px var(--dark), -5px -5px 10px var(--light); }
</style>
""",
    unsafe_allow_html=True,
)

if "flash" in ss:
    st.toast(ss.flash)
    del ss["flash"]


# ------------------------------------------------------------------ helpers
def calc_bmi(weight, height):
    return round(weight / (height ** 2), 2)


def calc_verdict(bmi):
    return "Under Weight" if bmi < 18.5 else "Normal" if bmi < 30 else "Observation required.."


def api(method, path, **kwargs):
    """Single gateway to the backend: returns (status, body, latency_ms)."""
    ss.api_calls += 1
    start = time.perf_counter()
    try:
        r = requests.request(method, ss.base_url + path, timeout=5, **kwargs)
        ms = round((time.perf_counter() - start) * 1000)
        try:
            body = r.json()
        except ValueError:
            body = {}
        return r.status_code, body, ms
    except requests.RequestException as e:
        return None, {"detail": f"Connection error: {e}"}, None


def fmt_err(body):
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if isinstance(detail, list):
        lines = []
        for e in detail:
            field = ".".join(str(x) for x in e.get("loc", [])[1:]) or "request"
            lines.append(f"• **{field}**: {e.get('msg')}")
        return "\n".join(lines)
    if isinstance(detail, dict):
        return "\n".join(f"• **{k}**: {v}" for k, v in detail.items())
    return str(detail)


def log_event(action, target, ok, ms):
    ss.activity.insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Action": action,
        "Patient ID": target,
        "Result": "Success" if ok else "Failed",
        "Latency (ms)": ms,
    })


@st.cache_data(ttl=15, show_spinner=False)
def fetch_patients(base_url):
    r = requests.get(f"{base_url}/patients", timeout=5)
    r.raise_for_status()
    return r.json()


def load_df():
    try:
        data = fetch_patients(ss.base_url)
    except Exception as e:
        return None, str(e)
    rows = []
    for pid, d in data.items():
        h, w = float(d.get("height") or 0), float(d.get("weight") or 0)
        bmi = float(d.get("BMI") or (calc_bmi(w, h) if h else 0))
        rows.append({
            "ID": pid, "Name": d.get("name", ""), "City": d.get("city", ""), "Gender": d.get("gender", ""),
            "Age": int(d.get("age", 0)), "Height (m)": h, "Weight (kg)": w, "BMI": bmi,
            "Verdict": d.get("verdict") or calc_verdict(bmi),
        })
    df = pd.DataFrame(rows, columns=COLS)
    if not df.empty:
        df["Age Group"] = pd.cut(df["Age"], [0, 12, 19, 35, 50, 65, 120], labels=AGE_LABELS).astype(str)
    return df, None


def need_data():
    df, err = load_df()
    if err:
        st.error(f"Could not load patients. Check that the FastAPI server is running at {ss.base_url}.\n\n{err}")
        st.stop()
    return df


def header(title, subtitle):
    st.markdown(
        f'<div class="hero"><div><h1>{title}</h1><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def verdict_pill(verdict):
    c = VERDICT_COLORS.get(verdict, "#718096")
    return f'<span class="pill" style="background:{c}22;color:{c}">{html.escape(verdict)}</span>'


def bmi_gauge(bmi):
    pos = max(0, min(100, (bmi - 10) / 30 * 100))
    return (
        f'<div class="gauge"><div class="gauge-marker" style="left:{pos}%"></div></div>'
        '<div class="gauge-labels"><span style="width:28%">Under weight</span>'
        '<span style="width:39%">Normal</span><span style="width:33%">Observation required</span></div>'
    )


def card_html(r):
    e = html.escape
    return (
        f'<div class="neumorphic-card compact"><div class="card-top">'
        f'<div class="avatar">{e(r["Name"][:1].upper())}</div>'
        f'<div><h4>{e(r["Name"])}</h4><span class="idtag">ID {e(str(r["ID"]))}</span></div></div>'
        f'<p><b>City</b> {e(r["City"])} &nbsp;|&nbsp; <b>Gender</b> {e(r["Gender"])} &nbsp;|&nbsp; <b>Age</b> {r["Age"]} yrs</p>'
        f'<p><b>Height</b> {r["Height (m)"]} m &nbsp;|&nbsp; <b>Weight</b> {r["Weight (kg)"]} kg</p>'
        f'<p>BMI <b>{r["BMI"]}</b> &nbsp; {verdict_pill(r["Verdict"])}</p></div>'
    )


def style_chart(chart, height=280):
    return chart.properties(height=height, background="transparent").configure_view(strokeOpacity=0)


VERDICT_SCALE = alt.Scale(domain=list(VERDICT_COLORS), range=list(VERDICT_COLORS.values()))


# ------------------------------------------------------------------ sidebar
st.sidebar.markdown("## MediTrack")
st.sidebar.caption("Patient management console")
page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
st.sidebar.markdown("---")

status, body, ms = api("GET", "/health")
if status == 200:
    st.sidebar.success(f"Backend **{body.get('status')}** | v{body.get('version')} | {ms} ms")
    ss.latency = (ss.latency + [{"Time": datetime.now().strftime("%H:%M:%S"), "ms": ms}])[-60:]
else:
    st.sidebar.error("Backend offline or unreachable.")

if st.sidebar.button("Refresh data"):
    fetch_patients.clear()
    st.rerun()

with st.sidebar.expander("Connection settings"):
    st.text_input("Backend URL", key="base_url")
    st.caption("Change this when the API is deployed to another host.")

st.sidebar.markdown("---")
st.sidebar.caption(f"API calls this session: **{ss.api_calls}**  \nActions logged: **{len(ss.activity)}**")


# ------------------------------------------------------------------ pages
if page == PAGES[0]:
    header("Overview", "Live snapshot of every patient record in the system.")
    df = need_data()
    if df.empty:
        st.info("No patient records yet. Add the first one from **Add Patient**.")
        st.stop()

    flagged = int((df["Verdict"] != "Normal").sum())
    k = st.columns(5)
    k[0].metric("Total patients", len(df))
    k[1].metric("Average age", f"{df['Age'].mean():.1f} yrs")
    k[2].metric("Average BMI", f"{df['BMI'].mean():.1f}")
    k[3].metric("Healthy range", f"{(df['Verdict'] == 'Normal').mean() * 100:.0f}%")
    k[4].metric("Needs attention", flagged)
    st.markdown("<br>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Health status", "Demographics", "Correlations", "Needs attention"])
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Verdict split")
            donut = alt.Chart(df).mark_arc(innerRadius=60).encode(
                theta="count():Q",
                color=alt.Color("Verdict:N", scale=VERDICT_SCALE, legend=alt.Legend(orient="bottom")),
                tooltip=["Verdict:N", "count():Q"],
            )
            st.altair_chart(style_chart(donut))
        with c2:
            st.markdown("##### BMI distribution")
            hist = alt.Chart(df).mark_bar(color="#4a6fa5", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("BMI:Q", bin=alt.Bin(maxbins=12), title="BMI"),
                y=alt.Y("count():Q", title="Patients"),
                tooltip=["count():Q"],
            )
            st.altair_chart(style_chart(hist))
    with t2:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("##### Gender")
            g = alt.Chart(df).mark_bar(color="#4a6fa5", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("Gender:N", title=None), y=alt.Y("count():Q", title="Patients"))
            st.altair_chart(style_chart(g))
        with c2:
            st.markdown("##### Age groups")
            a = alt.Chart(df).mark_bar(color="#6b8cba", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("Age Group:N", sort=AGE_LABELS, title=None), y=alt.Y("count():Q", title="Patients"))
            st.altair_chart(style_chart(a))
        with c3:
            st.markdown("##### Top cities")
            cities = df["City"].value_counts().head(8).reset_index()
            cities.columns = ["City", "Patients"]
            cc = alt.Chart(cities).mark_bar(color="#38a169", cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                y=alt.Y("City:N", sort="-x", title=None), x=alt.X("Patients:Q"))
            st.altair_chart(style_chart(cc))
    with t3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Age vs BMI")
            s = alt.Chart(df).mark_circle(size=90, opacity=.8).encode(
                x="Age:Q", y=alt.Y("BMI:Q", scale=alt.Scale(zero=False)),
                color=alt.Color("Verdict:N", scale=VERDICT_SCALE, legend=None),
                tooltip=["Name", "Age", "BMI", "Verdict"])
            st.altair_chart(style_chart(s))
        with c2:
            st.markdown("##### Height vs weight")
            s2 = alt.Chart(df).mark_circle(size=90, opacity=.8).encode(
                x=alt.X("Height (m):Q", scale=alt.Scale(zero=False)),
                y=alt.Y("Weight (kg):Q", scale=alt.Scale(zero=False)),
                color=alt.Color("Verdict:N", scale=VERDICT_SCALE, legend=alt.Legend(orient="bottom")),
                tooltip=["Name", "Height (m)", "Weight (kg)", "BMI"])
            st.altair_chart(style_chart(s2))
    with t4:
        attention = df[df["Verdict"] != "Normal"].sort_values("BMI", ascending=False)
        if attention.empty:
            st.success("Every patient is currently in the normal BMI range.")
        else:
            st.caption(f"{len(attention)} patient(s) outside the normal range, highest BMI first.")
            st.dataframe(attention[COLS[:-1]], hide_index=True)

elif page == PAGES[1]:
    header("Patient Registry", "Search, filter, sort and export patient records.")
    df = need_data()
    if df.empty:
        st.info("The registry is empty.")
        st.stop()

    with st.expander("Search and filters", expanded=True):
        f1, f2, f3 = st.columns([2, 1, 1])
        query = f1.text_input("Search by name, ID or city", placeholder="Type to search...")
        genders = f2.multiselect("Gender", GENDERS)
        verdicts = f3.multiselect("Verdict", list(VERDICT_COLORS))
        f4, f5, f6 = st.columns([2, 1, 1])
        cities = f4.multiselect("City", sorted(df["City"].unique()))
        lo, hi = int(df["Age"].min()), int(df["Age"].max())
        age_range = f5.slider("Age range", min(lo, hi), max(lo, hi + 1), (lo, max(lo, hi)))
        sort_by = f6.selectbox("Sort by", ["Name", "Age", "BMI", "Weight (kg)", "Height (m)", "City", "ID"])
        asc = st.toggle("Ascending order", value=True)

    view = df.copy()
    if query:
        q = query.lower()
        mask = (view["Name"].str.lower().str.contains(q, regex=False)
                | view["ID"].astype(str).str.lower().str.contains(q, regex=False)
                | view["City"].str.lower().str.contains(q, regex=False))
        view = view[mask]
    if genders:
        view = view[view["Gender"].isin(genders)]
    if verdicts:
        view = view[view["Verdict"].isin(verdicts)]
    if cities:
        view = view[view["City"].isin(cities)]
    view = view[view["Age"].between(*age_range)].sort_values(sort_by, ascending=asc)

    top = st.columns([3, 2, 1, 1])
    top[0].markdown(f"**{len(view)}** of {len(df)} patients match")
    mode = top[1].radio("View", ["Table", "Cards"], horizontal=True, label_visibility="collapsed")
    top[2].download_button("Download CSV", view[COLS[:-1]].to_csv(index=False), "patients.csv", "text/csv")
    top[3].download_button("Download JSON", view[COLS[:-1]].to_json(orient="records", indent=2), "patients.json", "application/json")

    if view.empty:
        st.warning("No patients match these filters. Clear a filter to see more results.")
    elif mode == "Table":
        st.dataframe(
            view[COLS[:-1]], hide_index=True,
            column_config={
                "BMI": st.column_config.ProgressColumn("BMI", min_value=10, max_value=40, format="%.1f"),
                "Age": st.column_config.NumberColumn("Age", format="%d yrs"),
                "Height (m)": st.column_config.NumberColumn(format="%.2f"),
                "Weight (kg)": st.column_config.NumberColumn(format="%.1f"),
            },
        )
    else:
        shown = view.head(30)
        cols = st.columns(3)
        for i, (_, row) in enumerate(shown.iterrows()):
            cols[i % 3].markdown(card_html(row), unsafe_allow_html=True)
        if len(view) > len(shown):
            st.caption(f"Showing the first {len(shown)} cards. Narrow the filters or switch to Table view to see all.")

elif page == PAGES[2]:
    header("Patient Profile", "Full detail for one patient, compared with everyone else.")
    df = need_data()
    if df.empty:
        st.info("No patients to show yet.")
        st.stop()

    names = dict(zip(df["ID"], df["Name"]))
    pid = st.selectbox("Choose a patient", df["ID"], format_func=lambda i: f"{i} | {names[i]}")
    p = df[df["ID"] == pid].iloc[0]
    e = html.escape

    left, right = st.columns([3, 2])
    with left:
        st.markdown(
            f'<div class="neumorphic-card"><div class="card-top"><div class="avatar">{e(p["Name"][:1].upper())}</div>'
            f'<div><h3 style="margin:0">{e(p["Name"])}</h3><span class="idtag">ID {e(str(pid))} | {e(p["Gender"])} | {p["Age"]} yrs | {e(p["City"])}</span></div></div>'
            f'<hr style="border:0;border-top:1px solid rgba(163,177,198,.6)">'
            f'<p><b>Body mass index</b> &nbsp; {p["BMI"]} &nbsp; {verdict_pill(p["Verdict"])}</p>{bmi_gauge(p["BMI"])}</div>',
            unsafe_allow_html=True,
        )
    with right:
        low, high = round(18.5 * p["Height (m)"] ** 2, 1), round(24.9 * p["Height (m)"] ** 2, 1)
        if p["Weight (kg)"] < low:
            tip = f"{low - p['Weight (kg)']:.1f} kg below the healthy range"
        elif p["Weight (kg)"] > high:
            tip = f"{p['Weight (kg)'] - high:.1f} kg above the healthy range"
        else:
            tip = "Within the healthy range"
        pct = (df["BMI"] < p["BMI"]).mean() * 100
        st.markdown(
            f'<div class="neumorphic-card"><h4>Reference</h4>'
            f'<div class="neumorphic-inset"><b>Healthy weight for {p["Height (m)"]} m</b><br>{low} – {high} kg (WHO 18.5–24.9 BMI)</div>'
            f'<div class="neumorphic-inset"><b>Status</b><br>{tip}</div>'
            f'<div class="neumorphic-inset"><b>BMI rank</b><br>Higher than {pct:.0f}% of patients</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("##### Compared with the patient average")
    m = st.columns(4)
    m[0].metric("Age", f"{p['Age']} yrs", f"{p['Age'] - df['Age'].mean():+.1f} vs avg", delta_color="off")
    m[1].metric("Height", f"{p['Height (m)']} m", f"{p['Height (m)'] - df['Height (m)'].mean():+.2f} vs avg", delta_color="off")
    m[2].metric("Weight", f"{p['Weight (kg)']} kg", f"{p['Weight (kg)'] - df['Weight (kg)'].mean():+.1f} vs avg", delta_color="off")
    m[3].metric("BMI", f"{p['BMI']}", f"{p['BMI'] - df['BMI'].mean():+.1f} vs avg", delta_color="off")
    with st.expander("View raw record"):
        st.json({k: (v.item() if hasattr(v, "item") else v) for k, v in p.drop("Age Group").to_dict().items()})

elif page == PAGES[3]:
    header("Add Patient", "Register a new patient. BMI and verdict update as you type.")
    df, _ = load_df()
    existing = set(df["ID"]) if df is not None and not df.empty else set()
    n = ss.nonce

    form, preview = st.columns([3, 2])
    with form:
        a, b = st.columns(2)
        pid = a.text_input("Patient ID*", placeholder="e.g. P001", key=f"id{n}").strip()
        name = b.text_input("Full name*", placeholder="e.g. Rahul Sharma", key=f"nm{n}").strip()
        city = a.text_input("City*", placeholder="e.g. Nashik", key=f"ct{n}").strip()
        gender = b.selectbox("Gender*", GENDERS, key=f"gd{n}")
        age = a.number_input("Age*", 1, 120, 25, key=f"ag{n}")
        height = b.number_input("Height (meters)*", 0.3, 2.5, 1.70, 0.01, key=f"ht{n}")
        weight = a.number_input("Weight (kg)*", 2.0, 300.0, 70.0, 0.1, key=f"wt{n}")

    checks = [
        ("ID uses 1–20 letters, digits, - or _", bool(re.fullmatch(r"[A-Za-z0-9_-]{1,20}", pid))),
        ("ID is not already registered", pid not in existing),
        ("Name has at least 2 characters", len(name) >= 2),
        ("Name has no numbers", not any(ch.isdigit() for ch in name)),
        ("City has at least 2 characters", len(city) >= 2),
        ("City has no numbers", not any(ch.isdigit() for ch in city)),
    ]
    ready = all(ok for _, ok in checks)
    bmi = calc_bmi(weight, height)
    verdict = calc_verdict(bmi)

    with preview:
        st.markdown(
            f'<div class="neumorphic-card"><h4>Live preview</h4>'
            f'<p><b>BMI</b> &nbsp; {bmi} &nbsp; {verdict_pill(verdict)}</p>{bmi_gauge(bmi)}</div>',
            unsafe_allow_html=True,
        )
        with st.expander("Validation checklist", expanded=True):
            for label, ok in checks:
                st.markdown(f"{':green[Passed]' if ok else ':gray[Pending]'} &nbsp; {label}")

    if st.button("Create patient", disabled=not ready, type="primary"):
        payload = {"id": pid, "name": name, "city": city, "age": int(age),
                   "height": float(height), "weight": float(weight), "gender": gender}
        with st.spinner("Saving patient..."):
            status, body, ms = api("POST", "/create", json=payload)
        log_event("Create", pid, status == 200, ms)
        if status == 200:
            fetch_patients.clear()
            ss.nonce += 1
            ss.flash = f"Patient {pid} created"
            st.rerun()
        else:
            st.error(f"Could not create the patient.\n\n{fmt_err(body)}")

elif page == PAGES[4]:
    header("Update Patient", "Change only what is needed. Review the differences before saving.")
    df = need_data()
    if df.empty:
        st.info("No patients available to update.")
        st.stop()

    names = dict(zip(df["ID"], df["Name"]))
    sid = st.selectbox("Choose a patient", df["ID"], format_func=lambda i: f"{i} | {names[i]}")
    cur = df[df["ID"] == sid].iloc[0]

    a, b = st.columns(2)
    name = a.text_input("Name", cur["Name"], key=f"un{sid}").strip()
    city = b.text_input("City", cur["City"], key=f"uc{sid}").strip()
    gender = a.selectbox("Gender", GENDERS, GENDERS.index(cur["Gender"]) if cur["Gender"] in GENDERS else 0, key=f"ug{sid}")
    age = b.number_input("Age", 1, 120, int(cur["Age"]), key=f"ua{sid}")
    height = a.number_input("Height (meters)", 0.3, 2.5, float(cur["Height (m)"]), 0.01, key=f"uh{sid}")
    weight = b.number_input("Weight (kg)", 2.0, 300.0, float(cur["Weight (kg)"]), 0.1, key=f"uw{sid}")

    new = {"name": name, "city": city, "age": int(age), "height": float(height), "weight": float(weight), "gender": gender}
    old = {"name": cur["Name"], "city": cur["City"], "age": int(cur["Age"]),
           "height": float(cur["Height (m)"]), "weight": float(cur["Weight (kg)"]), "gender": cur["Gender"]}
    changes = {k: v for k, v in new.items() if (abs(v - old[k]) > 1e-9 if isinstance(v, float) else v != old[k])}

    problems = []
    if len(name) < 2 or any(ch.isdigit() for ch in name):
        problems.append("Name needs at least 2 characters and no numbers.")
    if len(city) < 2 or any(ch.isdigit() for ch in city):
        problems.append("City needs at least 2 characters and no numbers.")

    new_bmi = calc_bmi(new["weight"], new["height"])
    st.markdown("##### Review changes")
    d1, d2 = st.columns([3, 2])
    with d1:
        if changes:
            st.dataframe(pd.DataFrame({"Field": [k.title() for k in changes],
                                       "Current": [str(old[k]) for k in changes],
                                       "New": [str(v) for k, v in changes.items()]}), hide_index=True)
        else:
            st.info("No changes yet. Edit a field above to enable saving.")
    with d2:
        st.metric("BMI after update", new_bmi, f"{new_bmi - cur['BMI']:+.2f}", delta_color="off")
        st.markdown(verdict_pill(calc_verdict(new_bmi)), unsafe_allow_html=True)
    for msg in problems:
        st.warning(msg)

    if st.button("Save changes", disabled=not changes or bool(problems), type="primary"):
        with st.spinner("Saving changes..."):
            status, body, ms = api("PUT", f"/edit/{sid}", json=changes)
        log_event("Update", sid, status == 200, ms)
        if status == 200:
            fetch_patients.clear()
            ss.flash = f"Patient {sid} updated"
            st.rerun()
        else:
            st.error(f"Could not update the patient.\n\n{fmt_err(body)}")

elif page == PAGES[5]:
    header("Delete Patient", "Permanent removal. Confirm twice before anything is deleted.")
    df = need_data()
    if df.empty:
        st.info("No patients available to delete.")
        st.stop()

    names = dict(zip(df["ID"], df["Name"]))
    did = st.selectbox("Choose a patient", df["ID"], format_func=lambda i: f"{i} | {names[i]}")
    row = df[df["ID"] == did].iloc[0]
    st.markdown(card_html(row).replace('class="neumorphic-card compact"', 'class="neumorphic-card compact danger"'),
                unsafe_allow_html=True)
    st.warning("Deleting a record cannot be undone.")

    typed = st.text_input(f"Type the patient ID ({did}) to confirm", key=f"dc{did}")
    sure = st.checkbox("I understand this record will be removed permanently", key=f"ds{did}")
    if st.button("Delete patient", disabled=not (sure and typed.strip() == str(did))):
        with st.spinner("Deleting..."):
            status, body, ms = api("DELETE", f"/delete_one/{did}")
        log_event("Delete", did, status == 200, ms)
        if status == 200:
            fetch_patients.clear()
            ss.flash = f"Patient {did} deleted"
            st.rerun()
        else:
            st.error(f"Could not delete the patient.\n\n{fmt_err(body)}")

elif page == PAGES[6]:
    header("Activity Log", "Every create, update and delete made from this session.")
    if not ss.activity:
        st.info("Nothing logged yet. Actions you take in this app will appear here.")
    else:
        log = pd.DataFrame(ss.activity)
        c = st.columns(3)
        c[0].metric("Actions", len(log))
        c[1].metric("Successful", int((log["Result"] == "Success").sum()))
        c[2].metric("Failed", int((log["Result"] == "Failed").sum()))
        st.dataframe(log, hide_index=True)
        d1, d2 = st.columns([1, 6])
        d1.download_button("Download CSV", log.to_csv(index=False), "activity_log.csv", "text/csv")
        if d2.button("Clear log"):
            ss.activity = []
            st.rerun()

elif page == PAGES[7]:
    header("System Health", "Endpoint status, response times and API reference.")
    probes = [("GET", "/"), ("GET", "/about"), ("GET", "/health"), ("GET", "/patients")]
    results = []
    for method, path in probes:
        status, body, ms = api(method, path)
        results.append({"Method": method, "Endpoint": path,
                        "Status": status if status else "unreachable",
                        "Latency (ms)": ms, "Health": "Online" if status == 200 else "Offline"})
    res = pd.DataFrame(results)
    up = int((res["Health"] == "Online").sum())

    k = st.columns(4)
    k[0].metric("Endpoints up", f"{up}/{len(res)}")
    k[1].metric("Avg latency", f"{res['Latency (ms)'].dropna().mean():.0f} ms" if up else "n/a")
    k[2].metric("Backend URL", ss.base_url.replace("http://", "").replace("https://", ""))
    k[3].metric("API calls", ss.api_calls)

    st.markdown("##### Endpoint checks")
    st.dataframe(res, hide_index=True)

    if len(ss.latency) > 1:
        st.markdown("##### Health-check latency over this session")
        lat = pd.DataFrame(ss.latency)
        line = alt.Chart(lat).mark_line(point=True, color="#2b6cb0").encode(
            x=alt.X("Time:N", title=None, axis=alt.Axis(labelAngle=-45)), y=alt.Y("ms:Q", title="ms"))
        st.altair_chart(style_chart(line, 220))

    st.markdown("##### API reference")
    st.dataframe(pd.DataFrame([
        ("GET", "/", "Welcome message"),
        ("GET", "/about", "About information"),
        ("GET", "/health", "Status, version and model flag"),
        ("GET", "/patients", "All patient records"),
        ("POST", "/create", "Create a patient"),
        ("PUT", "/edit/{patient_id}", "Update selected fields"),
        ("DELETE", "/delete_one/{patient_id}", "Delete a patient"),
    ], columns=["Method", "Endpoint", "Purpose"]), hide_index=True)

st.markdown("<br><center style='color:#718096;font-size:.8rem'>MediTrack | Streamlit front end for the FastAPI patient service</center>",
            unsafe_allow_html=True)