import streamlit as st


def render_regras(API_URL: str):
    st.subheader("Regras de Negócio")

    st.markdown("""
    <div class="card-item">
        <strong>Assiduidade mensal</strong><br>
        Todo funcionário começa o mês com <span class="valor-bonus">R$ 150,00</span> de assiduidade.
        Se tiver qualquer ausência no mês, perde o valor de assiduidade.
    </div>

    <div class="card-item">
        <strong>Regra por turno</strong><br>
        Manhã recebe apenas por toneladas.
        <br>• Toneladas: <span class="valor-bonus">R$ 2,00</span> por tonelada
        <br><br>
        Tarde recebe apenas por pedidos separados.
        <br>• Pedidos separados: <span class="valor-bonus">R$ 0,10</span> por pedido
        <br><br>
        Noite recebe apenas por pedidos carregados.
        <br>• Pedidos carregados: <span class="valor-bonus">R$ 0,10</span> por pedido
        <br><br>
        Horário comercial recebe apenas assiduidade.
    </div>

    <div class="card-item">
        <strong>Funcionários de entrega</strong><br>
        Motorista e ajudante de motorista ficam agrupados na opção única <strong>Entrega</strong>.
    </div>

    <div class="card-item">
        <strong>Nota de desempenho</strong><br>
        A nota altera o valor da bonificação:
        <br>• Nota 5: 100%
        <br>• Nota 4: 90%
        <br>• Nota 3: 80%
        <br>• Nota 2: 50%
        <br>• Nota 1: 20%
    </div>

    <div class="card-item">
        <strong>Penalidade de 50%</strong><br>
        Quando marcada, a bonificação é reduzida pela metade.
        O sistema exige informar o motivo da penalidade.
    </div>
    """, unsafe_allow_html=True)
