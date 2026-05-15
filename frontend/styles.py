import streamlit as st


def aplicar_estilos():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

/* ===== OCULTAR ELEMENTOS NATIVOS DO STREAMLIT ===== */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu { display: none !important; visibility: hidden !important; }
footer { visibility: hidden !important; }

/* ===== VARIÁVEIS ===== */
:root {
    --ink-950: #060B14;
    --ink-900: #0C1526;
    --ink-800: #111E36;
    --ink-700: #172744;
    --ink-600: #1E3357;
    --ink-500: #26406C;
    --mint-400: #2FFFA0;
    --mint-300: #5CFFB5;
    --mint-200: #A8FFDA;
    --mint-100: #D4FFF0;
    --slate-500: rgba(255,255,255,0.55);
    --slate-400: rgba(255,255,255,0.38);
    --slate-300: rgba(255,255,255,0.18);
    --slate-200: rgba(255,255,255,0.09);
    --slate-100: rgba(255,255,255,0.05);
    --text-primary: #FFFFFF;
    --text-soft:    rgba(255,255,255,0.75);
    --text-muted:   rgba(255,255,255,0.45);
    --border:       rgba(255,255,255,0.18);
    --success:  #2FFFA0;
    --danger:   #FF6B6B;
    --warn:     #FFD166;
    --neutral:  rgba(255,255,255,0.38);
}

/* ===== RESET E TIPOGRAFIA ===== */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ===== CORRIGE ÍCONES NATIVOS DO STREAMLIT ===== */
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons {
    font-family: 'Material Symbols Rounded' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 1.25rem !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    direction: ltr !important;
}

html, body, .stApp {
    max-width: 100vw !important;
    overflow-x: hidden !important;
    color: var(--text-primary) !important;
}

/* ===== BACKGROUND ===== */
.stApp {
    background: var(--ink-950) !important;
}

/* ===== FAIXA LATERAL (decorativa) ===== */
.stApp::before {
    content: '';
    position: fixed;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, var(--mint-400) 0%, #5B8BFF 60%, transparent 100%);
    border-radius: 0 2px 2px 0;
    z-index: 999;
}

/* ===== CONTAINERS ===== */
.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    max-width: 100vw !important;
    overflow-x: hidden !important;
    padding-top: 0 !important;
}

.block-container {
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-bottom: 4rem !important;
    padding-top: 2rem !important;
}

/* ===== HEADER ===== */
.header-wrap {
    position: relative;
    text-align: left;
    width: 100%;
    padding: 3rem 0 2.5rem !important;
    margin: 0 0 0.5rem !important;
    border-bottom: 1px solid var(--border);
    overflow: hidden;
}

/* Grid de fundo no header */
.header-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(var(--slate-100) 1px, transparent 1px),
        linear-gradient(90deg, var(--slate-100) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse 80% 100% at 50% 0%, black 30%, transparent 100%);
    pointer-events: none;
}

/* Tag acima do título (eyebrow) */
.header-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem;
    color: var(--mint-400);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
    position: relative;
    z-index: 1;
}

.header-eyebrow::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--mint-400);
    flex-shrink: 0;
}

.header-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: clamp(2.2rem, 5.5vw, 4.2rem);
    font-weight: 700 !important;
    line-height: 1;
    letter-spacing: -0.03em !important;
    color: #FFFFFF;
    text-transform: none;
    margin: 0;
    text-shadow: none;
    position: relative;
    z-index: 1;
}

.header-title span {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--mint-400);
    font-style: normal;
}

.header-desc {
    margin-top: 1rem;
    font-size: 0.875rem;
    font-weight: 400;
    color: var(--slate-500);
    max-width: 480px;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

/* Remover header-line (não existe no novo design) */
.header-line { display: none !important; }

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
    margin-bottom: 2rem;
    overflow-x: auto;
    backdrop-filter: none !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--slate-500) !important;
    font-weight: 500 !important;
    font-size: 0.81rem !important;
    border-radius: 0 !important;
    padding: 1rem 1.125rem !important;
    transition: all 0.15s ease;
    white-space: nowrap !important;
    letter-spacing: 0.01em !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    background: transparent !important;
}

.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--mint-400) !important;
    font-weight: 600 !important;
    border-bottom-color: var(--mint-400) !important;
}

.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: rgba(255,255,255,0.75) !important;
}

/* ===== HEADINGS ===== */
h1, h2, h3,
.stSubheader,
[data-testid="stSubheader"] {
    color: white !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

h2, h3 {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.69rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--slate-400) !important;
    border-bottom: 1px solid var(--slate-200) !important;
    padding-bottom: 0.625rem !important;
    margin-bottom: 1rem !important;
}

/* ===== FORMS ===== */
[data-testid="stForm"] {
    background: var(--ink-800) !important;
    backdrop-filter: none !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.75rem !important;
}

/* ===== LABELS ===== */
label,
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stDateInput label {
    color: var(--slate-500) !important;
    font-size: 0.625rem !important;
    font-weight: 700 !important;
    font-family: 'Space Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.13em !important;
}

/* ===== CHECKBOX ===== */
.stCheckbox label,
.stCheckbox label span,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] span,
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    line-height: 1.35 !important;
}

[data-testid="stCheckbox"] {
    margin-top: 8px !important;
}

[data-testid="stCheckbox"] label[data-baseweb="checkbox"] {
    align-items: center !important;
    gap: 0.55rem !important;
}

