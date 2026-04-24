import requests
import streamlit as st
from datetime import date, timedelta

API_URL = "http://127.0.0.1:8000"


def gerar_semana_mes(data_ref: date) -> str:
    primeiro_dia = data_ref.replace(day=1)

    dias_ate_domingo = 6 - primeiro_dia.weekday()
    if dias_ate_domingo < 0:
        dias_ate_domingo += 7

    fim_semana_1 = primeiro_dia + timedelta(days=dias_ate_domingo)

    if data_ref <= fim_semana_1:
        numero_semana = 1
    else:
        dias_restantes = (data_ref - fim_semana_1).days
        numero_semana = 1 + ((dias_restantes - 1) // 7) + 1

    return f"Semana {numero_semana} - {data_ref.strftime('%m/%Y')}"


def funcionario_recebe_entrega(tipo_entrega: str) -> bool:
    return tipo_entrega in ["Motorista", "Ajudante de motorista"]


st.set_page_config(
    page_title="Sistema de Bonificação",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #E8E6E1;
}

.stApp {
    background-color: #0F1117;
    background-image:
        radial-gradient(ellipse at 10% 0%, rgba(200, 146, 42, 0.06) 0%, transparent 55%),
        radial-gradient(ellipse at 90% 100%, rgba(255, 100, 50, 0.05) 0%, transparent 55%);
}

h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.6rem !important;
    color: #C8922A !important;
    padding: 1.5rem 0 0.25rem 0 !important;
    border-bottom: 2px solid rgba(200, 146, 42, 0.2) !important;
    margin-bottom: 1.5rem !important;
}

h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #C8922A !important;
    font-size: 1.35rem !important;
    margin-bottom: 1.2rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px 6px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 1.5rem;
}

.stTabs [aria-selected="true"] {
    background: #C8922A !important;
    color: #0F1117 !important;
    font-weight: 700 !important;
}

.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    background: #C8922A !important;
    color: #0F1117 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
}

.stDownloadButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    background: transparent !important;
    color: #C8922A !important;
    border: 1.5px solid #C8922A !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
}

.card-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-size: 0.88rem;
    color: #C8C4BE;
    line-height: 1.6;
}

.card-item strong {
    color: #C8922A;
    font-weight: 600;
}

.badge-sim {
    background: rgba(52, 211, 153, 0.15);
    color: #34D399;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.78rem;
    font-weight: 600;
}

.badge-nao {
    background: rgba(255,255,255,0.06);
    color: #888;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.78rem;
}

.badge-elegivel {
    background: rgba(52, 211, 153, 0.15);
    color: #34D399;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.78rem;
    font-weight: 600;
}

.badge-eliminado {
    background: rgba(248, 113, 113, 0.12);
    color: #F87171;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.78rem;
    font-weight: 600;
}

.valor-bonus {
    color: #C8922A;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
}

[data-testid="stForm"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>⬡ Sistema de Bonificação</h1>", unsafe_allow_html=True)

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "＋ Cadastrar Funcionário",
    "≡ Listar Funcionários",
    "↑ Lançamento Semanal",
    "≡ Listar Lançamentos",
    "◷ Frequência Mensal",
    "✦ Fechamento Mensal"
])

