import requests
import streamlit as st
from datetime import date


def _lancamento_pertence_ao_mes(lancamento: dict, mes_api: str, mes_semana: str) -> bool:
    data_lancamento = lancamento.get("data_lancamento")
    if data_lancamento and str(data_lancamento).startswith(mes_api):
        return True

    return mes_semana in lancamento.get("semana", "")


def render_dashboard(API_URL: str):
    st.subheader("Dashboard do Mês")

    data_filtro = st.date_input(
        "Mês de referência",
        value=date.today(),
        key="dashboard_mes"
    )

    mes = data_filtro.strftime("%Y-%m")
    mes_ano = data_filtro.strftime("%m/%Y")

    try:
        resp_fechamento = requests.get(f"{API_URL}/fechamento/{mes}", timeout=10)
        resp_lancamentos = requests.get(f"{API_URL}/lancamentos-semanais", timeout=10)
        resp_funcionarios = requests.get(f"{API_URL}/funcionarios", timeout=10)

        respostas = {
            "fechamento": resp_fechamento,
            "lançamentos": resp_lancamentos,
            "funcionários": resp_funcionarios,
        }
        erros = [
            f"{nome}: HTTP {resp.status_code} - {resp.text[:250]}"
            for nome, resp in respostas.items()
            if resp.status_code != 200
        ]

        if erros:
            if all(resp.status_code == 404 for resp in respostas.values()):
                st.error(
                    "O dashboard encontrou outro servico ou uma versao antiga do backend na porta 8000. "
                    "Feche o sistema, encerre processos antigos se houver, e abra novamente."
                )
            else:
                st.error("Erro ao carregar dados do dashboard.")
            with st.expander("Detalhes técnicos"):
                st.code("\n".join(erros))
            return

        fechamento = resp_fechamento.json()
        lancamentos = resp_lancamentos.json()
        funcionarios = resp_funcionarios.json()

        opcoes_funcionarios = {"Todos": None}

        for f in funcionarios:
            opcoes_funcionarios[f"{f['nome']} - {f['cargo']} (ID {f['id']})"] = f["id"]

        funcionario_filtro_label = st.selectbox(
            "Filtrar por funcionário",
            list(opcoes_funcionarios.keys()),
            key="dashboard_funcionario"
        )

        funcionario_filtro_id = opcoes_funcionarios[funcionario_filtro_label]

        lancamentos_mes = [
            l for l in lancamentos
            if _lancamento_pertence_ao_mes(l, mes, mes_ano)
        ]

        if funcionario_filtro_id is not None:
            lancamentos_mes = [
                l for l in lancamentos_mes
                if l.get("funcionario_id") == funcionario_filtro_id
            ]

            fechamento = [
                item for item in fechamento
                if item.get("funcionario_id") == funcionario_filtro_id
            ]

            funcionarios_ativos = [
                f for f in funcionarios
                if f.get("id") == funcionario_filtro_id and f.get("ativo", True)
            ]
        else:
            funcionarios_ativos = [
                f for f in funcionarios
                if f.get("ativo", True)
            ]

        total_bonus = sum(float(item.get("bonus_final", 0)) for item in fechamento)
        total_assiduidade = sum(float(item.get("assiduidade", 0)) for item in fechamento)
        bloqueados = sum(1 for item in fechamento if not item.get("elegivel", True))
        elegiveis = sum(1 for item in fechamento if item.get("elegivel", False))

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Funcionários ativos", len(funcionarios_ativos))
        col2.metric("Lançamentos no mês", len(lancamentos_mes))
        col3.metric("Total bônus", f"R$ {total_bonus:.2f}")
        col4.metric("Bloqueados por falta", bloqueados)

        st.divider()

        col5, col6 = st.columns(2)

        with col5:
            st.markdown("### Resumo de elegibilidade")
            st.write(f"✅ Elegíveis: **{elegiveis}**")
            st.write(f"❌ Bloqueados: **{bloqueados}**")
            st.write(f"🎁 Total assiduidade: **R$ {total_assiduidade:.2f}**")

        with col6:
            st.markdown("### Lançamentos por tipo")

            diarios = [
                l for l in lancamentos_mes
                if l.get("tipo_lancamento") == "diario"
            ]

            semanais = [
                l for l in lancamentos_mes
                if l.get("tipo_lancamento", "semanal") != "diario"
            ]

            st.write(f"📅 Semanais: **{len(semanais)}**")
            st.write(f"🗓️ Diários: **{len(diarios)}**")

        st.divider()

        st.markdown("### Top funcionários por bônus")

        ranking = sorted(
            fechamento,
            key=lambda x: float(x.get("bonus_final", 0)),
            reverse=True
        )

        if ranking:
            for i, item in enumerate(ranking[:10], start=1):
                st.markdown(f"""
                <div class="card-item">
                    <strong>{i}º - {item['funcionario']}</strong>
                    <span style="color:#9A9690"> · {item['cargo']}</span>
                    <br>
                    Lançamentos: <strong>{item['quantidade_lancamentos']}</strong>
                    &nbsp;·&nbsp;
                    Ausências: <strong>{item['ausencias']}</strong>
                    &nbsp;·&nbsp;
                    Bônus: <span class="valor-bonus">R$ {item['bonus_final']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum dado encontrado para este mês.")

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao backend.")
    except requests.exceptions.RequestException as erro:
        st.error("Erro ao carregar dados do dashboard.")
        with st.expander("Detalhes técnicos"):
            st.code(str(erro))
