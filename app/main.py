from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import Base, engine, SessionLocal
from .models import Funcionario, LancamentoSemanal, FrequenciaMensal
from .schemas import (
    FuncionarioCreate,
    FuncionarioResponse,
    FuncionarioUpdate,
    LancamentoSemanalCreate,
    LancamentoMensalCreate,
    LancamentoSemanalResponse,
    FrequenciaMensalCreate,
    FrequenciaMensalResponse,
    LancamentoSemanalUpdate
)
from .calculos import calcular_bonus, calcular_bonus_mensal
from .export_excel import exportar_fechamento_excel
from datetime import date
from pathlib import Path
import json
import unicodedata

app = FastAPI(title="Sistema de Bonificação")

PROJECT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = PROJECT_DIR / "frontend-react" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

Base.metadata.create_all(bind=engine)


def garantir_colunas_frequencia():
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("ALTER TABLE frequencias_mensais ADD COLUMN IF NOT EXISTS status_mes TEXT DEFAULT 'Normal'"))
            conn.execute(text("ALTER TABLE frequencias_mensais ADD COLUMN IF NOT EXISTS data_falta DATE"))
            conn.execute(text("ALTER TABLE frequencias_mensais ADD COLUMN IF NOT EXISTS tipo_falta TEXT"))
            return

        if engine.dialect.name != "sqlite":
            return

        colunas = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(frequencias_mensais)"))
        }

        if "status_mes" not in colunas:
            conn.execute(text("ALTER TABLE frequencias_mensais ADD COLUMN status_mes TEXT DEFAULT 'Normal'"))
        if "data_falta" not in colunas:
            conn.execute(text("ALTER TABLE frequencias_mensais ADD COLUMN data_falta DATE"))
        if "tipo_falta" not in colunas:
            conn.execute(text("ALTER TABLE frequencias_mensais ADD COLUMN tipo_falta TEXT"))


garantir_colunas_frequencia()


def garantir_colunas_funcionario():
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("ALTER TABLE funcionarios ADD COLUMN IF NOT EXISTS turno TEXT DEFAULT 'Não informado'"))
            return

        if engine.dialect.name != "sqlite":
            return

        colunas = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(funcionarios)"))
        }

        if "turno" not in colunas:
            conn.execute(text("ALTER TABLE funcionarios ADD COLUMN turno TEXT DEFAULT 'Não informado'"))


garantir_colunas_funcionario()


def garantir_colunas_lancamento():
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS ajuste_personalizado_descricao TEXT"))
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS ajuste_personalizado_operacao TEXT"))
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS ajuste_personalizado_valor DOUBLE PRECISION DEFAULT 0"))
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS ajuste_personalizado_itens TEXT"))
            return

        if engine.dialect.name != "sqlite":
            return

        colunas = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(lancamentos_semanais)"))
        }

        if "ajuste_personalizado_descricao" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN ajuste_personalizado_descricao TEXT"))
        if "ajuste_personalizado_operacao" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN ajuste_personalizado_operacao TEXT"))
        if "ajuste_personalizado_valor" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN ajuste_personalizado_valor REAL DEFAULT 0"))
        if "ajuste_personalizado_itens" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN ajuste_personalizado_itens TEXT"))


garantir_colunas_lancamento()


def carregar_ajustes_personalizados(itens: str | None, criterio: str | None = None, operacao: str | None = None):
    if itens:
        try:
            dados = json.loads(itens)
            if isinstance(dados, list):
                return [
                    item for item in dados
                    if isinstance(item, dict) and item.get("criterio") and item.get("operacao")
                ]
        except json.JSONDecodeError:
            pass

    if criterio and operacao:
        return [{"criterio": criterio, "operacao": operacao}]

    return []


def formatar_mes_para_semana(mes: str) -> str:
    return f"{mes[5:7]}/{mes[:4]}"


def lancamento_pertence_ao_mes(lancamento: LancamentoSemanal, mes: str, mes_formatado: str) -> bool:
    if lancamento.data_lancamento and lancamento.data_lancamento.strftime("%Y-%m") == mes:
        return True

    return mes_formatado in (lancamento.semana or "")