# ABA 1
with aba1:
    st.subheader("Cadastro de Funcionário")

    with st.form("form_funcionario", clear_on_submit=True):
        nome = st.text_input("Nome", key="cad_nome")
        cargo = st.text_input("Cargo", key="cad_cargo")

        tipo_entrega = st.selectbox(
            "Função de entrega",
            ["Não se aplica", "Motorista", "Ajudante de motorista"],
            key="cad_tipo_entrega"
        )

        ativo = st.checkbox("Ativo", value=True, key="cad_ativo")

        salvar = st.form_submit_button("Salvar funcionário")

        if salvar:
            if not nome.strip() or not cargo.strip():
                st.error("Preencha nome e cargo.")
            else:
                payload = {
                    "nome": nome.strip(),
                    "cargo": cargo.strip(),
                    "ativo": ativo,
                    "tipo_entrega": tipo_entrega
                }

                try:
                    response = requests.post(f"{API_URL}/funcionarios", json=payload, timeout=10)

                    if response.status_code == 200:
                        st.success("Funcionário cadastrado com sucesso.")
                    else:
                        st.error(f"Erro ao cadastrar: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

# ABA 2
with aba2:
    st.subheader("Funcionários Cadastrados")

    if st.button("Atualizar lista", key="btn_atualizar_funcionarios"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)

        if response.status_code == 200:
            funcionarios = response.json()

            if funcionarios:
                for f in funcionarios:
                    badge = '<span class="badge-sim">Ativo</span>' if f["ativo"] else '<span class="badge-nao">Inativo</span>'
                    entrega = f.get("tipo_entrega", "Não se aplica")

                    st.markdown(f"""
                    <div class="card-item">
                        <strong>#{f['id']}</strong> &nbsp;·&nbsp;
                        {f['nome']} &nbsp;·&nbsp;
                        <span style="color:#9A9690">{f['cargo']}</span>
                        &nbsp;·&nbsp;
                        <span style="color:#9A9690">Entrega: {entrega}</span>
                        &nbsp;&nbsp;{badge}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum funcionário cadastrado ainda.")
        else:
            st.error("Erro ao buscar funcionários.")
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

# ABA 3
with aba3:
    st.subheader("Lançamento Semanal")

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)
        funcionarios = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        funcionarios = []

    if not funcionarios:
        st.warning("Cadastre pelo menos um funcionário antes de lançar a bonificação semanal.")
    else:
        mapa_funcionarios = {
            f"{f['nome']} - {f['cargo']} - {f.get('tipo_entrega', 'Não se aplica')} (ID {f['id']})": f
            for f in funcionarios
        }

        funcionario_label = st.selectbox(
            "Funcionário",
            list(mapa_funcionarios.keys()),
            key="lanc_funcionario"
        )

        funcionario_selecionado = mapa_funcionarios[funcionario_label]
        funcionario_id = funcionario_selecionado["id"]
        tipo_entrega_funcionario = funcionario_selecionado.get("tipo_entrega", "Não se aplica")
        recebe_entrega = funcionario_recebe_entrega(tipo_entrega_funcionario)

        st.info(f"Função de entrega do funcionário: {tipo_entrega_funcionario}")

        data_referencia = st.date_input("Data de referência da semana", key="lanc_data_referencia")

        col1, col2, col3 = st.columns(3)

        with col1:
            pedidos_sep = st.number_input("Pedidos separados", min_value=0, value=0, key="lanc_pedidos_sep")
            pedidos_car = st.number_input("Pedidos carregados", min_value=0, value=0, key="lanc_pedidos_car")

        with col2:
            toneladas = st.number_input("Toneladas", min_value=0.0, value=0.0, step=0.1, key="lanc_toneladas")

            if recebe_entrega:
                entregas = st.number_input("Entregas", min_value=0, value=0, key="lanc_entregas")
            else:
                entregas = 0
                st.warning("Este funcionário não recebe bonificação por entregas. O campo foi desativado.")

        with col3:
            if recebe_entrega:
                retornos = st.number_input("Retornos", min_value=0, value=0, key="lanc_retornos")
            else:
                retornos = 0
            nota = st.selectbox("Nota", [1, 2, 3, 4, 5], index=2, key="lanc_nota")

        penalidade = st.checkbox("Houve penalidade de 50%", key="lanc_penalidade")

        motivo_penalidade = None
        if penalidade:
            motivo_base = st.selectbox(
                "Motivo da penalidade",
                [
                    "Erro de carregamento",
                    "Erro de recebimento",
                    "Avaria",
                    "Produto vencido",
                    "Atraso cliente retira",
                    "5S não realizado",
                    "Entrega errada",
                    "Avaria na carga",
                    "Falta de produtos",
                    "Falta de canhotos",
                    "Outro"
                ],
                key="lanc_motivo_base"
            )

            if motivo_base == "Outro":
                motivo_penalidade = st.text_input("Descreva o motivo", key="lanc_motivo_outro")
            else:
                motivo_penalidade = motivo_base

        if st.button("Salvar lançamento semanal", key="btn_salvar_lancamento"):
            semana = gerar_semana_mes(data_referencia)

            if penalidade and (not motivo_penalidade or not str(motivo_penalidade).strip()):
                st.error("Informe o motivo da penalidade.")
            else:
                payload = {
                    "funcionario_id": funcionario_id,
                    "semana": semana,
                    "pedidos_separados": pedidos_sep,
                    "pedidos_carregados": pedidos_car,
                    "toneladas": toneladas,
                    "entregas": entregas,
                    "retornos": retornos,
                    "nota": nota,
                    "penalidade": penalidade,
                    "motivo_penalidade": motivo_penalidade.strip() if isinstance(motivo_penalidade, str) else motivo_penalidade
                }

                try:
                    response = requests.post(f"{API_URL}/lancamentos-semanais", json=payload, timeout=10)

                    if response.status_code == 200:
                        dados = response.json()
                        st.success(
                            f"Lançamento salvo. Semana: {semana} | "
                            f"Bonificação calculada: R$ {dados['bonus_calculado']:.2f}"
                        )
                    else:
                        st.error(f"Erro ao salvar lançamento: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

# ABA 4
with aba4:
    st.subheader("Lançamentos Semanais")

    if st.button("Atualizar lista", key="btn_atualizar_lancamentos"):
        st.rerun()

    try:
        resp_lanc = requests.get(f"{API_URL}/lancamentos-semanais", timeout=10)
        resp_func = requests.get(f"{API_URL}/funcionarios", timeout=10)

        if resp_lanc.status_code == 200 and resp_func.status_code == 200:
            lancamentos = resp_lanc.json()
            funcionarios = resp_func.json()

            mapa_funcionarios = {
                f["id"]: f for f in funcionarios
            }

            if lancamentos:
                for l in lancamentos:
                    funcionario = mapa_funcionarios.get(l["funcionario_id"], {})
                    nome_funcionario = funcionario.get("nome", f"Funcionário #{l['funcionario_id']}")
                    cargo_funcionario = funcionario.get("cargo", "-")
                    tipo_entrega = funcionario.get("tipo_entrega", "Não se aplica")

                    motivo = l["motivo_penalidade"] if l["motivo_penalidade"] else "—"
                    pen_badge = (
                        '<span class="badge-eliminado">Penalidade</span>'
                        if l["penalidade"]
                        else '<span class="badge-nao">Sem penalidade</span>'
                    )

                    st.markdown(f"""
                    <div class="card-item">
                        <strong>#{l['id']}</strong> &nbsp;·&nbsp;
                        <strong>{nome_funcionario}</strong>
                        <span style="color:#9A9690"> · {cargo_funcionario} · {tipo_entrega}</span>
                        <br>
                        Semana <strong>{l['semana']}</strong>
                        &nbsp;&nbsp;{pen_badge}
                        &nbsp;·&nbsp; Motivo: <span style="color:#9A9690">{motivo}</span>
                        &nbsp;&nbsp;<span class="valor-bonus">R$ {l['bonus_calculado']:.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"Editar lançamento #{l['id']} - {nome_funcionario}"):
                        nova_semana = st.text_input(
                            "Semana",
                            value=l["semana"],
                            key=f"edit_semana_{l['id']}"
                        )

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            novos_pedidos_sep = st.number_input(
                                "Pedidos separados",
                                min_value=0,
                                value=int(l["pedidos_separados"]),
                                key=f"edit_sep_{l['id']}"
                            )

                            novos_pedidos_car = st.number_input(
                                "Pedidos carregados",
                                min_value=0,
                                value=int(l["pedidos_carregados"]),
                                key=f"edit_car_{l['id']}"
                            )

                        with col2:
                            novas_toneladas = st.number_input(
                                "Toneladas",
                                min_value=0.0,
                                value=float(l["toneladas"]),
                                step=0.1,
                                key=f"edit_ton_{l['id']}"
                            )

                            if tipo_entrega in ["Motorista", "Ajudante de motorista"]:
                                novas_entregas = st.number_input(
                                    "Entregas",
                                    min_value=0,
                                    value=int(l["entregas"]),
                                    key=f"edit_entregas_{l['id']}"
                                )
                            else:
                                novas_entregas = 0
                                st.info("Este funcionário não recebe bonificação por entregas.")

                        with col3:
                            novos_retornos = st.number_input(
                                "Retornos",
                                min_value=0,
                                value=int(l["retornos"]),
                                key=f"edit_retornos_{l['id']}"
                            )

                            nova_nota = st.selectbox(
                                "Nota",
                                [1, 2, 3, 4, 5],
                                index=[1, 2, 3, 4, 5].index(int(l["nota"])),
                                key=f"edit_nota_{l['id']}"
                            )

                        nova_penalidade = st.checkbox(
                            "Houve penalidade de 50%",
                            value=bool(l["penalidade"]),
                            key=f"edit_penalidade_{l['id']}"
                        )

                        novo_motivo = None
                        if nova_penalidade:
                            motivos = [
                                "Erro de carregamento",
                                "Erro de recebimento",
                                "Avaria",
                                "Produto vencido",
                                "Atraso cliente retira",
                                "5S não realizado",
                                "Entrega errada",
                                "Avaria na carga",
                                "Falta de produtos",
                                "Falta de canhotos",
                                "Outro"
                            ]

                            motivo_atual = l["motivo_penalidade"] or motivos[0]
                            index_motivo = motivos.index(motivo_atual) if motivo_atual in motivos else len(motivos) - 1

                            motivo_base = st.selectbox(
                                "Motivo da penalidade",
                                motivos,
                                index=index_motivo,
                                key=f"edit_motivo_base_{l['id']}"
                            )

                            if motivo_base == "Outro":
                                novo_motivo = st.text_input(
                                    "Descreva o motivo",
                                    value=l["motivo_penalidade"] or "",
                                    key=f"edit_motivo_outro_{l['id']}"
                                )
                            else:
                                novo_motivo = motivo_base

                        col_btn1, col_btn2 = st.columns(2)

                        with col_btn1:
                            if st.button("Salvar alterações", key=f"btn_salvar_edit_{l['id']}"):
                                if nova_penalidade and (not novo_motivo or not str(novo_motivo).strip()):
                                    st.error("Informe o motivo da penalidade.")
                                else:
                                    payload = {
                                        "semana": nova_semana,
                                        "pedidos_separados": novos_pedidos_sep,
                                        "pedidos_carregados": novos_pedidos_car,
                                        "toneladas": novas_toneladas,
                                        "entregas": novas_entregas,
                                        "retornos": novos_retornos,
                                        "nota": nova_nota,
                                        "penalidade": nova_penalidade,
                                        "motivo_penalidade": novo_motivo.strip() if isinstance(novo_motivo, str) else novo_motivo
                                    }

                                    resp_edit = requests.put(
                                        f"{API_URL}/lancamentos-semanais/{l['id']}",
                                        json=payload,
                                        timeout=10
                                    )

                                    if resp_edit.status_code == 200:
                                        st.success("Lançamento atualizado com sucesso.")
                                        st.rerun()
                                    else:
                                        st.error(f"Erro ao atualizar: {resp_edit.text}")

                        with col_btn2:
                            if st.button("Excluir lançamento", key=f"btn_excluir_{l['id']}"):
                                resp_del = requests.delete(
                                    f"{API_URL}/lancamentos-semanais/{l['id']}",
                                    timeout=10
                                )

                                if resp_del.status_code == 200:
                                    st.success("Lançamento excluído com sucesso.")
                                    st.rerun()
                                else:
                                    st.error(f"Erro ao excluir: {resp_del.text}")
            else:
                st.info("Nenhum lançamento semanal cadastrado ainda.")
        else:
            st.error("Erro ao buscar lançamentos ou funcionários.")
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

# ABA 5
with aba5:
    st.subheader("Frequência Mensal")

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)
        funcionarios = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        funcionarios = []

    if not funcionarios:
        st.warning("Cadastre pelo menos um funcionário antes de lançar frequência.")
    else:
        mapa_funcionarios_freq = {
            f"{f['nome']} - {f['cargo']} - {f.get('tipo_entrega', 'Não se aplica')} (ID {f['id']})": f["id"]
            for f in funcionarios
        }

        funcionario_label_freq = st.selectbox(
            "Funcionário para frequência",
            list(mapa_funcionarios_freq.keys()),
            key="freq_funcionario"
        )

        data_mes = st.date_input("Mês de referência", key="freq_mes")
        ausencias = st.number_input("Ausências no mês", min_value=0, value=0, key="freq_ausencias")

        if st.button("Salvar frequência", key="btn_salvar_frequencia"):
            mes = data_mes.strftime("%Y-%m")

            payload = {
                "funcionario_id": mapa_funcionarios_freq[funcionario_label_freq],
                "mes": mes,
                "ausencias": ausencias
            }

            try:
                response = requests.post(f"{API_URL}/frequencias", json=payload, timeout=10)

                if response.status_code == 200:
                    st.success(f"Frequência mensal salva com sucesso para {mes}.")
                else:
                    st.error(f"Erro ao salvar frequência: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

# ABA 6
with aba6:
    st.subheader("Fechamento Mensal")

    data_fechamento = st.date_input("Mês para fechamento", key="fech_data")
    mes_fechamento = data_fechamento.strftime("%Y-%m")

    if st.button("Calcular fechamento mensal", key="btn_calcular_fechamento"):
        try:
            response = requests.get(f"{API_URL}/fechamento/{mes_fechamento}", timeout=10)

            if response.status_code == 200:
                dados = response.json()

                if dados:
                    for d in dados:
                        elegivel = d["elegivel"]
                        status_badge = '<span class="badge-elegivel">Elegível</span>' if elegivel else '<span class="badge-eliminado">Eliminado por ausência</span>'
                        bonus_class = "valor-bonus" if elegivel else ""

                        st.markdown(f"""
                        <div class="card-item">
                            <strong>{d['funcionario']}</strong>
                            <span style="color:#9A9690"> · {d['cargo']}</span>
                            &nbsp;&nbsp;{status_badge}
                            <br>
                            <span style="font-size:0.82rem; color:#777; margin-top:6px; display:block">
                                Ausências: <strong style="color:#C8C4BE">{d['ausencias']}</strong>
                                &nbsp;·&nbsp; Lançamentos: <strong style="color:#C8C4BE">{d['quantidade_lancamentos']}</strong>
                                &nbsp;·&nbsp; Assiduidade: <strong style="color:#C8C4BE">R$ {d['assiduidade']:.2f}</strong>
                                &nbsp;·&nbsp; Bônus final: <span class="{bonus_class}">R$ {d['bonus_final']:.2f}</span>
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhum dado encontrado para o mês informado.")
            else:
                st.error(f"Erro no fechamento: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

    st.markdown("---")
    st.subheader("Exportar Excel")

    if st.button("Baixar Excel do fechamento", key="btn_baixar_excel_fechamento"):
        try:
            response = requests.get(f"{API_URL}/exportar-fechamento/{mes_fechamento}", timeout=30)

            if response.status_code == 200:
                st.download_button(
                    label="⬇ Clique aqui para baixar o arquivo Excel",
                    data=response.content,
                    file_name=f"fechamento_{mes_fechamento}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_fechamento"
                )
            else:
                st.error(f"Erro ao exportar Excel: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")