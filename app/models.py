from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from .database import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    tipo_entrega = Column(String, default="Não se aplica")
    turno = Column(String, default="Não informado")


class LancamentoSemanal(Base):
    __tablename__ = "lancamentos_semanais"

    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    
    semana = Column(String, nullable=False)
    tipo_lancamento = Column(String, default="semanal")
    data_lancamento = Column(Date, nullable=True)
    data_registro = Column(Date, nullable=True)
    usuario_lancamento = Column(String, nullable=True)
    
    pedidos_separados = Column(Integer, default=0)
    pedidos_carregados = Column(Integer, default=0)
    toneladas = Column(Float, default=0)
    entregas = Column(Integer, default=0)
    retornos = Column(Integer, default=0)
    nota = Column(Integer, default=3)
    penalidade = Column(Boolean, default=False)
    motivo_penalidade = Column(String, nullable=True)
    ajuste_personalizado_descricao = Column(String, nullable=True)
    ajuste_personalizado_operacao = Column(String, nullable=True)
    ajuste_personalizado_valor = Column(Float, default=0)
    ajuste_personalizado_itens = Column(String, nullable=True)
    bonus_calculado = Column(Float, default=0)


class FrequenciaMensal(Base):
    __tablename__ = "frequencias_mensais"

    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    mes = Column(String, nullable=False) 
    ausencias = Column(Integer, default=0)
    data_falta = Column(Date, nullable=True)
    tipo_falta = Column(String, nullable=True)
    status_mes = Column(String, default="Normal")  


class DescontoFechamento(Base):
    __tablename__ = "descontos_fechamento"

    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    mes = Column(String, nullable=False)
    valor = Column(Float, default=0)
    motivo = Column(String, nullable=True)