def resumir_frequencias(frequencias: list[FrequenciaMensal]) -> tuple[int, str]:
    ausencias = sum(f.ausencias or 0 for f in frequencias)

    if ausencias > 0:
        return ausencias, "Normal"

    if any(f.status_mes == "Férias" for f in frequencias):
        return 0, "Férias"

    return 0, "Normal"


def normalizar_texto(valor: str) -> str:
    texto = (valor or "").strip().lower()
    return "".join(
        char for char in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(char)
    )


def turnos_do_filtro(filtro_turno: str) -> set[str]:
    return {normalizar_texto(filtro_turno)}


def funcionario_aplicavel_tipo(funcionario: Funcionario, tipo_funcionario: str) -> bool:
    tipo_entrega = normalizar_texto(funcionario.tipo_entrega)

    if normalizar_texto(tipo_funcionario) == "funcionario normal":
        return tipo_entrega in {"", "nao se aplica", "n?o se aplica"}
    if normalizar_texto(tipo_funcionario) == "entrega":
        return tipo_entrega in {"entrega", "motorista", "ajudante", "ajudante de motorista"}
    return tipo_entrega == normalizar_texto(tipo_funcionario)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return {"status": "Sistema rodando"}


@app.get("/health")
def health():
    return {"status": "Sistema rodando"}


@app.get("/logo.png", include_in_schema=False)
def frontend_logo():
    logo_path = FRONTEND_DIST / "logo.png"
    if logo_path.exists():
        return FileResponse(logo_path)
    raise HTTPException(status_code=404, detail="Logo nao encontrado.")


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
        tipo_entrega=funcionario.tipo_entrega,
        turno=funcionario.turno
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/funcionarios", response_model=list[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    return db.query(Funcionario).order_by(Funcionario.nome).all()


@app.put("/funcionarios/{funcionario_id}", response_model=FuncionarioResponse)
def editar_funcionario(
    funcionario_id: int,
    dados: FuncionarioUpdate,
    db: Session = Depends(get_db)
):
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    funcionario.nome = dados.nome
    funcionario.cargo = dados.cargo
    funcionario.ativo = dados.ativo
    funcionario.tipo_entrega = dados.tipo_entrega
    funcionario.turno = dados.turno

    db.commit()
    db.refresh(funcionario)

    return funcionario


