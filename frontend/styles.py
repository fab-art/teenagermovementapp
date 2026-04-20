FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
"""

CSS = """
<style>
/* ── Variables ─────────────────────────────────────────────── */
:root {
  --bg:       #0c0b09;
  --s1:       #141210;
  --s2:       #1c1916;
  --s3:       #252118;
  --gold:     #c8922a;
  --gold-d:   rgba(200,146,42,0.13);
  --gold-b:   rgba(200,146,42,0.28);
  --cream:    #f0ead8;
  --cdim:     #9a8f7a;
  --cfaint:   #5a5247;
  --danger:   #c0402a;
  --success:  #4a8c5c;
  --info:     #3a6ea8;
  --border:   rgba(240,234,216,0.08);
  --borderh:  rgba(240,234,216,0.15);
}

/* ── App shell ──────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"] { background: var(--s1) !important; border-bottom: 1px solid var(--border) !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--s1) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--cdim) !important; }
[data-testid="stSidebarNav"] a { border-radius: 4px !important; }
[data-testid="stSidebarNav"] a:hover { background: var(--s2) !important; color: var(--cream) !important; }
[data-testid="stSidebarNav"] a[aria-selected="true"] {
  background: var(--gold-d) !important;
  border: 1px solid var(--gold-b) !important;
  color: var(--gold) !important;
}
[data-testid="stSidebarNav"] a[aria-selected="true"] span { color: var(--gold) !important; }
[data-testid="stSidebarNav"] a span { color: var(--cdim) !important; }

/* ── Main content ───────────────────────────────────────────── */
.main .block-container {
  padding: 2rem 2.5rem !important;
  max-width: 1400px !important;
}

/* ── Typography ─────────────────────────────────────────────── */
h1 { font-family: 'Cormorant Garamond', serif !important; font-size: 2rem !important; font-weight: 500 !important; letter-spacing: 0.03em !important; color: var(--cream) !important; margin-bottom: 0.2rem !important; }
h2 { font-family: 'Cormorant Garamond', serif !important; font-size: 1.5rem !important; font-weight: 500 !important; color: var(--cream) !important; }
h3 { font-family: 'DM Sans', sans-serif !important; font-size: 0.7rem !important; font-weight: 500 !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; color: var(--cfaint) !important; }
p, div, span, label { color: var(--cdim) !important; }

/* ── Metrics ────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--s2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { font-size: 0.65rem !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; color: var(--cfaint) !important; }
[data-testid="stMetricValue"] { font-family: 'Cormorant Garamond', serif !important; font-size: 1.9rem !important; font-weight: 500 !important; color: var(--cream) !important; }
[data-testid="stMetricDelta"] svg { display: none !important; }

/* ── Inputs ─────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: var(--s3) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  color: var(--cream) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.85rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--gold-b) !important;
  box-shadow: 0 0 0 2px rgba(200,146,42,0.08) !important;
}
.stSelectbox > div > div > div { color: var(--cream) !important; }
.stSelectbox svg, .stMultiSelect svg { color: var(--cfaint) !important; }
label[data-testid="stWidgetLabel"] p {
  font-size: 0.65rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--cfaint) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--borderh) !important;
  color: var(--cdim) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.7rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  border-radius: 4px !important;
  padding: 0.45rem 1rem !important;
  transition: all 0.15s !important;
}
.stButton > button:hover { border-color: var(--gold-b) !important; color: var(--gold) !important; }
.stButton > button[kind="primary"] {
  background: var(--gold) !important;
  border-color: var(--gold) !important;
  color: #0c0b09 !important;
}
.stButton > button[kind="primary"]:hover { background: #d9a03a !important; }

/* ── Dataframe / Table ──────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}
.dvn-scroller { background: var(--s2) !important; }
[data-testid="glideDataEditor"] { background: var(--s2) !important; }

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  background: var(--s2) !important;
}
[data-testid="stExpander"] summary { color: var(--cdim) !important; }

/* ── Tabs ───────────────────────────────────────────────────── */
[data-testid="stTabs"] { border-bottom: 1px solid var(--border) !important; }
button[role="tab"] {
  font-size: 0.7rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--cfaint) !important;
  border-radius: 0 !important;
  padding: 0.5rem 1rem !important;
}
button[role="tab"][aria-selected="true"] {
  color: var(--gold) !important;
  border-bottom: 2px solid var(--gold) !important;
  background: transparent !important;
}

