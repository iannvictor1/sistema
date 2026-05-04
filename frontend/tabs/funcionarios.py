import requests
import streamlit as st

def render_funcionarios(API_URL: str):
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