@app.delete("/funcionarios/{funcionario_id}")
def excluir_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    total_lancamentos = (
        db.query(LancamentoSemanal)
        .filter(LancamentoSemanal.funcionario_id == funcionario_id)
        .delete()
    )
    total_frequencias = (
        db.query(FrequenciaMensal)
        .filter(FrequenciaMensal.funcionario_id == funcionario_id)
        .delete()
    )

    db.delete(funcionario)
    db.commit()

    return {
        "mensagem": "Funcionário excluído com sucesso.",
        "lancamentos_excluidos": total_lancamentos,
        "frequencias_excluidas": total_frequencias
    }


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
        penalidade=lancamento.penalidade,
        turno=funcionario.turno,
        criterio_personalizado=lancamento.ajuste_personalizado_descricao,
        operacao_personalizada=lancamento.ajuste_personalizado_operacao,
        ajustes_personalizados=carregar_ajustes_personalizados(
            lancamento.ajuste_personalizado_itens,
            lancamento.ajuste_personalizado_descricao,
            lancamento.ajuste_personalizado_operacao,
        ),
    )

    novo = LancamentoSemanal(
        funcionario_id=lancamento.funcionario_id,
        semana=lancamento.semana,
        tipo_lancamento=lancamento.tipo_lancamento,
        data_lancamento=lancamento.data_lancamento,
        data_registro=date.today(),
        usuario_lancamento=lancamento.usuario_lancamento,
        pedidos_separados=lancamento.pedidos_separados,
        pedidos_carregados=lancamento.pedidos_carregados,
        toneladas=lancamento.toneladas,
        entregas=lancamento.entregas,
        retornos=lancamento.retornos,
        nota=lancamento.nota,
        penalidade=lancamento.penalidade,
        motivo_penalidade=motivo_penalidade,
        ajuste_personalizado_descricao=lancamento.ajuste_personalizado_descricao,
        ajuste_personalizado_operacao=lancamento.ajuste_personalizado_operacao,
        ajuste_personalizado_valor=lancamento.ajuste_personalizado_valor,
        ajuste_personalizado_itens=lancamento.ajuste_personalizado_itens,
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
        penalidade=dados.penalidade,
        turno=funcionario.turno,
        criterio_personalizado=dados.ajuste_personalizado_descricao,
        operacao_personalizada=dados.ajuste_personalizado_operacao,
        ajustes_personalizados=carregar_ajustes_personalizados(
            dados.ajuste_personalizado_itens,
            dados.ajuste_personalizado_descricao,
            dados.ajuste_personalizado_operacao,
        ),
    )
        
    lancamento.semana = dados.semana
    lancamento.data_lancamento = dados.data_lancamento
    lancamento.pedidos_separados = dados.pedidos_separados
    lancamento.pedidos_carregados = dados.pedidos_carregados
    lancamento.toneladas = dados.toneladas
    lancamento.entregas = dados.entregas
    lancamento.retornos = dados.retornos
    lancamento.nota = dados.nota
    lancamento.penalidade = dados.penalidade
    lancamento.motivo_penalidade = dados.motivo_penalidade if dados.penalidade else None
    lancamento.ajuste_personalizado_descricao = dados.ajuste_personalizado_descricao
    lancamento.ajuste_personalizado_operacao = dados.ajuste_personalizado_operacao
    lancamento.ajuste_personalizado_valor = dados.ajuste_personalizado_valor
    lancamento.ajuste_personalizado_itens = dados.ajuste_personalizado_itens
    lancamento.bonus_calculado = bonus
    
    db.commit()
    db.refresh(lancamento)
    return lancamento


