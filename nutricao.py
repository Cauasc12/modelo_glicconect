#Acesso e normalização da base de dados TACO.
import pandas as pd
import os
from typing import Optional

# Singleton: Carrega a tabela apenas uma vez na memória
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(_BASE_DIR, 'alimentos.csv')

def _load_database() -> pd.DataFrame:
    if not os.path.exists(_CSV_PATH):
        return pd.DataFrame()
    
    try:
        # Tenta UTF-8/Vírgula, fallback para Latin1/Ponto-e-vírgula
        df = pd.read_csv(_CSV_PATH, na_values='NA', sep=',', encoding='utf-8')
        if len(df.columns) <= 1:
            df = pd.read_csv(_CSV_PATH, na_values='NA', sep=';', encoding='latin1')

        # Normalização de colunas
        col_name, col_carb = None, None
        for col in df.columns:
            clean = col.lower().strip()
            if "descri" in clean and "alimento" in clean: col_name = col
            elif "carbo" in clean: col_carb = col
        
        if not col_name or not col_carb: return pd.DataFrame()

        df = df[[col_name, col_carb]].copy()
        df.columns = ['Nome', 'Carboidratos']
        df['Carboidratos'] = pd.to_numeric(df['Carboidratos'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame()

TABELA_NUTRI = _load_database()

def buscar_alimentos(termo: str) -> pd.DataFrame:
    """Retorna DataFrame filtrado por substring (case-insensitive)."""
    if TABELA_NUTRI.empty: return pd.DataFrame()
    return TABELA_NUTRI[TABELA_NUTRI['Nome'].str.lower().str.contains(termo.lower(), na=False)]

def get_carboidratos(nome_exato: str, peso_gramas: float) -> Optional[float]:
    """Calcula carboidratos totais para um peso específico."""
    if TABELA_NUTRI.empty: return 0.0
    item = TABELA_NUTRI[TABELA_NUTRI['Nome'] == nome_exato]
    if item.empty: return None
    return (item['Carboidratos'].values[0] / 100) * peso_gramas