/* ── Alerts / Info boxes ────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 6px !important; border-left-width: 3px !important; }
.stSuccess { background: rgba(74,140,92,0.08) !important; border-color: var(--success) !important; }
.stError { background: rgba(192,64,42,0.08) !important; border-color: var(--danger) !important; }
.stInfo { background: rgba(200,146,42,0.08) !important; border-color: var(--gold) !important; }
.stWarning { background: rgba(192,100,42,0.1) !important; }

/* ── Divider ────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Spinner ─────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── Checkbox / Radio ───────────────────────────────────────── */
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label { color: var(--cdim) !important; }

/* ── Form container ─────────────────────────────────────────── */
[data-testid="stForm"] {
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 1.2rem !important;
  background: var(--s2) !important;
}

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--s3); border-radius: 3px; }
</style>
"""

def inject(extra_css=""):
    import streamlit as st
    st.markdown(FONTS + CSS + (f"<style>{extra_css}</style>" if extra_css else ""), unsafe_allow_html=True)


def metric_card(label, value, color="cream", sub=None):
    """Custom HTML metric card."""
    colors = {
        "cream": "#f0ead8",
        "gold":  "#c8922a",
        "danger":"#c0402a",
        "success":"#4a8c5c",
        "info":  "#3a6ea8",
    }
    c = colors.get(color, "#f0ead8")
    sub_html = f'<div style="font-size:11px;color:#5a5247;margin-top:4px;font-family:DM Mono,monospace">{sub}</div>' if sub else ""
    return f"""
<div style="background:#1c1916;border:1px solid rgba(240,234,216,0.08);border-radius:8px;padding:16px 18px;">
  <div style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#5a5247;margin-bottom:6px;font-family:DM Sans,sans-serif">{label}</div>
  <div style="font-family:Cormorant Garamond,serif;font-size:28px;font-weight:500;color:{c};line-height:1">{value}</div>
  {sub_html}
</div>"""


def badge(text, style="neutral"):
    styles = {
        "neutral": "background:rgba(240,234,216,0.07);color:#9a8f7a;border:1px solid rgba(240,234,216,0.1)",
        "gold":    "background:rgba(200,146,42,0.12);color:#c8922a;border:1px solid rgba(200,146,42,0.25)",
        "danger":  "background:rgba(192,64,42,0.1);color:#c0402a;border:1px solid rgba(192,64,42,0.25)",
        "success": "background:rgba(74,140,92,0.1);color:#4a8c5c;border:1px solid rgba(74,140,92,0.25)",
        "info":    "background:rgba(58,110,168,0.1);color:#3a6ea8;border:1px solid rgba(58,110,168,0.25)",
    }
    s = styles.get(style, styles["neutral"])
    return f'<span style="display:inline-block;padding:2px 8px;border-radius:3px;font-size:10px;letter-spacing:.08em;text-transform:uppercase;font-weight:500;{s}">{text}</span>'


def section_header(title, subtitle=None):
    sub = f'<p style="font-size:12px;color:#5a5247;margin:2px 0 0;font-family:DM Sans,sans-serif">{subtitle}</p>' if subtitle else ""
    import streamlit as st
    st.markdown(f"""
<div style="margin-bottom:20px">
  <h2 style="font-family:Cormorant Garamond,serif;font-size:1.5rem;font-weight:500;color:#f0ead8;margin:0">{title}</h2>
  {sub}
</div>""", unsafe_allow_html=True)


def panel(content_html, title=None, padding=True):
    title_html = f'<div style="padding:12px 18px;border-bottom:1px solid rgba(240,234,216,0.08);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#9a8f7a;font-family:DM Sans,sans-serif">{title}</div>' if title else ""
    pad = "padding:18px" if padding else ""
    import streamlit as st
    st.markdown(f"""
<div style="background:#1c1916;border:1px solid rgba(240,234,216,0.08);border-radius:8px;overflow:hidden;margin-bottom:16px">
  {title_html}
  <div style="{pad}">{content_html}</div>
</div>""", unsafe_allow_html=True)
