import requests
import streamlit as st


def _rotulo_tipo_entrega(tipo_entrega: str) -> str:
    if tipo_entrega in ["Motorista", "Ajudante de motorista"]:
        return "Entrega"
    return tipo_entrega or "Não se aplica"


def render_funcionarios(API_URL: str):
    st.subheader("Funcionários Cadastrados")

    col_busca, col_atualizar = st.columns([3, 1])

    with col_busca:
        busca_funcionario = st.text_input(
            "Pesquisar funcionário",
            key="busca_funcionarios"
        )

    with col_atualizar:
        st.write("")
        if st.button("Atualizar lista", key="btn_atualizar_funcionarios"):
            st.rerun()

    try:
        response = requests.get(f"{API_URL}/funcionarios", timeout=10)

        if response.status_code != 200:
            st.error("Erro ao buscar funcionários.")
            return

        funcionarios = response.json()
        termo_busca = busca_funcionario.strip().lower()

        if termo_busca:
            funcionarios = [
                f for f in funcionarios
                if termo_busca in f.get("nome", "").lower()
                or termo_busca in f.get("cargo", "").lower()
                or termo_busca in f.get("turno", "").lower()
                or termo_busca in f.get("tipo_entrega", "").lower()
            ]

        if not funcionarios:
            st.info("Nenhum funcionário encontrado.")
            return

        opcoes_exclusao = {
            f"{f['nome']} - {f['cargo']} - {f.get('turno', 'Não informado')} (ID {f['id']})": f["id"]
            for f in funcionarios
        }

        selecionados_exclusao = st.multiselect(
            "Selecionar funcionários para excluir",
            list(opcoes_exclusao.keys()),
            key="funcionarios_para_excluir"
        )

        col_confirmar, col_excluir = st.columns([2, 1])

        with col_confirmar:
            confirmar_exclusao = st.checkbox(
                "Confirmar exclusão dos selecionados",
                key="confirmar_excluir_funcionarios_selecionados"
            )

        with col_excluir:
            st.write("")
            if st.button("Excluir selecionados", key="btn_excluir_funcionarios_selecionados"):
                if not selecionados_exclusao:
                    st.warning("Selecione pelo menos um funcionário.")
                elif not confirmar_exclusao:
                    st.warning("Marque a confirmação antes de excluir.")
                else:
                    erros = []

                    for label in selecionados_exclusao:
                        funcionario_id = opcoes_exclusao[label]
                        resp_del = requests.delete(
                            f"{API_URL}/funcionarios/{funcionario_id}",
                            timeout=10
                        )

                        if resp_del.status_code != 200:
                            erros.append(label)

                    if erros:
                        st.error(f"Erro ao excluir: {', '.join(erros)}")
                    else:
                        st.success(f"{len(selecionados_exclusao)} funcionário(s) excluído(s) com sucesso.")
                        st.rerun()

        for f in funcionarios:
            badge = (
                '<span class="badge-sim">Ativo</span>'
                if f["ativo"]
                else '<span class="badge-nao">Inativo</span>'
            )

            entrega = _rotulo_tipo_entrega(f.get("tipo_entrega", "Não se aplica"))
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

            with st.expander(f"Editar funcionário #{f['id']} - {f['nome']}"):
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
                    "Entrega"
                ]

                tipo_atual = _rotulo_tipo_entrega(f.get("tipo_entrega", "Não se aplica"))
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
