from datetime import datetime

# Constantes Médicas
TDD_FACTOR = 0.55  # Total Daily Dose Factor (Units/kg)
ISF_CONST = 1800   # Rule of 1800
ICR_CONST = 500    # Rule of 500

def calcular_iob(dose: float, hora_app_str: str, duracao_h: int = 4) -> float:
    """Calcula Insulina Ativa (Decaimento Quadrático)."""
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

def prever_glicemia_pontual(glicemia_atual: float, peso: float, total_carbos: float, iob: float) -> float:
    """Predição matemática pontual (Estado Final)."""
    if peso <= 0: return glicemia_atual

    tdd = peso * TDD_FACTOR
    isf = ISF_CONST / tdd
    icr = ICR_CONST / tdd
    
    delta_comida = (total_carbos / icr) * isf
    delta_insulina = iob * isf
    
    return max(20.0, glicemia_atual + delta_comida - delta_insulina)