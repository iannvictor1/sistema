import unicodedata
import json


def normalizar_texto(valor: str) -> str:
    texto = (valor or "").strip().lower()
    return "".join(
        char for char in unicodedata.normalize("NFD", texto)
        if unicodedata.category(char) != "Mn"
    )


def recebe_bonus_entrega(tipo_entrega: str) -> bool:
    tipo = normalizar_texto(tipo_entrega)

    tipos_validos = {
        "entrega",
        "motorista",
        "ajudante",
        "ajudante de motorista",
    }

    return tipo in tipos_validos


def normalizar_turno(turno: str) -> str:
    return normalizar_texto(turno)


def calcular_bonus(
    tipo_entrega: str,
    pedidos_separados: int,
    pedidos_carregados: int,
    toneladas: float,
    entregas: int,
    retornos: int,
    nota: int,
    penalidade: bool,
    turno: str = "Nao informado",
    criterio_personalizado: str | None = None,
    operacao_personalizada: str | None = None,
    ajustes_personalizados: list[dict] | None = None,
) -> float:
    turno_normalizado = normalizar_turno(turno)
    ajustes = ajustes_personalizados or []

    if not ajustes and criterio_personalizado and operacao_personalizada:
        ajustes = [{"criterio": criterio_personalizado, "operacao": operacao_personalizada}]

    criterios_adicionados = {
        normalizar_texto(item.get("criterio"))
        for item in ajustes
        if normalizar_texto(item.get("operacao")) == "adicionar"
    }
    criterios_removidos = {
        normalizar_texto(item.get("criterio"))
        for item in ajustes
        if normalizar_texto(item.get("operacao")) == "retirar"
    }
    criterios_adicionados.discard("")
    criterios_removidos.discard("")

    if turno_normalizado == "horario comercial":
        return 0.0

    funcionario_entrega = recebe_bonus_entrega(tipo_entrega)
    turno_sem_regra = turno_normalizado not in {"manha", "tarde", "noite"}

    usar_toneladas = "toneladas" not in criterios_removidos and (
        (not funcionario_entrega and (turno_sem_regra or turno_normalizado == "manha"))
        or "toneladas" in criterios_adicionados
    )
    usar_pedidos_separados = "pedidos_separados" not in criterios_removidos and (
        (not funcionario_entrega and (turno_sem_regra or turno_normalizado == "tarde"))
        or "pedidos_separados" in criterios_adicionados
    )
    usar_pedidos_carregados = "pedidos_carregados" not in criterios_removidos and (
        (not funcionario_entrega and (turno_sem_regra or turno_normalizado == "noite"))
        or "pedidos_carregados" in criterios_adicionados
    )
    usar_entregas = "entregas" not in criterios_removidos and (
        funcionario_entrega or "entregas" in criterios_adicionados
    )
    usar_retornos = "retornos" not in criterios_removidos and (
        funcionario_entrega or "retornos" in criterios_adicionados
    )

    ganho = 0
    if usar_toneladas:
        ganho += toneladas * 2.00
    if usar_pedidos_separados:
        ganho += pedidos_separados * 0.10
    if usar_pedidos_carregados:
        ganho += pedidos_carregados * 0.10
    if usar_entregas:
        ganho += entregas * 0.30
    if usar_retornos:
        ganho -= retornos * 0.60

    if penalidade:
        ganho *= 0.5

    base = max(0, ganho)

    fatores = {
        5: 1.0,
        4: 0.9,
        3: 0.8,
        2: 0.5,
        1: 0.2,
    }

    fator = fatores.get(nota, 0)
    return round(base * fator, 2)


def fator_da_nota(nota: int | None) -> float:
    fatores = {
        5: 1.0,
        4: 0.9,
        3: 0.8,
        2: 0.5,
        1: 0.2,
    }
    return fatores.get(nota, 0)


def calcular_bonus_recebimento_toneladas(toneladas: float, nota: int = 5) -> float:
    return calcular_bonus(
        tipo_entrega="Nao se aplica",
        pedidos_separados=0,
        pedidos_carregados=0,
        toneladas=toneladas or 0,
        entregas=0,
        retornos=0,
        nota=nota,
        penalidade=False,
        turno="Manha",
    )


def carregar_ajustes_personalizados_lancamento(lancamento) -> list[dict]:
    itens = getattr(lancamento, "ajuste_personalizado_itens", None)
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

    criterio = getattr(lancamento, "ajuste_personalizado_descricao", None)
    operacao = getattr(lancamento, "ajuste_personalizado_operacao", None)
    if criterio and operacao:
        return [{"criterio": criterio, "operacao": operacao}]

    return []


def calcular_base_lancamento(lancamento, funcionario=None) -> float:
    if normalizar_texto(getattr(lancamento, "tipo_lancamento", "")) == "recebimento_toneladas":
        return calcular_bonus_recebimento_toneladas(getattr(lancamento, "toneladas", 0), nota=5)

    funcionario = funcionario or getattr(lancamento, "funcionario", None)
    tipo_entrega = getattr(funcionario, "tipo_entrega", "") if funcionario else ""
    turno = getattr(funcionario, "turno", "Nao informado") if funcionario else "Nao informado"

    return calcular_bonus(
        tipo_entrega=tipo_entrega,
        pedidos_separados=lancamento.pedidos_separados or 0,
        pedidos_carregados=lancamento.pedidos_carregados or 0,
        toneladas=lancamento.toneladas or 0,
        entregas=lancamento.entregas or 0,
        retornos=lancamento.retornos or 0,
        nota=5,
        penalidade=bool(lancamento.penalidade),
        turno=turno,
        criterio_personalizado=getattr(lancamento, "ajuste_personalizado_descricao", None),
        operacao_personalizada=getattr(lancamento, "ajuste_personalizado_operacao", None),
        ajustes_personalizados=carregar_ajustes_personalizados_lancamento(lancamento),
    )


def calcular_bonus_mensal(lancamentos, ausencias: int, nota_atual: int | None = None, funcionario=None) -> float:
    if ausencias > 0:
        return 0.0

    lancamentos_producao = [
        lancamento for lancamento in lancamentos
        if normalizar_texto(getattr(lancamento, "tipo_lancamento", "")) != "avaliacao_semanal"
    ]

    if nota_atual is None:
        total = sum(l.bonus_calculado for l in lancamentos_producao)
    else:
        base_periodo = sum(calcular_base_lancamento(l, funcionario) for l in lancamentos_producao)
        total = base_periodo * fator_da_nota(nota_atual)

    total += 150.0
    return round(total, 2)
