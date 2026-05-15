def recebe_bonus_entrega(tipo_entrega: str) -> bool:
    tipo = (tipo_entrega or "").strip().lower()

    tipos_validos = {
        "entrega",
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
    turno: str = "Nao informado"
) -> float:
    turno_normalizado = normalizar_turno(turno)

    if turno_normalizado in {"manhã", "manha"}:
        ganho = toneladas * 2.00
    elif turno_normalizado == "tarde":
        ganho = pedidos_separados * 0.10
    elif turno_normalizado == "noite":
        ganho = pedidos_carregados * 0.10
    else:
        ganho = (
            pedidos_separados * 0.10 +
            pedidos_carregados * 0.10 +
            toneladas * 2.00
        )

    if recebe_bonus_entrega(tipo_entrega):
        ganho += entregas * 0.30
        ganho -= retornos * 0.60

    if penalidade:
        ganho *= 0.5

    base = max(0, ganho)

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
