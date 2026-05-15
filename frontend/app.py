import requests
import streamlit as st
from styles import aplicar_estilos
from utils import gerar_semana_mes, funcionario_recebe_entrega
from utils import API_URL
from tabs.cadastros import render_cadastro
from tabs.funcionarios import render_funcionarios
from tabs.lancamento import render_lancamento
from tabs.historico_lancamentos import render_historico_lancamentos
from tabs.frequencia import render_frequencia
from tabs.fechamento import render_fechamento
from tabs.regras_negocio import render_regras
from tabs.login import tela_login
import hmac
from pathlib import Path
from tabs.dashboard import render_dashboard
from PIL import Image
import base64
from io import BytesIO

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo.png"

st.set_page_config(
    page_title="Sistema de Bonificação",
    page_icon=Image.open(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="collapsed"
)

tela_login()

aplicar_estilos()

st.markdown(f"""
<div class="header-wrap">
    <div class="header-eyebrow">Sistema de Bônus</div>
    <div class="header-title">Performance <span>& Resultados</span></div>
    <div class="header-line"></div>
</div>
""", unsafe_allow_html=True)

aba0, aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
    "📊 Dashboard",
    "＋  Cadastrar Funcionário",
    "≡  Listar Funcionários",
    "↑  Lançamentos",
    "≡  Listar Lançamentos",
    "◷  Frequência Mensal",
    "✦  Fechamento Mensal",
    "📘 Regras de Negócio"
])

with aba0:
    render_dashboard(API_URL)

with aba1:
    render_cadastro(API_URL)

with aba2:
    render_funcionarios(API_URL)

with aba3:
    render_lancamento(API_URL)

with aba4:
    render_historico_lancamentos(API_URL)

with aba5:
    render_frequencia(API_URL)

with aba6:
    render_fechamento(API_URL)

with aba7:
    render_regras(API_URL)
    