@app.post("/lancamentos-mensais", response_model=list[LancamentoSemanalResponse])
def criar_lancamento_mensal(
    lancamento: LancamentoMensalCreate,
    db: Session = Depends(get_db)
):
    turnos = turnos_do_filtro(lancamento.filtro_turno)
    funcionarios = (
        db.query(Funcionario)
        .filter(Funcionario.ativo == True)
        .order_by(Funcionario.nome)
        .all()
    )
    funcionarios_aplicaveis = [
        funcionario for funcionario in funcionarios
        if normalizar_texto(funcionario.turno) in turnos
        and funcionario_aplicavel_tipo(funcionario, lancamento.tipo_funcionario)
    ]

    if not funcionarios_aplicaveis:
        raise HTTPException(status_code=400, detail="Nenhum funcionário aplicável encontrado para os filtros.")

    semana = f"Mensal - {lancamento.mes[5:7]}/{lancamento.mes[:4]}"
    data_lancamento = date.fromisoformat(f"{lancamento.mes}-01")

    criados = []

    for funcionario in funcionarios_aplicaveis:
        nota = lancamento.notas.get(funcionario.id)
        if nota not in {1, 2, 3, 4, 5}:
            raise HTTPException(status_code=400, detail=f"Informe nota válida para {funcionario.nome}.")

        bonus = calcular_bonus(
            tipo_entrega=funcionario.tipo_entrega,
            pedidos_separados=lancamento.pedidos_separados,
            pedidos_carregados=lancamento.pedidos_carregados,
            toneladas=lancamento.toneladas,
            entregas=lancamento.entregas,
            retornos=lancamento.retornos,
            nota=nota,
            penalidade=False,
            turno=funcionario.turno
        )

        novo = LancamentoSemanal(
            funcionario_id=funcionario.id,
            semana=semana,
            tipo_lancamento="mensal",
            data_lancamento=data_lancamento,
            data_registro=date.today(),
            usuario_lancamento=lancamento.usuario_lancamento,
            pedidos_separados=lancamento.pedidos_separados,
            pedidos_carregados=lancamento.pedidos_carregados,
            toneladas=lancamento.toneladas,
            entregas=lancamento.entregas,
            retornos=lancamento.retornos,
            nota=nota,
            penalidade=False,
            motivo_penalidade=None,
            bonus_calculado=bonus
        )

        db.add(novo)
        criados.append(novo)

    db.commit()

    for criado in criados:
        db.refresh(criado)

    return criados

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

    tipos_falta_validos = {"Falta", "Atestado", "Licença legal"}

    if frequencia.status_mes == "Férias":
        frequencia.ausencias = 0
        frequencia.data_falta = None
        frequencia.tipo_falta = None
    elif frequencia.ausencias > 0:
        if not frequencia.data_falta:
            raise HTTPException(status_code=400, detail="Informe o dia da falta.")
        if frequencia.tipo_falta not in tipos_falta_validos:
            raise HTTPException(status_code=400, detail="Informe um tipo de falta válido.")
        frequencia.mes = frequencia.data_falta.strftime("%Y-%m")
    else:
        frequencia.data_falta = None
        frequencia.tipo_falta = None

    existente = (
        db.query(FrequenciaMensal)
        .filter(
            FrequenciaMensal.funcionario_id == frequencia.funcionario_id,
            FrequenciaMensal.mes == frequencia.mes,
            FrequenciaMensal.data_falta == frequencia.data_falta
        )
        .first()
    )

    if existente:
        existente.ausencias = frequencia.ausencias
        existente.status_mes = frequencia.status_mes
        existente.data_falta = frequencia.data_falta
        existente.tipo_falta = frequencia.tipo_falta

        db.commit()
        db.refresh(existente)
        return existente

    nova = FrequenciaMensal(
        funcionario_id=frequencia.funcionario_id,
        mes=frequencia.mes,
        ausencias=frequencia.ausencias,
        data_falta=frequencia.data_falta,
        tipo_falta=frequencia.tipo_falta,
        status_mes=frequencia.status_mes
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@app.get("/frequencias", response_model=list[FrequenciaMensalResponse])
def listar_frequencias(db: Session = Depends(get_db)):
    return db.query(FrequenciaMensal).order_by(FrequenciaMensal.id.desc()).all()


@app.put("/frequencias/{frequencia_id}", response_model=FrequenciaMensalResponse)
def editar_frequencia(
    frequencia_id: int,
    dados: FrequenciaMensalCreate,
    db: Session = Depends(get_db)
):
    frequencia = (
        db.query(FrequenciaMensal)
        .filter(FrequenciaMensal.id == frequencia_id)
        .first()
    )

    if not frequencia:
        raise HTTPException(status_code=404, detail="Frequência não encontrada.")

    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == dados.funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    tipos_falta_validos = {"Falta", "Atestado", "Licença legal"}

    if dados.status_mes == "Férias":
        dados.ausencias = 0
        dados.data_falta = None
        dados.tipo_falta = None
    elif dados.ausencias > 0:
        if not dados.data_falta:
            raise HTTPException(status_code=400, detail="Informe o dia da falta.")
        if dados.tipo_falta not in tipos_falta_validos:
            raise HTTPException(status_code=400, detail="Informe um tipo de falta válido.")
        dados.mes = dados.data_falta.strftime("%Y-%m")
    else:
        dados.data_falta = None
        dados.tipo_falta = None

    frequencia.funcionario_id = dados.funcionario_id
    frequencia.mes = dados.mes
    frequencia.ausencias = dados.ausencias
    frequencia.data_falta = dados.data_falta
    frequencia.tipo_falta = dados.tipo_falta
    frequencia.status_mes = dados.status_mes

    db.commit()
    db.refresh(frequencia)
    return frequencia


@app.delete("/frequencias/{frequencia_id}")
def excluir_frequencia(
    frequencia_id: int,
    db: Session = Depends(get_db)
):
    frequencia = (
        db.query(FrequenciaMensal)
        .filter(FrequenciaMensal.id == frequencia_id)
        .first()
    )

    if not frequencia:
        raise HTTPException(status_code=404, detail="Frequência não encontrada.")

    db.delete(frequencia)
    db.commit()
    return {"mensagem": "Frequência excluída com sucesso."}


@app.get("/fechamento/{mes}")
def fechamento_mensal(mes: str, db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).order_by(Funcionario.nome).all()
    resultado = []
    mes_formatado = formatar_mes_para_semana(mes)

    for funcionario in funcionarios:
        frequencias = (
            db.query(FrequenciaMensal)
            .filter(
                FrequenciaMensal.funcionario_id == funcionario.id,
                FrequenciaMensal.mes == mes
            )
            .all()
        )

        ausencias, status_mes = resumir_frequencias(frequencias)

        lancamentos_funcionario = (
            db.query(LancamentoSemanal)
            .filter(LancamentoSemanal.funcionario_id == funcionario.id)
            .all()
        )
        lancamentos = [
            lancamento for lancamento in lancamentos_funcionario
            if lancamento_pertence_ao_mes(lancamento, mes, mes_formatado)
        ]

        if status_mes == "Férias":
            bonus_final = 0.0
            assiduidade = 0.0
            elegivel = True
            ausencias = 0
        else:
            bonus_final = calcular_bonus_mensal(lancamentos, ausencias)
            assiduidade = 150.0 if ausencias == 0 else 0.0
            elegivel = ausencias == 0

        resultado.append({
            "funcionario_id": funcionario.id,
            "funcionario": funcionario.nome,
            "cargo": funcionario.cargo,
            "mes": mes,
            "ausencias": ausencias,
            "quantidade_lancamentos": len(lancamentos),
            "bonus_final": bonus_final,
            "assiduidade": assiduidade,
            "elegivel": elegivel,
            "status_mes": status_mes
        })

    return resultado


@app.get("/exportar-fechamento/{mes}")
def exportar_excel_fechamento(mes: str, db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).order_by(Funcionario.nome).all()
    mes_formatado = formatar_mes_para_semana(mes)

    fechamento = []
    for funcionario in funcionarios:
        frequencias_funcionario = (
            db.query(FrequenciaMensal)
            .filter(
                FrequenciaMensal.funcionario_id == funcionario.id,
                FrequenciaMensal.mes == mes
            )
            .all()
        )

        ausencias, status_mes = resumir_frequencias(frequencias_funcionario)

        lancamentos_funcionario = (
            db.query(LancamentoSemanal)
            .filter(LancamentoSemanal.funcionario_id == funcionario.id)
            .all()
        )
        lancamentos_mes = [
            lancamento for lancamento in lancamentos_funcionario
            if lancamento_pertence_ao_mes(lancamento, mes, mes_formatado)
        ]

        if status_mes == "Férias":
            bonus_final = 0.0
            assiduidade = 0.0
            elegivel = True
            ausencias = 0
        
        else:
            bonus_final = calcular_bonus_mensal(lancamentos_mes, ausencias)
            assiduidade = 150.0 if ausencias == 0 else 0.0
            elegivel = ausencias == 0

        fechamento.append({
            "funcionario_id": funcionario.id,
            "funcionario": funcionario.nome,
            "cargo": funcionario.cargo,
            "mes": mes,
            "ausencias": ausencias,
            "quantidade_lancamentos": len(lancamentos_mes),
            "bonus_final": bonus_final,
            "assiduidade": assiduidade,
            "elegivel": elegivel,
            "status_mes": status_mes
        })

    todos_lancamentos = [
        lancamento for lancamento in (
        db.query(LancamentoSemanal)
        .order_by(LancamentoSemanal.id.desc())
        .all()
        )
        if lancamento_pertence_ao_mes(lancamento, mes, mes_formatado)
    ]

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


@app.get("/{full_path:path}", include_in_schema=False)
def frontend_app(full_path: str):
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    raise HTTPException(status_code=404, detail="Frontend nao compilado.")
