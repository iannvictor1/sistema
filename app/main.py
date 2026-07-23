from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import Base, engine, SessionLocal
from .models import Funcionario, LancamentoSemanal, RecebimentoToneladas, FrequenciaMensal, DescontoFechamento
from .schemas import (
    FuncionarioCreate,
    FuncionarioResponse,
    FuncionarioUpdate,
    LancamentoSemanalCreate,
    LancamentoMensalCreate,
    LancamentoSemanalResponse,
    FrequenciaMensalCreate,
    FrequenciaMensalResponse,
    LancamentoSemanalUpdate,
    RecebimentoToneladasCreate,
    RecebimentoToneladasResponse,
    RecebimentoParticipantesUpdate,
    DescontoFechamentoCreate,
    DescontoFechamentoResponse
)
from .calculos import calcular_bonus, calcular_bonus_mensal
from .export_excel import exportar_fechamento_excel
from datetime import date
from pathlib import Path
import json
import unicodedata
import base64
import binascii

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
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS numero_carregamento TEXT"))
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS numero_nota_fiscal TEXT"))
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS nota_fiscal_pdf TEXT"))
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN IF NOT EXISTS nota_fiscal_pdf_nome TEXT"))
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
        if "numero_carregamento" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN numero_carregamento TEXT"))
        if "numero_nota_fiscal" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN numero_nota_fiscal TEXT"))
        if "nota_fiscal_pdf" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN nota_fiscal_pdf TEXT"))
        if "nota_fiscal_pdf_nome" not in colunas:
            conn.execute(text("ALTER TABLE lancamentos_semanais ADD COLUMN nota_fiscal_pdf_nome TEXT"))


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


LIMITE_PDF_NOTA_FISCAL = 10 * 1024 * 1024


def validar_pdf_nota_fiscal(pdf_base64: str | None) -> str | None:
    if not pdf_base64:
        return None

    try:
        conteudo = base64.b64decode(pdf_base64, validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(status_code=400, detail="O arquivo da nota fiscal estÃ¡ invÃ¡lido.")

    if len(conteudo) > LIMITE_PDF_NOTA_FISCAL:
        raise HTTPException(status_code=400, detail="O PDF da nota fiscal deve ter no mÃ¡ximo 10 MB.")
    if not conteudo.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="O anexo da nota fiscal deve ser um arquivo PDF.")

    return pdf_base64


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


def nota_atual_lancamentos(lancamentos: list[LancamentoSemanal]) -> int | None:
    avaliacoes = [
        lancamento for lancamento in lancamentos
        if normalizar_texto(lancamento.tipo_lancamento) == "avaliacao_semanal"
    ]
    if not avaliacoes:
        return None

    lancamento_atual = max(
        avaliacoes,
        key=lambda lancamento: (
            lancamento.data_lancamento or date.min,
            lancamento.data_registro or date.min,
            lancamento.id or 0,
        ),
    )
    return lancamento_atual.nota


def lancamento_conta_producao(lancamento: LancamentoSemanal) -> bool:
    return normalizar_texto(lancamento.tipo_lancamento) not in {
        "avaliacao_semanal",
    }


def desconto_por_funcionario(db: Session, mes: str) -> dict[int, DescontoFechamento]:
    descontos = (
        db.query(DescontoFechamento)
        .filter(DescontoFechamento.mes == mes)
        .all()
    )
    return {desconto.funcionario_id: desconto for desconto in descontos}


def aplicar_desconto_fechamento(bonus_bruto: float, desconto: DescontoFechamento | None) -> tuple[float, float, str | None]:
    valor_desconto = max(0.0, float(getattr(desconto, "valor", 0) or 0))
    motivo_desconto = getattr(desconto, "motivo", None) if desconto else None
    bonus_final = max(0.0, round(float(bonus_bruto or 0) - valor_desconto, 2))
    return bonus_final, valor_desconto, motivo_desconto


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


def funcionario_recebe_por_toneladas(funcionario: Funcionario) -> bool:
    tipo_entrega = normalizar_texto(funcionario.tipo_entrega)
    return normalizar_texto(funcionario.turno) == "manha" and tipo_entrega not in {
        "entrega",
        "motorista",
        "ajudante",
        "ajudante de motorista",
    }


