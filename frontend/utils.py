from datetime import date, timedelta

API_URL = "http://127.0.0.1:8000"

def gerar_semana_mes(data_ref: date) -> str:
    primeiro_dia = data_ref.replace(day=1)

    dias_ate_domingo = 6 - primeiro_dia.weekday()
    if dias_ate_domingo < 0:
        dias_ate_domingo += 7

    fim_semana_1 = primeiro_dia + timedelta(days=dias_ate_domingo)

    if data_ref <= fim_semana_1:
        numero_semana = 1
    else:
        dias_restantes = (data_ref - fim_semana_1).days
        numero_semana = 1 + ((dias_restantes - 1) // 7) + 1

    return f"Semana {numero_semana} - {data_ref.strftime('%m/%Y')}"


def funcionario_recebe_entrega(tipo_entrega: str) -> bool:
    return tipo_entrega in ["Entrega", "Motorista", "Ajudante de motorista"]