[data-testid="stCheckbox"] label[data-baseweb="checkbox"] > span:first-child {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.45) !important;
    box-shadow: 0 0 0 1px rgba(47,255,160,0.12) !important;
}

[data-testid="stCheckbox"] label[data-baseweb="checkbox"]:hover > span:first-child {
    border-color: var(--mint-300) !important;
    background: rgba(47,255,160,0.10) !important;
}

[data-testid="stCheckbox"] label[data-baseweb="checkbox"] svg {
    color: var(--ink-950) !important;
    fill: var(--ink-950) !important;
}

/* ===== INPUTS ===== */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] > div {
    background: var(--ink-950) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--slate-400) !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--mint-400) !important;
    box-shadow: 0 0 0 3px rgba(47,255,160,0.10) !important;
    outline: none !important;
}

/* ===== BOTÕES ===== */
.stButton > button,
.stDownloadButton > button {
    background: var(--mint-400) !important;
    color: var(--ink-950) !important;
    font-weight: 700 !important;
    font-size: 0.81rem !important;
    letter-spacing: 0.01em !important;
    font-family: 'Space Grotesk', sans-serif !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.69rem 1.375rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--mint-300) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active,
.stDownloadButton > button:active {
    transform: translateY(0) !important;
}

/* Botão secundário (outline) — use st.button com key "outline" ou classe customizada via markdown */
.btn-outline-st > button {
    background: transparent !important;
    color: var(--slate-500) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.81rem !important;
    padding: 0.69rem 1.375rem !important;
    transition: all 0.15s !important;
}

.btn-outline-st > button:hover {
    color: #fff !important;
    border-color: rgba(255,255,255,0.35) !important;
    background: transparent !important;
    transform: none !important;
}

/* ===== CARDS / EXPANDERS ===== */
.card-item {
    background: var(--ink-800) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.4rem !important;
    margin: 0 0 0.75rem 0 !important;
    backdrop-filter: none !important;
}

.card-item strong {
    color: white !important;
}
[data-testid="stExpander"] {
    margin-bottom: 1.25rem !important;
}

/* ===== BADGES ===== */
.badge-sim,
.badge-elegivel {
    background: rgba(47,255,160,0.12);
    color: var(--mint-300);
    border: 1px solid rgba(47,255,160,0.25);
    padding: 3px 9px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.625rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.badge-nao {
    background: var(--slate-200);
    color: var(--slate-400);
    border: 1px solid var(--slate-300);
    padding: 3px 9px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.625rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.badge-eliminado {
    background: rgba(255,107,107,0.12);
    color: #FF9E9E;
    border: 1px solid rgba(255,107,107,0.25);
    padding: 3px 9px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.625rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.badge-pendente {
    background: rgba(255,209,102,0.12);
    color: #FFDD77;
    border: 1px solid rgba(255,209,102,0.25);
    padding: 3px 9px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.625rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ===== VALOR BÔNUS ===== */
.valor-bonus {
    color: var(--mint-400);
    font-weight: 700;
    font-family: 'Space Mono', monospace;
}

/* ===== ALERTS / NOTICES ===== */
[data-testid="stAlert"] {
    background: rgba(47,255,160,0.06) !important;
    color: var(--slate-500) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(47,255,160,0.18) !important;
}

[data-testid="stAlert"] p {
    color: var(--slate-500) !important;
}

/* Alert de erro */
[data-testid="stAlert"][data-type="error"] {
    background: rgba(255,107,107,0.07) !important;
    border-color: rgba(255,107,107,0.20) !important;
    color: #FF9E9E !important;
}

[data-testid="stAlert"][data-type="error"] p {
    color: #FF9E9E !important;
}

/* ===== DIVIDERS ===== */
hr {
    border-color: var(--slate-200) !important;
}

/* ===== MÉTRICAS NATIVAS DO STREAMLIT ===== */
[data-testid="stMetric"] {
    background: var(--ink-800);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
}

[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.625rem !important;
    color: var(--slate-400) !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    letter-spacing: -0.03em !important;
    line-height: 1 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.69rem !important;
    font-weight: 500 !important;
    color: var(--mint-400) !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--slate-300);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--slate-400);
}

/* ===== LOGO FIXA ===== */
.logo-fixa {
    position: absolute;
    top: 28px;
    left: 40px;
    z-index: 999;
}

.logo-fixa img {
    width: 110px;
    height: auto;
}

/* ===== MOBILE ===== */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }
    .header-wrap {
        padding: 2.5rem 0 2rem !important;
    }
    .header-title {
        font-size: clamp(2rem, 10vw, 3.2rem) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    .stTabs [data-baseweb="tab"] {
        min-width: max-content !important;
        font-size: 0.72rem !important;
    }
    [data-testid="stForm"] {
        padding: 1.25rem !important;
    }
    .logo-fixa {
        top: 15px;
        left: 15px;
    }
    .logo-fixa img {
        width: 80px;
    }
    .header-wrap {
        text-align: left;
        width: 100%;
    }
}

/* ===== EXPANDER CORRIGIDO ===== */
[data-testid="stExpander"] {
    background: var(--ink-800) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0 !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] details {
    background: transparent !important;
}

[data-testid="stExpander"] summary {
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    padding: 14px 18px !important;
    min-height: 48px !important;
    display: flex !important;
    align-items: center !important;
}

[data-testid="stExpander"] summary p {
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}

[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 18px !important;
    border-top: 1px solid var(--border) !important;
}
</style>
""", unsafe_allow_html=True)
