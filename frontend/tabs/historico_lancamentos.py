import requests
import streamlit as st
from datetime import date
from utils import API_URL
from utils import gerar_semana_mes


def _rotulo_tipo_entrega(tipo_entrega: str) -> str:
    if tipo_entrega in ["Motorista", "Ajudante de motorista"]:
        return "Entrega"
    return tipo_entrega or "Não se aplica"


def render_historico_lancamentos(API_URL: str):
    st.subheader("Lançamentos")

    col_filtro, col_btn = st.columns([2, 1])

    with col_filtro:
        col_mes, col_dia = st.columns(2)

    with col_mes:
        data_filtro = st.date_input(
            "Filtrar por mês",
            value=date.today(),
            key="filtro_mes_lancamentos"
        )

    with col_dia:
        filtro_data = st.date_input(
            "Filtrar por dia",
            value=None,
            key="filtro_data_lancamentos"
        )

    with col_btn:
        st.write("")
        if st.button("Atualizar lista", key="btn_atualizar_lancamentos"):
            st.rerun()

    mes_ano = data_filtro.strftime("%m/%Y")

    try:
        resp_lanc = requests.get(f"{API_URL}/lancamentos-semanais", timeout=10)
        resp_func = requests.get(f"{API_URL}/funcionarios", timeout=10)

        if resp_lanc.status_code == 200 and resp_func.status_code == 200:
            lancamentos = resp_lanc.json()
            funcionarios = resp_func.json()

            mapa_funcionarios = {f["id"]: f for f in funcionarios}

            col_nome, col_tipo, col_turno = st.columns(3)

            with col_nome:
                filtro_nome = st.text_input(
                    "Filtrar por funcionário",
                    key="filtro_nome_lancamentos"
                )

            with col_tipo:
                filtro_tipo = st.selectbox(
                    "Tipo de lançamento",
                    ["Todos", "Mensal", "Semanal", "Diário"],
                    key="filtro_tipo_lancamentos"
                )

            with col_turno:
                filtro_turno = st.selectbox(
                    "Turno",
                    ["Todos", "Manhã", "Tarde", "Noite", "Horário comercial"],
                    key="filtro_turno_lancamentos"
                )

            col_valor_min, col_valor_max = st.columns(2)

            with col_valor_min:
                filtro_valor_min = st.number_input(
                    "Valor mínimo",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    key="filtro_valor_min_lancamentos"
                )

            with col_valor_max:
                filtro_valor_max = st.number_input(
                    "Valor máximo",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    key="filtro_valor_max_lancamentos"
                )

            lancamentos_filtrados = []

            for l in lancamentos:
                semana = l.get("semana", "")
                data_lancamento = l.get("data_lancamento")

                corresponde_mes = mes_ano in semana

                corresponde_dia = True

                if filtro_data:
                    corresponde_dia = (
                        data_lancamento == filtro_data.strftime("%Y-%m-%d")
                    )

                funcionario = mapa_funcionarios.get(l["funcionario_id"], {})
                nome_funcionario = funcionario.get("nome", "")
                turno_funcionario = funcionario.get("turno", "")
                tipo_lancamento = l.get("tipo_lancamento", "semanal")
                valor_bonus = float(l.get("bonus_calculado", 0))

                corresponde_nome = (
                    not filtro_nome.strip()
                    or filtro_nome.strip().lower() in nome_funcionario.lower()
                )
                corresponde_tipo = (
                    filtro_tipo == "Todos"
                    or tipo_lancamento == filtro_tipo.lower().replace("á", "a")
                )
                corresponde_turno = (
                    filtro_turno == "Todos"
                    or turno_funcionario == filtro_turno
                )
                corresponde_valor = (
                    valor_bonus >= filtro_valor_min
                    and (filtro_valor_max == 0 or valor_bonus <= filtro_valor_max)
                )

                if (
                    corresponde_mes
                    and corresponde_dia
                    and corresponde_nome
                    and corresponde_tipo
                    and corresponde_turno
                    and corresponde_valor
                ):
                    lancamentos_filtrados.append(l)

            if not lancamentos_filtrados:
                st.info(f"Nenhum lançamento encontrado para {mes_ano}.")
                return

            opcoes_exclusao = {}
            for l in lancamentos_filtrados:
                funcionario = mapa_funcionarios.get(l["funcionario_id"], {})
                nome_funcionario = funcionario.get("nome", f"Funcionário #{l['funcionario_id']}")
                opcoes_exclusao[
                    f"#{l['id']} - {nome_funcionario} - R$ {float(l.get('bonus_calculado', 0)):.2f}"
                ] = l["id"]

            selecionados_exclusao = st.multiselect(
                "Selecionar lançamentos para excluir",
                list(opcoes_exclusao.keys()),
                key="lancamentos_para_excluir"
            )

            col_confirmar, col_excluir = st.columns([2, 1])

            with col_confirmar:
                confirmar_exclusao = st.checkbox(
                    "Confirmar exclusão dos selecionados",
                    key="confirmar_excluir_lancamentos_selecionados"
                )

            with col_excluir:
                st.write("")
                if st.button("Excluir selecionados", key="btn_excluir_lancamentos_selecionados"):
                    if not selecionados_exclusao:
                        st.warning("Selecione pelo menos um lançamento.")
                    elif not confirmar_exclusao:
                        st.warning("Marque a confirmação antes de excluir.")
                    else:
                        erros = []

                        for label in selecionados_exclusao:
                            lancamento_id = opcoes_exclusao[label]
                            resp_del = requests.delete(
                                f"{API_URL}/lancamentos-semanais/{lancamento_id}",
                                timeout=10
                            )

                            if resp_del.status_code != 200:
                                erros.append(label)

                        if erros:
                            st.error(f"Erro ao excluir: {', '.join(erros)}")
                        else:
                            st.success(f"{len(selecionados_exclusao)} lançamento(s) excluído(s) com sucesso.")
                            st.rerun()

            for l in lancamentos_filtrados:
                funcionario = mapa_funcionarios.get(l["funcionario_id"], {})
                nome_funcionario = funcionario.get("nome", f"Funcionário #{l['funcionario_id']}")
                cargo_funcionario = funcionario.get("cargo", "-")
                tipo_entrega = _rotulo_tipo_entrega(funcionario.get("tipo_entrega", "Não se aplica"))
                turno_funcionario = funcionario.get("turno", "Não informado")

                tipo_lancamento = l.get("tipo_lancamento", "semanal")
                data_escolhida = l.get("data_lancamento") or "—"
                usuario = l.get("usuario_lancamento") or "—"

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
                    <span style="color:#9A9690"> · {cargo_funcionario} · {turno_funcionario} · {tipo_entrega}</span>
                    <br>
                    Tipo: <strong>{tipo_lancamento}</strong>
                    &nbsp;·&nbsp; Semana <strong>{l['semana']}</strong>
                    &nbsp;·&nbsp; Data escolhida: <strong>{data_escolhida}</strong>
                    &nbsp;·&nbsp; Usuário: <strong>{usuario}</strong>
                    <br>
                    {pen_badge}
                    &nbsp;·&nbsp; Motivo: <span style="color:#9A9690">{motivo}</span>
                    &nbsp;&nbsp;<span class="valor-bonus">R$ {l['bonus_calculado']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"Editar lançamento #{l['id']} - {nome_funcionario}"):
                    if tipo_lancamento == "diario":

                        nova_data = st.date_input(
                            "Data do lançamento",
                            value=date.fromisoformat(l["data_lancamento"])
                            if l.get("data_lancamento")
                            else date.today(),
                            key=f"edit_data_{l['id']}"
                        )

                        nova_semana = gerar_semana_mes(nova_data)

                    else:

                        nova_semana = st.text_input(
                            "Semana",
                            value=l["semana"],
                            key=f"edit_semana_{l['id']}"
                        )

                    novas_entregas = 0
                    novos_retornos = 0
                    novos_pedidos_sep = 0
                    novos_pedidos_car = 0
                    novas_toneladas = 0.0

                    if turno_funcionario == "Manhã":
                        col1, col2 = st.columns(2)

                        with col1:
                            novas_toneladas = st.number_input(
                                "Toneladas",
                                min_value=0.0,
                                value=float(l["toneladas"]),
                                step=0.1,
                                key=f"edit_ton_{l['id']}"
                            )

                        with col2:
                            nova_nota = st.selectbox(
                                "Nota",
                                [1, 2, 3, 4, 5],
                                index=[1, 2, 3, 4, 5].index(int(l["nota"])),
                                key=f"edit_nota_{l['id']}"
                            )
                    elif turno_funcionario == "Tarde":
                        col1, col2 = st.columns(2)

                        with col1:
                            novos_pedidos_sep = st.number_input(
                                "Pedidos separados",
                                min_value=0,
                                value=int(l["pedidos_separados"]),
                                key=f"edit_sep_{l['id']}"
                            )

                        with col2:
                            nova_nota = st.selectbox(
                                "Nota",
                                [1, 2, 3, 4, 5],
                                index=[1, 2, 3, 4, 5].index(int(l["nota"])),
                                key=f"edit_nota_{l['id']}"
                            )
                    elif turno_funcionario == "Noite":
                        col1, col2 = st.columns(2)

                        with col1:
                            novos_pedidos_car = st.number_input(
                                "Pedidos carregados",
                                min_value=0,
                                value=int(l["pedidos_carregados"]),
                                key=f"edit_car_{l['id']}"
                            )

                        with col2:
                            nova_nota = st.selectbox(
                                "Nota",
                                [1, 2, 3, 4, 5],
                                index=[1, 2, 3, 4, 5].index(int(l["nota"])),
                                key=f"edit_nota_{l['id']}"
                            )
                    elif turno_funcionario == "Horário comercial":
                        nova_nota = int(l["nota"])
                        st.info("Este turno recebe apenas assiduidade no fechamento mensal.")
                    else:
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            novas_toneladas = st.number_input(
                                "Toneladas",
                                min_value=0.0,
                                value=float(l["toneladas"]),
                                step=0.1,
                                key=f"edit_ton_{l['id']}"
                            )

                        with col2:
                            novos_pedidos_sep = st.number_input(
                                "Pedidos separados",
                                min_value=0,
                                value=int(l["pedidos_separados"]),
                                key=f"edit_sep_{l['id']}"
                            )

                        with col3:
                            novos_pedidos_car = st.number_input(
                                "Pedidos carregados",
                                min_value=0,
                                value=int(l["pedidos_carregados"]),
                                key=f"edit_car_{l['id']}"
                            )

                        with col4:
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
                                    "data_lancamento": str(nova_data) if tipo_lancamento == "diario" else l.get("data_lancamento"),
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
            st.error("Erro ao buscar lançamentos ou funcionários.")

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")
