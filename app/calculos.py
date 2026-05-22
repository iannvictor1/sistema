import unicodedata


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


def calcular_bonus_mensal(lancamentos, ausencias: int) -> float:
    if ausencias > 0:
        return 0.0

    total = sum(l.bonus_calculado for l in lancamentos)
    total += 150.0
    return round(total, 2)
