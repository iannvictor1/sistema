import requests
import streamlit as st

def render_fechamento(API_URL: str):
    st.subheader("Fechamento Mensal")

    data_fechamento = st.date_input("Mês para fechamento", key="fech_data")
    mes_fechamento = data_fechamento.strftime("%Y-%m")

    if st.button("Calcular fechamento mensal", key="btn_calcular_fechamento"):
        try:
            response = requests.get(f"{API_URL}/fechamento/{mes_fechamento}", timeout=10)

            if response.status_code == 200:
                dados = response.json()

                if dados:
                    for d in dados:
                        elegivel = d["elegivel"]
                        if d.get("status_mes") == "Férias":
                            status_badge = '<span class="badge-pendente">Férias</span>'
                        elif elegivel:
                            status_badge = '<span class="badge-elegivel">Elegível</span>'
                        else:
                            status_badge = '<span class="badge-eliminado">Eliminado por ausência</span>'
                        bonus_class = "valor-bonus" if elegivel else ""

                        st.markdown(f"""
                        <div class="card-item">
                            <strong>{d['funcionario']}</strong>
                            <span style="color:#9A9690"> · {d['cargo']}</span>
                            &nbsp;&nbsp;{status_badge}
                            <br>
                            <span style="font-size:0.82rem; color:#777; margin-top:6px; display:block">
                                Ausências: <strong style="color:#C8C0AC">{d['ausencias']}</strong>
                                &nbsp;·&nbsp; Lançamentos: <strong style="color:#C8C0AC">{d['quantidade_lancamentos']}</strong>
                                &nbsp;·&nbsp; Assiduidade: <strong style="color:#C8C0AC">R$ {d['assiduidade']:.2f}</strong>
                                &nbsp;·&nbsp; Bônus final: <span class="{bonus_class}">R$ {d['bonus_final']:.2f}</span>
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhum dado encontrado para o mês informado.")
            else:
                st.error(f"Erro no fechamento: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")

    st.markdown("---")
    st.subheader("Exportar Excel")

    if st.button("Baixar Excel do fechamento", key="btn_baixar_excel_fechamento"):
        try:
            response = requests.get(f"{API_URL}/exportar-fechamento/{mes_fechamento}", timeout=30)

            if response.status_code == 200:
                st.download_button(
                    label="⬇ Clique aqui para baixar o arquivo Excel",
                    data=response.content,
                    file_name=f"fechamento_{mes_fechamento}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel_fechamento"
                )
            else:
                st.error(f"Erro ao exportar Excel: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao backend. Verifique se o FastAPI está rodando.")
