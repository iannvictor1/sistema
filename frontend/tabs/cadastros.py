import requests
import streamlit as st


def render_cadastro(API_URL: str):
    st.subheader("Cadastro de Funcionário")

    with st.form("form_funcionario", clear_on_submit=True):
        nome = st.text_input("Nome", key="cad_nome")
        cargo = st.text_input("Cargo", key="cad_cargo")

        tipo_entrega = st.selectbox(
            "Função de entrega",
            ["Não se aplica", "Entrega"],
            key="cad_tipo_entrega"
        )

        turno = st.selectbox(
            "Turno",
            ["Manhã", "Tarde", "Noite"],
            key="cad_turno"
        )

        ativo = st.checkbox("Ativo", value=True, key="cad_ativo")

        salvar = st.form_submit_button("Salvar funcionário")

        if salvar:
            nome_limpo = nome.strip()
            cargo_limpo = cargo.strip()

            if not nome_limpo or not cargo_limpo:
                st.error("Preencha nome e cargo.")
                return

            payload = {
                "nome": nome_limpo,
                "cargo": cargo_limpo,
                "ativo": ativo,
                "tipo_entrega": tipo_entrega,
                "turno": turno
            }

            try:
                response = requests.post(
                    f"{API_URL}/funcionarios",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    st.success(f"Funcionário {nome_limpo} cadastrado com sucesso.")
                else:
                    st.error(f"Erro ao cadastrar: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")
