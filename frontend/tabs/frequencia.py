import requests
import streamlit as st

def render_frequencia(API_URL: str):
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