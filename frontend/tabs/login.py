import streamlit as st
import hmac
import base64
import hashlib
import json
import os
import time

USUARIOS = {
    "admin": "8599256",
    "iann": "1234",
    "valesca": "Rhcem123@",
    "paulo": "Cempaulo123@",
    "romario": "Cemromario123@"
}

LOGIN_SECRET = os.getenv("LOGIN_SECRET", "bonificacao-system-local-secret")
TOKEN_DURACAO_SEGUNDOS = 60 * 60 * 12


def criar_token_login(usuario: str) -> str:
    payload = {
        "usuario": usuario,
        "exp": int(time.time()) + TOKEN_DURACAO_SEGUNDOS,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
    assinatura = hmac.new(
        LOGIN_SECRET.encode("utf-8"),
        payload_b64.encode("ascii"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload_b64}.{assinatura}"


def validar_token_login(token: str) -> str | None:
    try:
        payload_b64, assinatura_recebida = token.split(".", 1)
        assinatura_esperada = hmac.new(
            LOGIN_SECRET.encode("utf-8"),
            payload_b64.encode("ascii"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(assinatura_recebida, assinatura_esperada):
            return None

        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
        usuario = payload.get("usuario")
        exp = int(payload.get("exp", 0))

        if exp < int(time.time()) or usuario not in USUARIOS:
            return None

        return usuario
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def verificar_login(usuario: str, senha: str) -> bool:
    senha_correta = USUARIOS.get(usuario)
    if not senha_correta:
        return False
    return hmac.compare_digest(senha, senha_correta)

def tela_login():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    token = st.query_params.get("auth")
    if not st.session_state["logado"] and token:
        usuario_token = validar_token_login(token)
        if usuario_token:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario_token
        else:
            if "auth" in st.query_params:
                del st.query_params["auth"]

    if st.session_state["logado"]:
        with st.sidebar:
            st.success(f"Logado como: {st.session_state.get('usuario', '')}")
            if st.button("Sair"):
                if "auth" in st.query_params:
                    del st.query_params["auth"]
                st.session_state.clear()
                st.rerun()
        return

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    box-sizing: border-box;
}

:root {
    --ink-950: #060B14;
    --ink-900: #0C1526;
    --ink-800: #111E36;
    --mint-400: #2FFFA0;
    --mint-300: #5CFFB5;
    --slate-500: rgba(255,255,255,0.55);
    --slate-400: rgba(255,255,255,0.38);
    --slate-300: rgba(255,255,255,0.18);
    --slate-200: rgba(255,255,255,0.09);
    --slate-100: rgba(255,255,255,0.05);
}

html, body, .stApp {
    background: var(--ink-950) !important;
    color: #fff !important;
}

/* Faixa lateral decorativa */
.stApp::before {
    content: '';
    position: fixed;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, var(--mint-400) 0%, #5B8BFF 60%, transparent 100%);
    border-radius: 0 2px 2px 0;
    z-index: 999;
}

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu { display: none !important; visibility: hidden !important; }
footer { visibility: hidden !important; }

[data-testid="stSidebar"] { display: none !important; }

.block-container {
    padding-top: 6rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* ── Ícone ── */
.login-logo {
    width: 72px;
    height: 72px;
    margin: 0 auto 20px auto;
    border-radius: 18px;
    background: linear-gradient(135deg, var(--ink-800) 0%, var(--ink-600, #1E3357) 100%);
    border: 1px solid var(--slate-300);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
}

/* ── Tag acima do título ── */
.login-tag {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem;
    color: var(--mint-400);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.login-tag::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--mint-400);
}

/* ── Título e subtítulo ── */
.login-title {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #ffffff;
    margin-bottom: 6px;
    line-height: 1.05;
}

.login-title em {
    font-style: normal;
    color: var(--mint-400);
}

.login-subtitle {
    text-align: center;
    color: var(--slate-500);
    font-size: 0.875rem;
    font-weight: 400;
    margin-bottom: 2rem;
    line-height: 1.5;
}

/* ── Form card ── */
div[data-testid="stForm"] {
    background: var(--ink-800) !important;
    border: 1px solid var(--slate-300) !important;
    padding: 2rem !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.40) !important;
    backdrop-filter: none !important;
}

/* ── Labels ── */
.stTextInput label {
    color: var(--slate-500) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.13em !important;
}

/* ── Inputs ── */
.stTextInput input {
    background: var(--ink-950) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid var(--slate-300) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.875rem !important;
    height: 44px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}

.stTextInput input:focus {
    border-color: var(--mint-400) !important;
    box-shadow: 0 0 0 3px rgba(47,255,160,0.10) !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: var(--slate-400) !important;
}

/* ── Botão ── */
.stButton button,
div[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    height: 46px !important;
    border-radius: 8px !important;
    background: var(--mint-400) !important;
    color: var(--ink-950) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    border: none !important;
    margin-top: 10px !important;
    transition: all 0.15s ease !important;
}

.stButton button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    background: var(--mint-300) !important;
    transform: translateY(-1px) !important;
}

/* ── Alert de erro ── */
[data-testid="stAlert"] {
    background: rgba(255,107,107,0.07) !important;
    border: 1px solid rgba(255,107,107,0.20) !important;
    border-radius: 10px !important;
    color: #FF9E9E !important;
    margin-top: 1rem !important;
}

[data-testid="stAlert"] p {
    color: #FF9E9E !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--slate-300); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

    st.markdown('<div class="login-logo">🔐</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-tag">Acesso restrito</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Sistema de<br><em>Bonificação</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Faça login para continuar.</div>', unsafe_allow_html=True)

    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if verificar_login(usuario, senha):
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.query_params["auth"] = criar_token_login(usuario)
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()
