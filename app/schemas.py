from pydantic import BaseModel


class FuncionarioCreate(BaseModel):
    nome: str
    cargo: str
    ativo: bool = True
    tipo_entrega: str

class FuncionarioResponse(BaseModel):
    id: int
    nome: str
    cargo: str
    ativo: bool
    tipo_entrega: str

    class Config:
        from_attributes = True

class LancamentoSemanalCreate(BaseModel):
    funcionario_id: int
    semana: str
    pedidos_separados: int = 0
    pedidos_carregados: int = 0
    toneladas: float = 0
    entregas: int = 0
    retornos: int = 0
    nota: int
    penalidade: bool = False
    motivo_penalidade: str | None = None


class LancamentoSemanalResponse(BaseModel):
    id: int
    funcionario_id: int
    semana: str
    pedidos_separados: int
    pedidos_carregados: int
    toneladas: float
    entregas: int
    retornos: int
    nota: int
    penalidade: bool
    motivo_penalidade: str | None = None
    bonus_calculado: float

    class Config:
        from_attributes = True

class LancamentoSemanalUpdate(BaseModel):
    semana: str
    pedidos_separados: int = 0
    pedidos_carregados: int = 0
    toneladas: float = 0
    entregas: int = 0
    retornos: int = 0
    nota: int
    penalidade: bool = False
    motivo_penalidade: str | None = None

class FrequenciaMensalCreate(BaseModel):
    funcionario_id: int
    mes: str
    ausencias: int


class FrequenciaMensalResponse(BaseModel):
    id: int
    funcionario_id: int
    mes: str
    ausencias: int

    class Config:
        from_attributes = True