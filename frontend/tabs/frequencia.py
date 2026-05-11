import requests
import streamlit as st
from datetime import date


def render_frequencia(API_URL: str):
    st.subheader("Frequência Mensal")

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)
        funcionarios = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        funcionarios = []

    if not funcionarios:
        st.warning("Cadastre pelo menos um funcionário antes de lançar frequência.")
        return

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

    status_mes = st.selectbox(
        "Status do mês",
        ["Normal", "Férias"],
        key="freq_status_mes"
    )

    if status_mes == "Férias":
        ausencias = 0
        data_falta = None
        tipo_falta = None
        st.info("Funcionário em férias: não será penalizado por ausência neste mês.")
    else:
        houve_ausencia = st.checkbox(
            "Houve ausência?",
            key="freq_houve_ausencia"
        )

        if houve_ausencia:
            col_data, col_tipo = st.columns(2)

            with col_data:
                data_falta = st.date_input(
                    "Dia da falta",
                    value=date.today(),
                    key="freq_data_falta"
                )

            with col_tipo:
                tipo_falta = st.selectbox(
                    "Tipo de falta",
                    ["Falta", "Atestado", "Licença legal"],
                    key="freq_tipo_falta"
                )

            ausencias = 1
        else:
            ausencias = 0
            data_falta = None
            tipo_falta = None

    if st.button("Salvar frequência", key="btn_salvar_frequencia"):
        mes = data_falta.strftime("%Y-%m") if data_falta else data_mes.strftime("%Y-%m")

        payload = {
            "funcionario_id": mapa_funcionarios_freq[funcionario_label_freq],
            "mes": mes,
            "ausencias": ausencias,
            "data_falta": str(data_falta) if data_falta else None,
            "tipo_falta": tipo_falta,
            "status_mes": status_mes
        }

        try:
            response = requests.post(
                f"{API_URL}/frequencias",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                if data_falta:
                    st.success(f"Ausência registrada em {data_falta.strftime('%d/%m/%Y')} ({tipo_falta}).")
                else:
                    st.success(f"Frequência mensal salva com sucesso para {mes}. Status: {status_mes}.")
            else:
                st.error(f"Erro ao salvar frequência: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")
