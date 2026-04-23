def cargo_recebe_entrega(cargo: str) -> bool:
    cargo_normalizado = cargo.strip().lower()

    cargos_validos = {
        "motorista",
        "ajudante",
        "ajudante de motorista",
        "ajudante motorista",
    }

    return cargo_normalizado in cargos_validos


def calcular_bonus(
    cargo: str,
    pedidos_separados: int,
    pedidos_carregados: int,
    toneladas: float,
    entregas: int,
    retornos: int,
    nota: int,
    penalidade: bool
) -> float:
    valor_entregas = entregas * 0.30 if cargo_recebe_entrega(cargo) else 0.0

    ganho = (
        pedidos_separados * 0.10 +
        pedidos_carregados * 0.10 +
        toneladas * 2.00 +
        valor_entregas
    )

    if penalidade:
        ganho *= 0.5

    perda = retornos * 0.60
    base = max(0, ganho - perda)

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
    total += 150.0  # saldo fixo de assiduidade
    return round(total, 2)