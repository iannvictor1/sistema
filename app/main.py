from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Funcionario, LancamentoSemanal, FrequenciaMensal
from .schemas import (
    FuncionarioCreate,
    FuncionarioResponse,
    LancamentoSemanalCreate,
    LancamentoSemanalResponse,
    FrequenciaMensalCreate,
    FrequenciaMensalResponse,
    LancamentoSemanalUpdate
)
from .calculos import calcular_bonus, calcular_bonus_mensal
from .export_excel import exportar_fechamento_excel

app = FastAPI(title="Sistema de Bonificação")

Base.metadata.create_all(bind=engine)

def formatar_mes_para_semana(mes: str) -> str:
    return f"{mes[5:7]}/{mes[:4]}"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"status": "Sistema rodando"}


@app.post("/funcionarios", response_model=FuncionarioResponse)
def criar_funcionario(funcionario: FuncionarioCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(Funcionario)
        .filter(
            Funcionario.nome == funcionario.nome,
            Funcionario.cargo == funcionario.cargo
        )
        .first()
    )

    if existente:
        raise HTTPException(status_code=400, detail="Funcionário já cadastrado com esse cargo.")

    novo = Funcionario(
        nome=funcionario.nome,
        cargo=funcionario.cargo,
        ativo=funcionario.ativo,
        tipo_entrega=funcionario.tipo_entrega
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/funcionarios", response_model=list[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    return db.query(Funcionario).order_by(Funcionario.nome).all()


@app.post("/lancamentos-semanais", response_model=LancamentoSemanalResponse)
def criar_lancamento_semanal(
    lancamento: LancamentoSemanalCreate,
    db: Session = Depends(get_db)
):
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == lancamento.funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    if lancamento.penalidade and not lancamento.motivo_penalidade:
        raise HTTPException(status_code=400, detail="Informe o motivo da penalidade.")

    if not lancamento.penalidade:
        motivo_penalidade = None
    else:
        motivo_penalidade = lancamento.motivo_penalidade

    bonus = calcular_bonus(
        tipo_entrega=funcionario.tipo_entrega,
        pedidos_separados=lancamento.pedidos_separados,
        pedidos_carregados=lancamento.pedidos_carregados,
        toneladas=lancamento.toneladas,
        entregas=lancamento.entregas,
        retornos=lancamento.retornos,
        nota=lancamento.nota,
        penalidade=lancamento.penalidade
    )

    novo = LancamentoSemanal(
        funcionario_id=lancamento.funcionario_id,
        semana=lancamento.semana,
        pedidos_separados=lancamento.pedidos_separados,
        pedidos_carregados=lancamento.pedidos_carregados,
        toneladas=lancamento.toneladas,
        entregas=lancamento.entregas,
        retornos=lancamento.retornos,
        nota=lancamento.nota,
        penalidade=lancamento.penalidade,
        motivo_penalidade=motivo_penalidade,
        bonus_calculado=bonus
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/lancamentos-semanais", response_model=list[LancamentoSemanalResponse])
def listar_lancamentos_semanais(db: Session = Depends(get_db)):
    return db.query(LancamentoSemanal).order_by(LancamentoSemanal.id.desc()).all()

@app.put("/lancamentos-semanais/{lancamento_id}", response_model=LancamentoSemanalResponse)
def editar_lancamento_semanal(
    lancamento_id: int,
    dados: LancamentoSemanalUpdate,
    db: Session = Depends(get_db)
):
    lancamento = (
        db.query(LancamentoSemanal)
        .filter(LancamentoSemanal.id == lancamento_id)
        .first()
    )
    
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.")
    
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == lancamento.funcionario_id)
        .first()
    )
    
    if not funcionario:
        raise HTTPException(status_code=404, detail= "Funcionário não encontrado.")
    
    if dados.penalidade and not dados.motivo_penalidade:
        raise HTTPException(status_code=400, detail="Informe o motivo da penalidade.")

    bonus = calcular_bonus(
        tipo_entrega=funcionario.tipo_entrega,
        pedidos_separados=dados.pedidos_separados,
        pedidos_carregados=dados.pedidos_carregados,
        toneladas=dados.toneladas,
        entregas=dados.entregas,
        retornos=dados.retornos,
        nota=dados.nota,
        penalidade=dados.penalidade
    )
        
    lancamento.semana = dados.semana
    lancamento.pedidos_separados = dados.pedidos_separados
    lancamento.pedidos_carregados = dados.pedidos_carregados
    lancamento.toneladas = dados.toneladas
    lancamento.entregas = dados.entregas
    lancamento.retornos = dados.retornos
    lancamento.nota = dados.nota
    lancamento.penalidade = dados.penalidade
    lancamento.motivo_penalidade = dados.motivo_penalidade if dados.penalidade else None
    lancamento.bonus_calculado = bonus
    
    db.commit()
    db.refresh(lancamento)
    return lancamento

