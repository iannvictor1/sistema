def recebe_bonus_entrega(tipo_entrega: str) -> bool:
    tipo = (tipo_entrega or "").strip().lower()

    tipos_validos = {
        "motorista",
        "ajudante",
        "ajudante de motorista",
    }

    return tipo in tipos_validos


def normalizar_turno(turno: str) -> str:
    return (turno or "").strip().lower()


def calcular_bonus(
    tipo_entrega: str,
    pedidos_separados: int,
    pedidos_carregados: int,
    toneladas: float,
    entregas: int,
    retornos: int,
    nota: int,
    penalidade: bool,
    turno: str = "Não informado"
) -> float:
    valor_entregas = 0.0
    perda_retornos = 0.0

    if recebe_bonus_entrega(tipo_entrega):
        valor_entregas = entregas * 0.30
        perda_retornos = retornos * 0.60

    if recebe_bonus_entrega(tipo_entrega):
        ganho = valor_entregas
    else:
        turno_normalizado = normalizar_turno(turno)

        if turno_normalizado in {"manhã", "manha", "tarde"}:
            ganho = pedidos_separados * 0.10 + toneladas * 2.00
        elif turno_normalizado == "noite":
            ganho = pedidos_carregados * 0.10
        else:
            ganho = (
                pedidos_separados * 0.10 +
                pedidos_carregados * 0.10 +
                toneladas * 2.00
            )

    if penalidade:
        ganho *= 0.5

    perda = retornos * 0.60 if recebe_bonus_entrega(tipo_entrega) else 0.0
    base = max(0, ganho - perda_retornos)

    fatores = {
        5: 1.0,
        4: 0.9,
        3: 0.8,
        2: 0.5,
        1: 0.2
    }

    fator = fatores.get(nota, 0)
    return round(base * fator, 2)


def calcular_bonus_mensal(lancamentos, ausencias: int) -> float:
    if ausencias > 0:
        return 0.0

    total = sum(l.bonus_calculado for l in lancamentos)
    total += 150.0
    return round(total, 2)
