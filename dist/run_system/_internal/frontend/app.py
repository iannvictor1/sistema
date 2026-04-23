import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Sistema de Bonificação", layout="wide")
st.title("Sistema de Bonificação")

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "Cadastrar Funcionário",
    "Listar Funcionários",
    "Lançamento Semanal",
    "Listar Lançamentos",
    "Frequência Mensal",
    "Fechamento Mensal"
])

with aba1:
    st.subheader("Cadastro de Funcionário")

    with st.form("form_funcionario", clear_on_submit=True):
        nome = st.text_input("Nome")
        cargo = st.text_input("Cargo")
        ativo = st.checkbox("Ativo", value=True)

        salvar = st.form_submit_button("Salvar")

        if salvar:
            if not nome.strip() or not cargo.strip():
                st.error("Preencha nome e cargo.")
            else:
                payload = {
                    "nome": nome.strip(),
                    "cargo": cargo.strip(),
                    "ativo": ativo
                }

                try:
                    response = requests.post(f"{API_URL}/funcionarios", json=payload, timeout=10)

                    if response.status_code == 200:
                        st.success("Funcionário cadastrado com sucesso.")
                    else:
                        st.error(f"Erro ao cadastrar: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

with aba2:
    st.subheader("Funcionários cadastrados")

    if st.button("Atualizar lista de funcionários"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)

        if response.status_code == 200:
            funcionarios = response.json()

            if funcionarios:
                for f in funcionarios:
                    st.write(
                        f"**ID:** {f['id']} | "
                        f"**Nome:** {f['nome']} | "
                        f"**Cargo:** {f['cargo']} | "
                        f"**Ativo:** {'Sim' if f['ativo'] else 'Não'}"
                    )
            else:
                st.info("Nenhum funcionário cadastrado ainda.")
        else:
            st.error("Erro ao buscar funcionários.")
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

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
            f"{f['nome']} - {f['cargo']} (ID {f['id']})": f["id"]
            for f in funcionarios
        }

        with st.form("form_lancamento_semanal", clear_on_submit=True):
            funcionario_label = st.selectbox("Funcionário", list(mapa_funcionarios.keys()))
            semana = st.text_input("Semana", placeholder="Ex: 2026-04-semana-1")

            pedidos_sep = st.number_input("Pedidos separados", min_value=0, value=0)
            pedidos_car = st.number_input("Pedidos carregados", min_value=0, value=0)
            toneladas = st.number_input("Toneladas", min_value=0.0, value=0.0, step=0.1)
            entregas = st.number_input("Entregas", min_value=0, value=0)
            retornos = st.number_input("Retornos", min_value=0, value=0)
            nota = st.selectbox("Nota", [1, 2, 3, 4, 5], index=2)

            penalidade = st.checkbox("Houve penalidade de 50%")

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
                    ]
                )

                if motivo_base == "Outro":
                    motivo_penalidade = st.text_input("Descreva o motivo")
                else:
                    motivo_penalidade = motivo_base

            salvar_lancamento = st.form_submit_button("Salvar lançamento semanal")

            if salvar_lancamento:
                if not semana.strip():
                    st.error("Preencha a semana.")
                elif penalidade and (not motivo_penalidade or not str(motivo_penalidade).strip()):
                    st.error("Informe o motivo da penalidade.")
                else:
                    payload = {
                        "funcionario_id": mapa_funcionarios[funcionario_label],
                        "semana": semana.strip(),
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
                        response = requests.post(
                            f"{API_URL}/lancamentos-semanais",
                            json=payload,
                            timeout=10
                        )

                        if response.status_code == 200:
                            dados = response.json()
                            st.success(
                                f"Lançamento salvo com sucesso. "
                                f"Bonificação calculada: R$ {dados['bonus_calculado']:.2f}"
                            )
                        else:
                            st.error(f"Erro ao salvar lançamento: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

with aba4:
    st.subheader("Lançamentos semanais")

    if st.button("Atualizar lista de lançamentos"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/lancamentos-semanais", timeout=10)

        if response.status_code == 200:
            lancamentos = response.json()

            if lancamentos:
                for l in lancamentos:
                    motivo = l["motivo_penalidade"] if l["motivo_penalidade"] else "-"
                    st.write(
                        f"**ID:** {l['id']} | "
                        f"**Funcionário ID:** {l['funcionario_id']} | "
                        f"**Semana:** {l['semana']} | "
                        f"**Penalidade:** {'Sim' if l['penalidade'] else 'Não'} | "
                        f"**Motivo:** {motivo} | "
                        f"**Bônus:** R$ {l['bonus_calculado']:.2f}"
                    )
            else:
                st.info("Nenhum lançamento semanal cadastrado ainda.")
        else:
            st.error("Erro ao buscar lançamentos.")
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

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
        mapa_funcionarios = {
            f"{f['nome']} - {f['cargo']} (ID {f['id']})": f["id"]
            for f in funcionarios
        }

        with st.form("form_frequencia_mensal", clear_on_submit=True):
            funcionario_label = st.selectbox("Funcionário para frequência", list(mapa_funcionarios.keys()))
            mes = st.text_input("Mês", placeholder="Ex: 2026-04")
            ausencias = st.number_input("Ausências no mês", min_value=0, value=0)

            salvar_frequencia = st.form_submit_button("Salvar frequência")

            if salvar_frequencia:
                if not mes.strip():
                    st.error("Preencha o mês.")
                else:
                    payload = {
                        "funcionario_id": mapa_funcionarios[funcionario_label],
                        "mes": mes.strip(),
                        "ausencias": ausencias
                    }

                    try:
                        response = requests.post(
                            f"{API_URL}/frequencias",
                            json=payload,
                            timeout=10
                        )

                        if response.status_code == 200:
                            st.success("Frequência mensal salva com sucesso.")
                        else:
                            st.error(f"Erro ao salvar frequência: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

with aba6:
    st.subheader("Fechamento Mensal")

    mes_fechamento = st.text_input("Mês para fechamento", placeholder="Ex: 2026-04")

    if st.button("Calcular fechamento mensal"):
        if not mes_fechamento.strip():
            st.error("Preencha o mês do fechamento.")
        else:
            try:
                response = requests.get(f"{API_URL}/fechamento/{mes_fechamento.strip()}", timeout=10)

                if response.status_code == 200:
                    dados = response.json()

                    if dados:
                        for d in dados:
                            status = "Elegível" if d["elegivel"] else "Eliminado por ausência"
                            st.write(
                                f"**Funcionário:** {d['funcionario']} | "
                                f"**Cargo:** {d['cargo']} | "
                                f"**Ausências:** {d['ausencias']} | "
                                f"**Lançamentos:** {d['quantidade_lancamentos']} | "
                                f"**Assiduidade:** R$ {d['assiduidade']:.2f} | "
                                f"**Status:** {status} | "
                                f"**Bônus final:** R$ {d['bonus_final']:.2f}"
                            )
                    else:
                        st.info("Nenhum dado encontrado para o mês informado.")
                else:
                    st.error(f"Erro no fechamento: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

    st.markdown("---")
    st.subheader("Exportar Excel")

    if st.button("Baixar Excel do fechamento"):
        if not mes_fechamento.strip():
            st.error("Preencha o mês antes de exportar.")
        else:
            try:
                response = requests.get(
                    f"{API_URL}/exportar-fechamento/{mes_fechamento.strip()}",
                    timeout=30
                )

                if response.status_code == 200:
                    st.download_button(
                        label="Clique aqui para baixar o arquivo Excel",
                        data=response.content,
                        file_name=f"fechamento_{mes_fechamento.strip()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error(f"Erro ao exportar Excel: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")