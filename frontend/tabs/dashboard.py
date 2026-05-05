import requests
import streamlit as st
from datetime import date


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

        if (
            resp_fechamento.status_code != 200
            or resp_lancamentos.status_code != 200
            or resp_funcionarios.status_code != 200
        ):
            st.error("Erro ao carregar dados do dashboard.")
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
            if mes_ano in l.get("semana", "")
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