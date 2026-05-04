import requests
import streamlit as st

def render_cadastro(API_URL: str):
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