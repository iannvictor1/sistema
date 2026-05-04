import requests
import streamlit as st

def render_regras(API_URL: str):
    st.subheader("Regras de Negócio")
    
    st.markdown("""
    <div class="car-item">
        <strong>Assiduida mensal</strong><br>
        Todo funcionário começa o mês com <span class="valor-bonus">R$ 150,00</span> de assiduidade.
        Se tiver qualquer ausência no mês, perde o valor de assiduidade.
    </div>
    
    <div class="card-item">
        <strong>Funcionários comuns</strong><br>
        Recebem por:
        <br>• Pedidos separados: <span class="valor-bonus">R$ 0,10</span> por pedido
        <br>• Pedidos carregados: <span class="valor-bonus">R$ 0,10</span> por pedido
        <br>• Toneladas: <span class="valor-bonus">R$ 2,00</span> por tonelada
    </div>
    
    <div class="card-item">
        <strong>Motoristas e ajudantes de motorista</strong><br>
        Recebem apenas por entregas e retornos:
        <br>• Entregas: <span class="valor-bonus">R$0,30</span> por entrega
        <br>• Retornos: desconto de <span class="valor-bonus">R$ 0,60</span> por retorno
    </div>
    
    <div class="car-item">
        <strong>Nota de desempenho</strong><br>
        A nota altera o valor da bonificação semanal:
        <br>• Nota 5: 100%
        <br>• Nota 4: 90%
        <br>• Nota 3: 80%
        <br>• Nota 2: 50%
        <br>• Nota 1: 20%
    </div>
    
    <div class="card-item">
        <strong>Penalidade de 50%</strong><br>
        Quando marcada, a bonificicação semanal é reduzida pela metade.
        O sistema exige informar o motivo da penalidade.
    </div>
    
    <div class="card-item">
        <strong>Exemplo 1 - Funcionário comum</strong><br>
        Pedidos eparados: 100 x R$ 0,10 = R$ 10,00<br>
        Pedidos carregados: 40 x R$ 0,10 = R$ 4,00<br>
        Toneladas: 20 x R$ 2,00 = R$ 40,00<br>
        Total: R$ 54,00<br>
        Nota 5: <span class="valor-bonus">R$ 54,00</span>
    </div>
    
    <div class="card-item">
        <strong>Exemplo 2 — Motorista/Ajudante</strong><br>
        Entregas: 50 × R$ 0,30 = R$ 15,00<br>
        Retornos: 10 × R$ 0,60 = R$ 6,00<br>
        Base: R$ 15,00 - R$ 6,00 = R$ 9,00<br>
        Nota 5: <span class="valor-bonus">R$ 9,00</span>
    </div>
    """, unsafe_allow_html=True)
    
        
    
    
    
    