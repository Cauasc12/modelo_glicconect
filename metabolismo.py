#Cálculos matemáticos puros (IOB e Previsão).
from datetime import datetime

def calcular_iob(dose: float, hora_app_str: str, duracao_h: int = 4) -> float:
    """Calcula Insulina Ativa (IOB) usando modelo de decaimento quadrático."""
    try:
        agora = datetime.now()
        dt_app = datetime.strptime(hora_app_str, "%H:%M").replace(
            year=agora.year, month=agora.month, day=agora.day
        )
        
        minutos = (agora - dt_app).total_seconds() / 60
        duracao_min = duracao_h * 60
        
        if not (0 <= minutos < duracao_min):
            return 0.0
        
        return dose * ((1 - (minutos / duracao_min)) ** 2)
    except ValueError:
        return 0.0

def prever_glicemia(glicemia_atual: float, peso: float, total_carbos: float, iob: float) -> float:
    """
    Predição pontual baseada em Fator de Sensibilidade (1800) e Razão Carbo (500).
    """
    if peso <= 0: return glicemia_atual

    # Estimativa de Dose Diária Total (TDD)
    tdd = peso * 0.55
    
    isf = 1800 / tdd  # Insulin Sensitivity Factor
    icr = 500 / tdd   # Insulin-to-Carb Ratio
    
    delta_comida = (total_carbos / icr) * isf
    delta_insulina = iob * isf
    
    return max(20.0, glicemia_atual + delta_comida - delta_insulina)