@app.delete("/lancamentos-semanais/{lancamento_id}")
def excluir_lancamento_semanal(
    lancamento_id: int,
    db: Session = Depends(get_db)
):
    lancamento = (
        db.query(LancamentoSemanal)
        .filter(LancamentoSemanal.id == lancamento_id)
        .first()
    )
    
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.")
    
    db.delete(lancamento)
    db.commit()
    
    return {"mensagem": "Lançamento excluído com sucesso."}
        
@app.post("/frequencias", response_model=FrequenciaMensalResponse)
def criar_frequencia(frequencia: FrequenciaMensalCreate, db: Session = Depends(get_db)):
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == frequencia.funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    existente = (
        db.query(FrequenciaMensal)
        .filter(
            FrequenciaMensal.funcionario_id == frequencia.funcionario_id,
            FrequenciaMensal.mes == frequencia.mes
        )
        .first()
    )

    if existente:
        existente.ausencias = frequencia.ausencias
        db.commit()
        db.refresh(existente)
        return existente

    nova = FrequenciaMensal(
        funcionario_id=frequencia.funcionario_id,
        mes=frequencia.mes,
        ausencias=frequencia.ausencias
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@app.get("/frequencias", response_model=list[FrequenciaMensalResponse])
def listar_frequencias(db: Session = Depends(get_db)):
    return db.query(FrequenciaMensal).order_by(FrequenciaMensal.id.desc()).all()


@app.get("/fechamento/{mes}")
def fechamento_mensal(mes: str, db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).order_by(Funcionario.nome).all()
    resultado = []
    mes_formatado = formatar_mes_para_semana(mes)

    for funcionario in funcionarios:
        frequencia = (
            db.query(FrequenciaMensal)
            .filter(
                FrequenciaMensal.funcionario_id == funcionario.id,
                FrequenciaMensal.mes == mes
            )
            .first()
        )

        ausencias = frequencia.ausencias if frequencia else 0

        lancamentos = (
            db.query(LancamentoSemanal)
            .filter(
                LancamentoSemanal.funcionario_id == funcionario.id,
                LancamentoSemanal.semana.like(f"%{mes_formatado}")
            )
            .all()
        )

        bonus_final = calcular_bonus_mensal(lancamentos, ausencias)
        assiduidade = 150.0 if ausencias == 0 else 0.0

        resultado.append({
            "funcionario_id": funcionario.id,
            "funcionario": funcionario.nome,
            "cargo": funcionario.cargo,
            "mes": mes,
            "ausencias": ausencias,
            "quantidade_lancamentos": len(lancamentos),
            "bonus_final": bonus_final,
            "assiduidade": assiduidade,
            "elegivel": ausencias == 0
        })

    return resultado


@app.get("/exportar-fechamento/{mes}")
def exportar_excel_fechamento(mes: str, db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).order_by(Funcionario.nome).all()
    mes_formatado = formatar_mes_para_semana(mes)

    fechamento = []
    for funcionario in funcionarios:
        frequencia = (
            db.query(FrequenciaMensal)
            .filter(
                FrequenciaMensal.funcionario_id == funcionario.id,
                FrequenciaMensal.mes == mes
            )
            .first()
        )

        ausencias = frequencia.ausencias if frequencia else 0

        lancamentos_mes = (
            db.query(LancamentoSemanal)
            .filter(
                LancamentoSemanal.funcionario_id == funcionario.id,
                LancamentoSemanal.semana.like(f"%{mes_formatado}")
            )
            .all()
        )

        bonus_final = calcular_bonus_mensal(lancamentos_mes, ausencias)
        assiduidade = 150.0 if ausencias == 0 else 0.0

        fechamento.append({
            "funcionario_id": funcionario.id,
            "funcionario": funcionario.nome,
            "cargo": funcionario.cargo,
            "mes": mes,
            "ausencias": ausencias,
            "quantidade_lancamentos": len(lancamentos_mes),
            "bonus_final": bonus_final,
            "assiduidade": assiduidade,
            "elegivel": ausencias == 0
        })

    todos_lancamentos = (
        db.query(LancamentoSemanal)
        .filter(LancamentoSemanal.semana.like(f"%{mes_formatado}"))
        .order_by(LancamentoSemanal.id.desc())
        .all()
    )

    todas_frequencias = (
        db.query(FrequenciaMensal)
        .filter(FrequenciaMensal.mes == mes)
        .order_by(FrequenciaMensal.id.desc())
        .all()
    )

    arquivo = exportar_fechamento_excel(
        mes=mes,
        fechamento=fechamento,
        lancamentos=todos_lancamentos,
        frequencias=todas_frequencias,
        funcionarios=funcionarios
    )

    nome_arquivo = f"fechamento_{mes}.xlsx"

    return StreamingResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'}
    )