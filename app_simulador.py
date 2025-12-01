import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import nutricao

# Configuração
st.set_page_config(page_title="GlicConnect Simulator", layout="wide")

class MotorSimulacao:
    """Motor de Série Temporal (Lógica baseada na Função Gamma)."""
    def __init__(self, peso):
        self.tdd = 0.55 * peso
        self.isf = 1800 / self.tdd
        self.icr = 500 / self.tdd
        self.time_steps = np.arange(0, 300, 1) # 5 horas

    def _gamma_curve(self, t, t_max, total):
        if t < 0 or t_max == 0: return 0
        return (total * t / (t_max**2)) * np.exp(-t / t_max)

    def executar(self, glicemia_ini, carbos, insulina, t_max_carbo):
        curve = np.zeros_like(self.time_steps, dtype=float)
        
        total_rise = carbos * (self.isf / self.icr)
        total_drop = insulina * self.isf
        
        cum_rise, cum_drop = 0, 0
        
        for i, t in enumerate(self.time_steps):
            cum_rise += self._gamma_curve(t, t_max_carbo, total_rise)
            cum_drop += self._gamma_curve(t, 55.0, total_drop) # 55min pico insulina
            curve[i] = max(0, glicemia_ini + cum_rise - cum_drop)
            
        return self.time_steps, curve

# --- UI ---
st.title("📊 Simulador Glicêmico Inteligente")
st.markdown("Integração: **TACO** (Dados) + **Heurística Nutricional** (IG) + **Farmacocinética** (Curvas).")

with st.sidebar:
    st.header("Paciente")
    peso = st.number_input("Peso (kg)", 30.0, 150.0, 70.0)
    sim = MotorSimulacao(peso)
    st.info(f"ISF: {sim.isf:.0f} | ICR: 1:{sim.icr:.0f}")
    st.divider()
    hora_ref = st.time_input("Hora Início", value=datetime.now().time())

col1, col2, col3 = st.columns(3)

with col1:
    glicemia = st.number_input("Glicemia (mg/dL)", 50, 500, 150)

with col2:
    busca = st.text_input("Buscar Alimento", placeholder="Ex: Arroz, Feijão...")
    carbos_100g = 0.0
    t_pico = 60.0
    nome = "Personalizado"
    
    if busca:
        res = nutricao.buscar_alimentos(busca)
        if not res.empty:
            nome = st.selectbox("Selecione:", res['Nome'].tolist())
            detalhes = nutricao.get_detalhes_alimento(nome)
            
            carbos_100g = detalhes['carbo_100g']
            ig = detalhes['ig_class']
            
            # Feedback Automático
            st.caption(f"Carbo: {carbos_100g:.1f}% | Fibra: {detalhes['fibra_100g']:.1f}%")
            if ig == 'A': 
                st.warning("⚡ Absorção Rápida"); t_pico = 40.0
            elif ig == 'B': 
                st.success("🐢 Absorção Lenta"); t_pico = 90.0
            else: 
                st.info("⚖️ Absorção Média"); t_pico = 60.0
    
    gramas = st.number_input("Quantidade (g)", 0, 1000, 100)
    total_carbos = (carbos_100g * gramas) / 100

with col3:
    st.metric("Total Carbo", f"{total_carbos:.1f} g")
    sugestao = total_carbos / sim.icr
    dose = st.number_input("Dose Insulina (U)", 0.0, 50.0, float(round(sugestao, 1)))

if st.button("Simular", type="primary"):
    _, y = sim.executar(glicemia, total_carbos, dose, t_pico)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    x_lbl = [(datetime.combine(date.today(), hora_ref) + timedelta(minutes=int(t))).strftime("%H:%M") for t in range(0, 301, 60)]
    
    ax.plot(y, color='#2980b9', lw=2)
    ax.set_xticks(range(0, 301, 60)); ax.set_xticklabels(x_lbl)
    ax.axhspan(70, 180, color='green', alpha=0.1)
    ax.axhline(70, c='red', ls='--'); ax.axhline(180, c='orange', ls='--')
    ax.set_title(f"Projeção: {gramas}g de {nome}")
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)