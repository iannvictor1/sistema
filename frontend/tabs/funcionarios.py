import requests
import streamlit as st


def render_funcionarios(API_URL: str):
    st.subheader("Funcionários Cadastrados")

    if st.button("Atualizar lista", key="btn_atualizar_funcionarios"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)

        if response.status_code != 200:
            st.error("Erro ao buscar funcionários.")
            return

        funcionarios = response.json()

        if not funcionarios:
            st.info("Nenhum funcionário cadastrado ainda.")
            return

        for f in funcionarios:
            badge = (
                '<span class="badge-sim">Ativo</span>'
                if f["ativo"]
                else '<span class="badge-nao">Inativo</span>'
            )

            entrega = f.get("tipo_entrega", "Não se aplica")
            turno = f.get("turno", "Não informado")

            st.markdown(f"""
            <div class="card-item">
                <strong>#{f['id']}</strong> &nbsp;·&nbsp;
                <strong>{f['nome']}</strong> &nbsp;·&nbsp;
                <span style="color:#9A9690">{f['cargo']}</span>
                &nbsp;·&nbsp;
                <span style="color:#9A9690">Turno: {turno}</span>
                &nbsp;·&nbsp;
                <span style="color:#9A9690">Entrega: {entrega}</span>
                &nbsp;&nbsp;{badge}
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"✏️ Editar funcionário #{f['id']} - {f['nome']}"):
                novo_nome = st.text_input(
                    "Nome",
                    value=f["nome"],
                    key=f"edit_func_nome_{f['id']}"
                )

                novo_cargo = st.text_input(
                    "Cargo",
                    value=f["cargo"],
                    key=f"edit_func_cargo_{f['id']}"
                )

                opcoes_entrega = [
                    "Não se aplica",
                    "Motorista",
                    "Ajudante de motorista"
                ]

                tipo_atual = f.get("tipo_entrega", "Não se aplica")
                index_tipo = opcoes_entrega.index(tipo_atual) if tipo_atual in opcoes_entrega else 0

                novo_tipo_entrega = st.selectbox(
                    "Função de entrega",
                    opcoes_entrega,
                    index=index_tipo,
                    key=f"edit_func_tipo_entrega_{f['id']}"
                )

                opcoes_turno = ["Manhã", "Tarde", "Noite"]
                turno_atual = f.get("turno", "Manhã")
                index_turno = opcoes_turno.index(turno_atual) if turno_atual in opcoes_turno else 0

                novo_turno = st.selectbox(
                    "Turno",
                    opcoes_turno,
                    index=index_turno,
                    key=f"edit_func_turno_{f['id']}"
                )

                novo_ativo = st.checkbox(
                    "Ativo",
                    value=bool(f["ativo"]),
                    key=f"edit_func_ativo_{f['id']}"
                )

                if st.button("Salvar alterações", key=f"btn_salvar_func_{f['id']}"):
                    if not novo_nome.strip() or not novo_cargo.strip():
                        st.error("Nome e cargo não podem ficar vazios.")
                    else:
                        payload = {
                            "nome": novo_nome.strip(),
                            "cargo": novo_cargo.strip(),
                            "ativo": novo_ativo,
                            "tipo_entrega": novo_tipo_entrega,
                            "turno": novo_turno
                        }

                        resp_edit = requests.put(
                            f"{API_URL}/funcionarios/{f['id']}",
                            json=payload,
                            timeout=10
                        )

                        if resp_edit.status_code == 200:
                            st.success("Funcionário atualizado com sucesso.")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar funcionário: {resp_edit.text}")

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")
