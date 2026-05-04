import streamlit as st


def aplicar_estilos():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700&display=swap');

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu { display: none !important; visibility: hidden !important; }
footer { visibility: hidden !important; }

:root {
    --crimson-900: #1E0202;
    --crimson-800: #3B0505;
    --crimson-700: #5E0808;
    --crimson-600: #7A0C0C;
    --crimson-500: #9B1111;
    --gold-400:    #E8A800;
    --gold-300:    #F2B800;
    --gold-200:    #FFD15C;
    --text-primary: #FFFFFF;
    --text-soft:    rgba(255,255,255,0.75);
    --text-muted:   rgba(255,255,255,0.45);
    --surface-1:    rgba(255,255,255,0.06);
    --surface-2:    rgba(255,255,255,0.10);
    --border:       rgba(255,255,255,0.10);
    --success:  #22C55E;
    --danger:   #EF4444;
    --neutral:  rgba(255,255,255,0.40);
}

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}

html, body, .stApp {
    max-width: 100vw !important;
    overflow-x: hidden !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: linear-gradient(160deg,
        var(--crimson-500) 0%,
        var(--crimson-600) 30%,
        var(--crimson-700) 65%,
        var(--crimson-900) 100%
    ) !important;
    background-attachment: fixed;
}

.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    max-width: 100vw !important;
    overflow-x: hidden !important;
    padding-top: 0 !important;
}

.block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
}

/* ===== HEADER ===== */
.header-wrap {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
}

.header-eyebrow {
    display: inline-block;
    background: var(--gold-400);
    color: var(--crimson-700);
    padding: 6px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
}

.header-title {
    font-family: 'Anton', sans-serif !important;
    font-size: clamp(2.4rem, 5.8vw, 4.8rem);
    line-height: 0.95;
    letter-spacing: 0.02em;
    color: #FFFFFF;
    text-transform: uppercase;
    margin: 0;
    text-shadow: 0 2px 0 rgba(0,0,0,0.18);
}

.header-title span {
    font-family: 'Anton', sans-serif !important;
    color: var(--gold-300);
}

.header-line {
    width: min(600px, 80%);
    height: 1px;
    margin: 1.75rem auto 0;
    background: linear-gradient(
        90deg,
        transparent,
        var(--gold-400),
        transparent
    );
    opacity: 0.5;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(0,0,0,0.20);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 6px;
    gap: 4px;
    margin-bottom: 2rem;
    overflow-x: auto;
    backdrop-filter: blur(8px);
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-soft) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    transition: all 0.2s ease;
    white-space: nowrap !important;
    letter-spacing: 0.01em;
}

.stTabs [aria-selected="true"] {
    background: var(--gold-400) !important;
    color: var(--crimson-700) !important;
    font-weight: 700 !important;
}

/* ===== HEADINGS ===== */
h1, h2, h3,
.stSubheader,
[data-testid="stSubheader"] {
    color: white !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}

h2, h3 {
    border-bottom: 1px solid rgba(232,168,0,0.20);
    padding-bottom: 0.6rem;
}

/* ===== FORMS ===== */
[data-testid="stForm"] {
    background: rgba(0,0,0,0.22);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem !important;
}

/* ===== LABELS ===== */
label,
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stDateInput label,
.stCheckbox label {
    color: var(--gold-200) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ===== INPUTS ===== */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.10) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--gold-400) !important;
    box-shadow: 0 0 0 2px rgba(232,168,0,0.15) !important;
    outline: none;
}

/* ===== BUTTONS ===== */
.stButton > button,
.stDownloadButton > button {
    background: var(--gold-400) !important;
    color: var(--crimson-700) !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.02em;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--gold-300) !important;
    transform: translateY(-1px);
}

.stButton > button:active,
.stDownloadButton > button:active {
    transform: translateY(0);
}

/* ===== CARDS ===== */
[data-testid="stForm"],
.card-item,
[data-testid="stExpander"] {
    background: rgba(94, 8, 8, 0.70) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 16px 20px;
    backdrop-filter: blur(8px);
}

.card-item strong {
    color: white;
}

/* ===== BADGES ===== */
.badge-sim,
.badge-elegivel {
    background: rgba(34,197,94,0.12);
    color: #86EFAC;
    border: 1px solid rgba(34,197,94,0.25);
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.8rem;
}

.badge-nao {
    background: rgba(255,255,255,0.07);
    color: var(--neutral);
    border: 1px solid rgba(255,255,255,0.10);
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.8rem;
}

.badge-eliminado {
    background: rgba(239,68,68,0.12);
    color: #FCA5A5;
    border: 1px solid rgba(239,68,68,0.25);
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.8rem;
}

/* ===== BONUS ===== */
.valor-bonus {
    color: var(--gold-200);
    font-weight: 700;
}

/* ===== ALERTS ===== */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}

[data-testid="stAlert"] p {
    color: #FFFFFF !important;
}

/* ===== DIVIDERS ===== */
hr {
    border-color: rgba(255,255,255,0.07) !important;
}

/* ===== SCROLL ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(232,168,0,0.40);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(232,168,0,0.65);
}

/* ===== MOBILE ===== */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .header-wrap { padding: 2rem 0 1.5rem; }
    .header-title {
        font-size: clamp(2.2rem, 11vw, 3.6rem) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    .stTabs [data-baseweb="tab"] {
        min-width: max-content !important;
        font-size: 0.78rem !important;
    }
    [data-testid="stForm"] { padding: 1.25rem !important; }
}
</style>
""", unsafe_allow_html=True)