#Interface visual para o usuário final. Integra backend e gráficos
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import nutricao

# Configuração
st.set_page_config(page_title="GlicConnect Simulator", layout="wide")

class SimuladorGlicemia:
    """Motor de simulação temporal (Time-Series) para visualização gráfica."""
    def __init__(self, peso):
        self.tdd = 0.55 * peso
        self.isf = 1800 / self.tdd
        self.icr = 500 / self.tdd
        self.time_steps = np.arange(0, 300, 1) # 5 horas

    def _gamma_curve(self, t, t_max, total):
        if t < 0 or t_max == 0: return 0
        return (total * t / (t_max**2)) * np.exp(-t / t_max)

    def run(self, glicemia_ini, carbos, insulina):
        curve = np.zeros_like(self.time_steps, dtype=float)
        
        total_rise = carbos * (self.isf / self.icr)
        total_drop = insulina * self.isf
        
        cum_rise, cum_drop = 0, 0
        
        for i, t in enumerate(self.time_steps):
            cum_rise += self._gamma_curve(t, 60.0, total_rise)
            cum_drop += self._gamma_curve(t, 75.0, total_drop)
            curve[i] = max(0, glicemia_ini + cum_rise - cum_drop)
            
        return self.time_steps, curve

# --- Interface ---
st.title("📊 Simulador Glicêmico")

with st.sidebar:
    st.header("Paciente")
    peso = st.number_input("Peso (kg)", 30.0, 150.0, 70.0)
    sim = SimuladorGlicemia(peso)
    st.caption(f"ISF: {sim.isf:.0f} | ICR: 1:{sim.icr:.0f}")
    
    st.divider()
    hora_ref = st.time_input("Hora Início", value=datetime.now().time())

col1, col2, col3 = st.columns(3)

with col1:
    glicemia = st.number_input("Glicemia Atual", 50, 400, 150)

with col2:
    busca = st.text_input("Buscar Alimento (TACO)")
    carbos_100g = 0.0
    
    if busca:
        res = nutricao.buscar_alimentos(busca)
        if not res.empty:
            nome = st.selectbox("Selecione:", res['Nome'].tolist())
            carbos_100g = res[res['Nome'] == nome].iloc[0]['Carboidratos']
            st.caption(f"Carbos: {carbos_100g:.1f}g / 100g")
    
    gramas = st.number_input("Quantidade (g)", 0, 1000, 100)
    total_carbos = (carbos_100g * gramas) / 100

with col3:
    st.metric("Total Carboidratos", f"{total_carbos:.1f} g")
    sugestao = total_carbos / sim.icr if sim.icr > 0 else 0
    dose = st.number_input("Dose Insulina (U)", 0.0, 50.0, float(round(sugestao, 1)))

if st.button("Simular", type="primary"):
    _, y_curve = sim.run(glicemia, total_carbos, dose)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    x_labels = [(datetime.combine(date.today(), hora_ref) + timedelta(minutes=int(t))).strftime("%H:%M") for t in range(0, 301, 60)]
    
    ax.plot(y_curve, color='#2980b9', lw=2)
    ax.set_xticks(range(0, 301, 60))
    ax.set_xticklabels(x_labels)
    ax.axhline(70, c='red', ls='--', alpha=0.5); ax.axhline(180, c='orange', ls='--', alpha=0.5)
    ax.set_title(f"Projeção: {total_carbos:.1f}g Carbo + {dose}U Insulina")
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)