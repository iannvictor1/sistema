import requests
import streamlit as st
from utils import gerar_semana_mes, funcionario_recebe_entrega, API_URL


def _turnos_do_filtro(filtro_turno: str) -> set[str]:
    if filtro_turno == "Manhã e Tarde":
        return {"Manhã", "Tarde"}
    return {filtro_turno}


def _funcionario_aplicavel(funcionario: dict, filtro_turno: str, tipo_funcionario: str) -> bool:
    if funcionario.get("turno") not in _turnos_do_filtro(filtro_turno):
        return False

    tipo_entrega = funcionario.get("tipo_entrega", "Não se aplica")

    if tipo_funcionario == "Funcionário normal":
        return tipo_entrega == "Não se aplica"

    return tipo_entrega == tipo_funcionario


def _render_lancamento_mensal(API_URL: str, funcionarios: list[dict]):
    data_mes = st.date_input(
        "Mês do lançamento mensal",
        key="lanc_mensal_data"
    )
    mes = data_mes.strftime("%Y-%m")

    col_turno, col_tipo = st.columns(2)

    with col_turno:
        filtro_turno = st.selectbox(
            "Turno",
            ["Manhã", "Tarde", "Noite", "Manhã e Tarde"],
            key="lanc_mensal_turno"
        )

    with col_tipo:
        tipo_funcionario = st.selectbox(
            "Tipo de funcionário",
            ["Funcionário normal", "Motorista", "Ajudante de motorista"],
            key="lanc_mensal_tipo_funcionario"
        )

    funcionarios_aplicaveis = [
        f for f in funcionarios
        if f.get("ativo", True)
        and _funcionario_aplicavel(f, filtro_turno, tipo_funcionario)
    ]

    if not funcionarios_aplicaveis:
        st.warning("Nenhum funcionário ativo encontrado para os filtros selecionados.")
        return

    st.info(f"{len(funcionarios_aplicaveis)} funcionário(s) serão incluídos neste lançamento mensal.")

    pedidos_sep = 0
    pedidos_car = 0
    toneladas = 0.0
    entregas = 0
    retornos = 0

    if tipo_funcionario == "Funcionário normal":
        if filtro_turno == "Noite":
            pedidos_car = st.number_input(
                "Total de pedidos carregados no mês",
                min_value=0,
                value=0,
                key="lanc_mensal_pedidos_car"
            )
        else:
            col1, col2 = st.columns(2)

            with col1:
                pedidos_sep = st.number_input(
                    "Total de pedidos separados no mês",
                    min_value=0,
                    value=0,
                    key="lanc_mensal_pedidos_sep"
                )

            with col2:
                toneladas = st.number_input(
                    "Total de toneladas recebidas no mês",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key="lanc_mensal_toneladas"
                )
    else:
        col1, col2 = st.columns(2)

        with col1:
            entregas = st.number_input(
                "Total de entregas no mês",
                min_value=0,
                value=0,
                key="lanc_mensal_entregas"
            )

        with col2:
            retornos = st.number_input(
                "Total de retornos no mês",
                min_value=0,
                value=0,
                key="lanc_mensal_retornos"
            )

    st.markdown("### Notas individuais")
    notas = {}

    for f in funcionarios_aplicaveis:
        notas[f["id"]] = st.selectbox(
            f"{f['nome']} · {f['cargo']} · {f.get('turno', 'Não informado')}",
            [1, 2, 3, 4, 5],
            index=4,
            key=f"lanc_mensal_nota_{f['id']}"
        )

    if st.button("Salvar lançamento mensal", key="btn_salvar_lancamento_mensal"):
        payload = {
            "mes": mes,
            "filtro_turno": filtro_turno,
            "tipo_funcionario": tipo_funcionario,
            "usuario_lancamento": st.session_state.get("usuario"),
            "pedidos_separados": pedidos_sep,
            "pedidos_carregados": pedidos_car,
            "toneladas": toneladas,
            "entregas": entregas,
            "retornos": retornos,
            "notas": notas
        }

        try:
            response = requests.post(
                f"{API_URL}/lancamentos-mensais",
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                dados = response.json()
                total_bonus = sum(float(item.get("bonus_calculado", 0)) for item in dados)
                st.success(
                    f"Lançamento mensal salvo para {len(dados)} funcionário(s). "
                    f"Total calculado: R$ {total_bonus:.2f}"
                )
            else:
                st.error(f"Erro ao salvar lançamento mensal: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")


def render_lancamento(API_URL: str):
    st.subheader("Lançamentos")

    tipo_lancamento_label = st.selectbox(
    "Tipo de lançamento",
    ["Semanal", "Diário", "Mensal"]
    )

    tipo_lancamento = "diario" if tipo_lancamento_label == "Diário" else "mensal" if tipo_lancamento_label == "Mensal" else "semanal"

    if tipo_lancamento == "mensal":
        data_lancamento = None
        data_referencia = None
    elif tipo_lancamento == "diario":
        data_lancamento = st.date_input(
            "Data do lançamento diário",
            key="lanc_data_diaria"
        )
        data_referencia = data_lancamento
    else:
        data_referencia = st.date_input(
            "Data de referência da semana",
            key="lanc_data_referencia"
        )
        data_lancamento = data_referencia
    
    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)
        funcionarios = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        funcionarios = []

    if not funcionarios:
        st.warning("Cadastre pelo menos um funcionário antes de lançar a bonificação semanal.")
    else:
        if tipo_lancamento == "mensal":
            _render_lancamento_mensal(API_URL, funcionarios)
            return

        mapa_funcionarios = {
            f"{f['nome']} - {f['cargo']} - {f.get('turno', 'Não informado')} - {f.get('tipo_entrega', 'Não se aplica')} (ID {f['id']})": f
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
        turno_funcionario = funcionario_selecionado.get("turno", "Não informado")
        recebe_entrega = funcionario_recebe_entrega(tipo_entrega_funcionario)

        st.info(f"Turno: {turno_funcionario} | Função de entrega: {tipo_entrega_funcionario}")

        if recebe_entrega:
            pedidos_sep = 0
            pedidos_car = 0
            toneladas = 0.0

            col1, col2, col3 = st.columns(3)
            
            with col1:
                entregas = st.number_input(
                    "Entregas",
                    min_value=0,
                    value=0,
                    key="lanc_entregas"
                )
                
            with col2:
                retornos = st.number_input(
                    "Retornos",
                    min_value=0,
                    value=0,
                    key="lanc_retornos"
                )
                
            nota = 5
        else:
            entregas = 0
            retornos = 0

            pedidos_sep = 0
            pedidos_car = 0
            toneladas = 0.0

            if turno_funcionario in ["Manhã", "Tarde"]:
                col1, col2, col3 = st.columns(3)

                with col1:
                    pedidos_sep = st.number_input(
                        "Pedidos separados",
                        min_value=0,
                        value=0,
                        key="lanc_pedidos_sep"
                    )

                with col2:
                    toneladas = st.number_input(
                        "Toneladas recebidas",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        key="lanc_toneladas"
                    )

                with col3:
                    nota = st.selectbox(
                        "Nota",
                        [1, 2, 3, 4, 5],
                        index=2,
                        key="lanc_nota"
                    )
            elif turno_funcionario == "Noite":
                col1, col2 = st.columns(2)

                with col1:
                    pedidos_car = st.number_input(
                        "Pedidos carregados",
                        min_value=0,
                        value=0,
                        key="lanc_pedidos_car"
                    )

                with col2:
                    nota = st.selectbox(
                        "Nota",
                        [1, 2, 3, 4, 5],
                        index=2,
                        key="lanc_nota"
                    )
            else:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    pedidos_sep = st.number_input(
                        "Pedidos separados",
                        min_value=0,
                        value=0,
                        key="lanc_pedidos_sep"
                    )

                with col2:
                    pedidos_car = st.number_input(
                        "Pedidos carregados",
                        min_value=0,
                        value=0,
                        key="lanc_pedidos_car"
                    )

                with col3:
                    toneladas = st.number_input(
                        "Toneladas",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        key="lanc_toneladas"
                    )

                with col4:
                    nota = st.selectbox(
                        "Nota",
                        [1, 2, 3, 4, 5],
                        index=2,
                        key="lanc_nota"
                    )
                
        
        
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

        texto_botao = "Salvar lançamento diário" if tipo_lancamento == "diario" else "Salvar lançamento semanal"

        if st.button(texto_botao, key="btn_salvar_lancamento"):
            semana = gerar_semana_mes(data_referencia)

            if penalidade and (not motivo_penalidade or not str(motivo_penalidade).strip()):
                st.error("Informe o motivo da penalidade.")
            else:
                payload = {
                    "funcionario_id": funcionario_id,
                    "semana": semana,
                    "tipo_lancamento": tipo_lancamento,
                    "data_lancamento": str(data_lancamento) if data_lancamento else None,
                    "usuario_lancamento": st.session_state.get("usuario"),
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