def usuario_supervisor(usuario: str | None) -> bool:
    return normalizar_texto(usuario) in {
        "admin",
        "iann",
        "valesca",
        "paulo",
        "romario",
        "gabriel",
        "junior",
    }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def usuario_da_requisicao(valor_payload: str | None, request: Request) -> str | None:
    usuario = (valor_payload or "").strip()
    if usuario:
        return usuario

    usuario_header = (request.headers.get("X-Bonificacao-User") or "").strip()
    return usuario_header or None


def exigir_funcionario_ativo(funcionario: Funcionario):
    if not funcionario.ativo:
        raise HTTPException(
            status_code=400,
            detail="Funcionario inativo nao pode receber lancamentos, frequencias ou descontos."
        )


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
    total_descontos = (
        db.query(DescontoFechamento)
        .filter(DescontoFechamento.funcionario_id == funcionario_id)
        .delete()
    )

    db.delete(funcionario)
    db.commit()

    return {
        "mensagem": "Funcionário excluído com sucesso.",
        "lancamentos_excluidos": total_lancamentos,
        "frequencias_excluidas": total_frequencias,
        "descontos_excluidos": total_descontos
    }


@app.post("/lancamentos-semanais", response_model=LancamentoSemanalResponse)
def criar_lancamento_semanal(
    lancamento: LancamentoSemanalCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    tipo_lancamento = normalizar_texto(lancamento.tipo_lancamento or "semanal")
    usuario_lancamento = usuario_da_requisicao(lancamento.usuario_lancamento, request)
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == lancamento.funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    exigir_funcionario_ativo(funcionario)

    if (
        tipo_lancamento in {"semanal", "diario"}
        and funcionario_recebe_por_toneladas(funcionario)
        and not usuario_supervisor(usuario_lancamento)
    ):
        raise HTTPException(
            status_code=400,
            detail="Funcionarios que recebem por toneladas devem ser lancados apenas em Recebimento de toneladas."
        )

    if tipo_lancamento == "avaliacao_semanal" and lancamento.nota not in {1, 2, 3, 4, 5}:
        raise HTTPException(status_code=400, detail="Informe uma nota valida entre 1 e 5.")

    if lancamento.penalidade and not lancamento.motivo_penalidade:
        raise HTTPException(status_code=400, detail="Informe o motivo da penalidade.")

    if not lancamento.penalidade:
        motivo_penalidade = None
    else:
        motivo_penalidade = lancamento.motivo_penalidade

    nota = lancamento.nota if tipo_lancamento == "avaliacao_semanal" else 5
    if tipo_lancamento == "avaliacao_semanal":
        bonus = 0.0
    else:
        bonus = calcular_bonus(
            tipo_entrega=funcionario.tipo_entrega,
            pedidos_separados=lancamento.pedidos_separados,
            pedidos_carregados=lancamento.pedidos_carregados,
            toneladas=lancamento.toneladas,
            entregas=lancamento.entregas,
            retornos=lancamento.retornos,
            nota=5,
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
        usuario_lancamento=usuario_lancamento,
        pedidos_separados=lancamento.pedidos_separados,
        pedidos_carregados=lancamento.pedidos_carregados,
        toneladas=lancamento.toneladas,
        numero_carregamento=(lancamento.numero_carregamento or "").strip() or None,
        numero_nota_fiscal=(lancamento.numero_nota_fiscal or "").strip() or None,
        nota_fiscal_pdf=validar_pdf_nota_fiscal(lancamento.nota_fiscal_pdf),
        nota_fiscal_pdf_nome=(lancamento.nota_fiscal_pdf_nome or "").strip() or None,
        entregas=lancamento.entregas,
        retornos=lancamento.retornos,
        nota=nota,
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


@app.post("/recebimentos-toneladas", response_model=RecebimentoToneladasResponse)
def criar_recebimento_toneladas(
    recebimento: RecebimentoToneladasCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    if recebimento.toneladas <= 0:
        raise HTTPException(status_code=400, detail="Informe uma quantidade de toneladas maior que zero.")

    novo = RecebimentoToneladas(
        semana=recebimento.semana,
        data_lancamento=recebimento.data_lancamento,
        data_registro=date.today(),
        usuario_lancamento=usuario_da_requisicao(recebimento.usuario_lancamento, request),
        toneladas=recebimento.toneladas,
        numero_carregamento=(recebimento.numero_carregamento or "").strip() or None,
        numero_nota_fiscal=(recebimento.numero_nota_fiscal or "").strip() or None,
        nota_fiscal_pdf=validar_pdf_nota_fiscal(recebimento.nota_fiscal_pdf),
        nota_fiscal_pdf_nome=(recebimento.nota_fiscal_pdf_nome or "").strip() or None,
        status="pendente",
        participantes=None,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/recebimentos-toneladas", response_model=list[RecebimentoToneladasResponse])
def listar_recebimentos_toneladas(db: Session = Depends(get_db)):
    return db.query(RecebimentoToneladas).order_by(RecebimentoToneladas.id.desc()).all()


@app.post("/recebimentos-toneladas/{recebimento_id}/participantes", response_model=list[LancamentoSemanalResponse])
def confirmar_participantes_recebimento(
    recebimento_id: int,
    dados: RecebimentoParticipantesUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    recebimento = (
        db.query(RecebimentoToneladas)
        .filter(RecebimentoToneladas.id == recebimento_id)
        .first()
    )
    if not recebimento:
        raise HTTPException(status_code=404, detail="Recebimento nao encontrado.")
    if recebimento.status == "distribuido":
        raise HTTPException(status_code=400, detail="Este recebimento ja foi distribuido.")

    funcionario_ids = list(dict.fromkeys(dados.funcionario_ids))
    if not funcionario_ids:
        raise HTTPException(status_code=400, detail="Selecione ao menos um participante.")

    funcionarios = (
        db.query(Funcionario)
        .filter(Funcionario.id.in_(funcionario_ids), Funcionario.ativo == True)
        .all()
    )
    if len(funcionarios) != len(funcionario_ids):
        raise HTTPException(status_code=400, detail="Todos os participantes precisam ser funcionarios ativos.")

    usuario = usuario_da_requisicao(dados.usuario_lancamento, request)
    criados = []
    for funcionario in funcionarios:
        bonus = calcular_bonus(
            tipo_entrega=funcionario.tipo_entrega,
            pedidos_separados=0,
            pedidos_carregados=0,
            toneladas=recebimento.toneladas,
            entregas=0,
            retornos=0,
            nota=5,
            penalidade=False,
            turno=funcionario.turno,
        )
        novo = LancamentoSemanal(
            funcionario_id=funcionario.id,
            semana=recebimento.semana,
            tipo_lancamento="recebimento_toneladas",
            data_lancamento=recebimento.data_lancamento,
            data_registro=date.today(),
            usuario_lancamento=usuario,
            pedidos_separados=0,
            pedidos_carregados=0,
            toneladas=recebimento.toneladas,
            numero_carregamento=recebimento.numero_carregamento,
            numero_nota_fiscal=recebimento.numero_nota_fiscal,
            nota_fiscal_pdf=recebimento.nota_fiscal_pdf,
            nota_fiscal_pdf_nome=recebimento.nota_fiscal_pdf_nome,
            entregas=0,
            retornos=0,
            nota=5,
            penalidade=False,
            motivo_penalidade=None,
            bonus_calculado=bonus,
        )
        db.add(novo)
        criados.append(novo)

    recebimento.status = "distribuido"
    recebimento.participantes = json.dumps(funcionario_ids)
    db.commit()

    for criado in criados:
        db.refresh(criado)
    return criados


@app.get("/lancamentos-semanais/{lancamento_id}/nota-fiscal")
def baixar_nota_fiscal(lancamento_id: int, db: Session = Depends(get_db)):
    lancamento = db.query(LancamentoSemanal).filter(LancamentoSemanal.id == lancamento_id).first()
    if not lancamento or not lancamento.nota_fiscal_pdf:
        raise HTTPException(status_code=404, detail="Nota fiscal nÃ£o encontrada.")

    try:
        conteudo = base64.b64decode(lancamento.nota_fiscal_pdf, validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(status_code=500, detail="O PDF armazenado estÃ¡ invÃ¡lido.")

    return Response(
        content=conteudo,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="nota-fiscal-{lancamento.id}.pdf"'},
    )


@app.put("/lancamentos-semanais/{lancamento_id}", response_model=LancamentoSemanalResponse)
def editar_lancamento_semanal(
    lancamento_id: int,
    dados: LancamentoSemanalUpdate,
    request: Request,
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
    

    exigir_funcionario_ativo(funcionario)

    tipo_lancamento = normalizar_texto(lancamento.tipo_lancamento or "semanal")
    usuario_edicao = usuario_da_requisicao(None, request) or lancamento.usuario_lancamento
    if (
        tipo_lancamento in {"semanal", "diario"}
        and funcionario_recebe_por_toneladas(funcionario)
        and not usuario_supervisor(usuario_edicao)
    ):
        raise HTTPException(
            status_code=400,
            detail="Funcionarios que recebem por toneladas devem ser lancados apenas em Recebimento de toneladas."
        )

    if tipo_lancamento == "avaliacao_semanal" and dados.nota not in {1, 2, 3, 4, 5}:
        raise HTTPException(status_code=400, detail="Informe uma nota valida entre 1 e 5.")

    if dados.penalidade and not dados.motivo_penalidade:
        raise HTTPException(status_code=400, detail="Informe o motivo da penalidade.")

    nota = dados.nota if tipo_lancamento == "avaliacao_semanal" else 5
    if tipo_lancamento == "avaliacao_semanal":
        bonus = 0.0
    else:
        bonus = calcular_bonus(
            tipo_entrega=funcionario.tipo_entrega,
            pedidos_separados=dados.pedidos_separados,
            pedidos_carregados=dados.pedidos_carregados,
            toneladas=dados.toneladas,
            entregas=dados.entregas,
            retornos=dados.retornos,
            nota=5,
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
    lancamento.numero_carregamento = (dados.numero_carregamento or "").strip() or None
    lancamento.numero_nota_fiscal = (dados.numero_nota_fiscal or "").strip() or None
    if dados.nota_fiscal_pdf:
        lancamento.nota_fiscal_pdf = validar_pdf_nota_fiscal(dados.nota_fiscal_pdf)
        lancamento.nota_fiscal_pdf_nome = (dados.nota_fiscal_pdf_nome or "").strip() or "nota-fiscal.pdf"
    lancamento.entregas = dados.entregas
    lancamento.retornos = dados.retornos
    lancamento.nota = nota
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
    request: Request,
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
            usuario_lancamento=usuario_da_requisicao(lancamento.usuario_lancamento, request),
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

    exigir_funcionario_ativo(funcionario)

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

    exigir_funcionario_ativo(funcionario)

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


@app.post("/descontos-fechamento", response_model=DescontoFechamentoResponse)
def salvar_desconto_fechamento(
    desconto: DescontoFechamentoCreate,
    db: Session = Depends(get_db)
):
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == desconto.funcionario_id)
        .first()
    )

    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionario nao encontrado.")

    exigir_funcionario_ativo(funcionario)

    if len(desconto.mes or "") != 7:
        raise HTTPException(status_code=400, detail="Informe o mes no formato AAAA-MM.")

    if desconto.valor < 0:
        raise HTTPException(status_code=400, detail="O desconto nao pode ser negativo.")

    existente = (
        db.query(DescontoFechamento)
        .filter(
            DescontoFechamento.funcionario_id == desconto.funcionario_id,
            DescontoFechamento.mes == desconto.mes
        )
        .first()
    )
    motivo = (desconto.motivo or "").strip() or None

    if existente:
        existente.valor = desconto.valor
        existente.motivo = motivo
        db.commit()
        db.refresh(existente)
        return existente

    novo = DescontoFechamento(
        funcionario_id=desconto.funcionario_id,
        mes=desconto.mes,
        valor=desconto.valor,
        motivo=motivo
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.delete("/descontos-fechamento/{mes}/{funcionario_id}")
def excluir_desconto_fechamento(
    mes: str,
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    desconto = (
        db.query(DescontoFechamento)
        .filter(
            DescontoFechamento.funcionario_id == funcionario_id,
            DescontoFechamento.mes == mes
        )
        .first()
    )

    if not desconto:
        return {"mensagem": "Nenhum desconto cadastrado para remover."}

    db.delete(desconto)
    db.commit()
    return {"mensagem": "Desconto removido."}


@app.get("/fechamento/{mes}")
def fechamento_mensal(mes: str, db: Session = Depends(get_db)):
    funcionarios = (
        db.query(Funcionario)
        .filter(Funcionario.ativo == True)
        .order_by(Funcionario.nome)
        .all()
    )
    resultado = []
    mes_formatado = formatar_mes_para_semana(mes)
    descontos_mapa = desconto_por_funcionario(db, mes)

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
        lancamentos_producao = [
            lancamento for lancamento in lancamentos
            if lancamento_conta_producao(lancamento)
        ]

        if status_mes == "Férias":
            nota_atual = nota_atual_lancamentos(lancamentos)
            bonus_bruto = 0.0
            assiduidade = 0.0
            elegivel = True
            ausencias = 0
        else:
            nota_atual = nota_atual_lancamentos(lancamentos)
            bonus_bruto = calcular_bonus_mensal(lancamentos_producao, ausencias, nota_atual, funcionario)
            assiduidade = 150.0 if ausencias == 0 else 0.0
            elegivel = ausencias == 0

        bonus_final, desconto, motivo_desconto = aplicar_desconto_fechamento(
            bonus_bruto,
            descontos_mapa.get(funcionario.id)
        )

        resultado.append({
            "funcionario_id": funcionario.id,
            "funcionario": funcionario.nome,
            "cargo": funcionario.cargo,
            "mes": mes,
            "ausencias": ausencias,
            "quantidade_lancamentos": len(lancamentos_producao),
            "nota_atual": nota_atual,
            "bonus_bruto": bonus_bruto,
            "desconto": desconto,
            "motivo_desconto": motivo_desconto,
            "bonus_final": bonus_final,
            "assiduidade": assiduidade,
            "elegivel": elegivel,
            "status_mes": status_mes
        })

    return resultado


@app.get("/exportar-fechamento/{mes}")
def exportar_excel_fechamento(mes: str, request: Request, db: Session = Depends(get_db)):
    funcionarios = (
        db.query(Funcionario)
        .filter(Funcionario.ativo == True)
        .order_by(Funcionario.nome)
        .all()
    )
    funcionario_ids_ativos = {funcionario.id for funcionario in funcionarios}
    mes_formatado = formatar_mes_para_semana(mes)
    descontos_mapa = desconto_por_funcionario(db, mes)

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
        lancamentos_producao = [
            lancamento for lancamento in lancamentos_mes
            if lancamento_conta_producao(lancamento)
        ]
        nota_atual = nota_atual_lancamentos(lancamentos_mes)

        if status_mes == "Férias":
            bonus_bruto = 0.0
            assiduidade = 0.0
            elegivel = True
            ausencias = 0
        
        else:
            nota_atual = nota_atual_lancamentos(lancamentos_mes)
            bonus_bruto = calcular_bonus_mensal(lancamentos_producao, ausencias, nota_atual, funcionario)
            assiduidade = 150.0 if ausencias == 0 else 0.0
            elegivel = ausencias == 0

        bonus_final, desconto, motivo_desconto = aplicar_desconto_fechamento(
            bonus_bruto,
            descontos_mapa.get(funcionario.id)
        )

        fechamento.append({
            "funcionario_id": funcionario.id,
            "funcionario": funcionario.nome,
            "cargo": funcionario.cargo,
            "mes": mes,
            "ausencias": ausencias,
            "quantidade_lancamentos": len(lancamentos_producao),
            "nota_atual": nota_atual,
            "bonus_bruto": bonus_bruto,
            "desconto": desconto,
            "motivo_desconto": motivo_desconto,
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
        if lancamento.funcionario_id in funcionario_ids_ativos
        and lancamento_pertence_ao_mes(lancamento, mes, mes_formatado)
    ]

    todas_frequencias = (
        db.query(FrequenciaMensal)
        .filter(
            FrequenciaMensal.mes == mes,
            FrequenciaMensal.funcionario_id.in_(funcionario_ids_ativos)
        )
        .order_by(FrequenciaMensal.id.desc())
        .all()
    )

    arquivo = exportar_fechamento_excel(
        mes=mes,
        fechamento=fechamento,
        lancamentos=todos_lancamentos,
        frequencias=todas_frequencias,
        funcionarios=funcionarios,
        base_url=str(request.base_url).rstrip("/")
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
