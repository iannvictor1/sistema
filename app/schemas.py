from pydantic import BaseModel
from datetime import date
from typing import Optional


class FuncionarioCreate(BaseModel):
    nome: str
    cargo: str
    ativo: bool = True
    tipo_entrega: str
    turno: str = "Não informado"

class FuncionarioResponse(BaseModel):
    id: int
    nome: str
    cargo: str
    ativo: bool
    tipo_entrega: str
    turno: str = "Não informado"

    class Config:
        from_attributes = True

class FuncionarioUpdate(BaseModel):
    nome: str
    cargo: str
    ativo: bool = True
    tipo_entrega: str
    turno: str = "Não informado"

class LancamentoSemanalCreate(BaseModel):
    funcionario_id: int
    semana: str
    tipo_lancamento: str = "semanal"
    data_lancamento: Optional[date] = None
    usuario_lancamento: Optional[str] = None
    numero_nota_fiscal: str | None = None
    nota_fiscal_pdf: str | None = None
    nota_fiscal_pdf_nome: str | None = None
    pedidos_separados: int = 0
    pedidos_carregados: int = 0
    toneladas: float = 0
    numero_carregamento: str | None = None
    entregas: int = 0
    retornos: int = 0
    nota: int
    penalidade: bool = False
    motivo_penalidade: str | None = None
    ajuste_personalizado_descricao: str | None = None
    ajuste_personalizado_operacao: str | None = None
    ajuste_personalizado_valor: float = 0
    ajuste_personalizado_itens: str | None = None


class LancamentoMensalCreate(BaseModel):
    mes: str
    filtro_turno: str
    tipo_funcionario: str
    usuario_lancamento: Optional[str] = None
    pedidos_separados: int = 0
    pedidos_carregados: int = 0
    toneladas: float = 0
    entregas: int = 0
    retornos: int = 0
    notas: dict[int, int]


class LancamentoSemanalResponse(BaseModel):
    id: int
    funcionario_id: int
    semana: str

    tipo_lancamento: str = "semanal"
    data_lancamento: Optional[date] = None
    data_registro: Optional[date] = None
    usuario_lancamento: Optional[str] = None

    pedidos_separados: int
    pedidos_carregados: int
    toneladas: float
    numero_carregamento: str | None = None
    numero_nota_fiscal: str | None = None
    nota_fiscal_pdf_nome: str | None = None
    nota_fiscal_pdf_disponivel: bool = False
    entregas: int
    retornos: int
    nota: int
    penalidade: bool
    motivo_penalidade: str | None = None
    ajuste_personalizado_descricao: str | None = None
    ajuste_personalizado_operacao: str | None = None
    ajuste_personalizado_valor: float = 0
    ajuste_personalizado_itens: str | None = None
    bonus_calculado: float

    class Config:
        from_attributes = True

class LancamentoSemanalUpdate(BaseModel):
    semana: str
    data_lancamento: Optional[date] = None
    pedidos_separados: int = 0
    pedidos_carregados: int = 0
    toneladas: float = 0
    numero_carregamento: str | None = None
    numero_nota_fiscal: str | None = None
    nota_fiscal_pdf: str | None = None
    nota_fiscal_pdf_nome: str | None = None
    entregas: int = 0
    retornos: int = 0
    nota: int
    penalidade: bool = False
    motivo_penalidade: str | None = None
    ajuste_personalizado_descricao: str | None = None
    ajuste_personalizado_operacao: str | None = None
    ajuste_personalizado_valor: float = 0
    ajuste_personalizado_itens: str | None = None


class RecebimentoToneladasCreate(BaseModel):
    semana: str
    data_lancamento: Optional[date] = None
    usuario_lancamento: Optional[str] = None
    toneladas: float
    numero_carregamento: str | None = None
    numero_nota_fiscal: str | None = None
    nota_fiscal_pdf: str | None = None
    nota_fiscal_pdf_nome: str | None = None


class RecebimentoToneladasUpdate(BaseModel):
    semana: str
    data_lancamento: Optional[date] = None
    toneladas: float
    numero_carregamento: str | None = None
    numero_nota_fiscal: str | None = None
    nota_fiscal_pdf: str | None = None
    nota_fiscal_pdf_nome: str | None = None


class RecebimentoToneladasResponse(BaseModel):
    id: int
    semana: str
    data_lancamento: Optional[date] = None
    data_registro: Optional[date] = None
    usuario_lancamento: Optional[str] = None
    toneladas: float
    numero_carregamento: str | None = None
    numero_nota_fiscal: str | None = None
    nota_fiscal_pdf_nome: str | None = None
    nota_fiscal_pdf_disponivel: bool = False
    status: str
    participantes: str | None = None

    class Config:
        from_attributes = True


class RecebimentoParticipantesUpdate(BaseModel):
    funcionario_ids: list[int]
    usuario_lancamento: Optional[str] = None


class FrequenciaMensalCreate(BaseModel):
    funcionario_id: int
    mes: str
    ausencias: int
    data_falta: Optional[date] = None
    tipo_falta: str | None = None
    status_mes: str = "Normal"


class FrequenciaMensalResponse(BaseModel):
    id: int
    funcionario_id: int
    mes: str
    ausencias: int
    data_falta: Optional[date] = None
    tipo_falta: str | None = None
    status_mes: str = "Normal"

    class Config:
        from_attributes = True


class DescontoFechamentoCreate(BaseModel):
    funcionario_id: int
    mes: str
    valor: float
    motivo: str | None = None


class DescontoFechamentoResponse(BaseModel):
    id: int
    funcionario_id: int
    mes: str
    valor: float
    motivo: str | None = None

    class Config:
        from_attributes = True
