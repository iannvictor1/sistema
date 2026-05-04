import requests
import streamlit as st
from utils import API_URL

def render_historico_lancamentos(API_URL: str):
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