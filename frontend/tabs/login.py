import streamlit as st
import hmac

USUARIOS = {
    "admin": "8599256",
    "iann": "1234",
    "valesca": "Rhcem123@",
    "paulo": "Cempaulo123@",
    "romario": "Cemromario123@"
}

def verificar_login(usuario: str, senha: str) -> bool:
    senha_correta = USUARIOS.get(usuario)
    if not senha_correta:
        return False
    return hmac.compare_digest(senha, senha_correta)

def tela_login():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if st.session_state["logado"]:
        with st.sidebar:
            st.success(f"Logado como: {st.session_state.get('usuario', '')}")
            if st.button("Sair"):
                st.session_state.clear()
                st.rerun()
        return

    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 7rem;
            max-width: 620px;
        }

        .login-logo {
            width: 82px;
            height: 82px;
            margin: 0 auto 18px auto;
            border-radius: 24px;
            background: linear-gradient(135deg, #990000, #f2a900);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            box-shadow: 0 16px 45px rgba(0,0,0,0.45);
        }

        .login-title {
            text-align: center;
            font-size: 34px;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 6px;
        }

        .login-subtitle {
            text-align: center;
            color: #f2a900;
            font-weight: 700;
            margin-bottom: 32px;
        }

        div[data-testid="stForm"] {
            background: rgba(120, 0, 0, 0.72);
            border: 1px solid rgba(242,169,0,0.22);
            padding: 32px 34px 28px 34px;
            border-radius: 22px;
            box-shadow: 0 18px 55px rgba(0,0,0,0.38);
        }

        .stTextInput label {
            color: #f2a900 !important;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .stTextInput input {
            background-color: #2f333d !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            height: 44px;
        }

        .stButton button,
        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            height: 48px;
            border-radius: 14px;
            background: #f2a900 !important;
            color: #1a1a1a !important;
            font-weight: 900;
            border: none;
            margin-top: 12px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-logo">🔐</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Sistema de Bonificação</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Acesso restrito</div>', unsafe_allow_html=True)

    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if verificar_login(usuario, senha):
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()