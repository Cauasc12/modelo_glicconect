import pandas as pd
import os
from typing import Optional, Dict

# Constantes de Caminho
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(_BASE_DIR, 'alimentos.csv')

def _load_database() -> pd.DataFrame:
    """Carrega a TACO e normaliza colunas (Carbo, Fibra, Gordura)."""
    if not os.path.exists(_CSV_PATH): return pd.DataFrame()
    
    try:
        # Tenta UTF-8 e separador virgula, fallback para Latin1 e ponto-e-vírgula
        df = pd.read_csv(_CSV_PATH, na_values='NA', sep=',', encoding='utf-8')
        if len(df.columns) <= 1:
            df = pd.read_csv(_CSV_PATH, na_values='NA', sep=';', encoding='latin1')

        # Mapeamento dinâmico
        mapa = {'nome': None, 'carbo': None, 'fibra': None, 'gordura': None}
        for col in df.columns:
            c = col.lower().strip()
            if "descri" in c and "alimento" in c: mapa['nome'] = col
            elif "carbo" in c: mapa['carbo'] = col
            elif "fibra" in c: mapa['fibra'] = col
            elif "lipídeo" in c or "gordura" in c: mapa['gordura'] = col
            
        if not mapa['nome'] or not mapa['carbo']: return pd.DataFrame()

        # Seleção e Renomeação
        cols = [mapa['nome'], mapa['carbo']]
        names = ['Nome', 'Carboidratos']
        
        if mapa['fibra']: 
            cols.append(mapa['fibra']); names.append('Fibras')
        if mapa['gordura']: 
            cols.append(mapa['gordura']); names.append('Gorduras')
            
        df = df[cols].copy()
        df.columns = names
        
        # Coerção Numérica
        for c in ['Carboidratos', 'Fibras', 'Gorduras']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
        return df
    except Exception:
        return pd.DataFrame()

TABELA_NUTRI = _load_database()

def buscar_alimentos(termo: str) -> pd.DataFrame:
    if TABELA_NUTRI.empty: return pd.DataFrame()
    return TABELA_NUTRI[TABELA_NUTRI['Nome'].str.lower().str.contains(termo.lower(), na=False)]

def estimar_ig(nome: str, carbo: float, fibra: float, gordura: float) -> str:
    """
    Aplica HEURÍSTICA para definir o Índice Glicêmico (A/M/B).
    Regras: Low Carb, Relação Fibra/Carbo, Gordura e Palavras-chave.
    """
    nome = nome.lower()
    
    # 1. Low Carb absoluto
    if carbo < 5: return 'B' 

    # 2. Fibra retarda absorção (>15% do carbo)
    if carbo > 0 and (fibra / carbo) > 0.15: return 'B'

    # 3. Gordura atrasa esvaziamento gástrico
    if gordura > 10: return 'M'

    # 4. Palavras-chave
    termos_alto = ['açúcar', 'doce', 'bala', 'refinado', 'mel', 'suco', 'branco']
    if any(t in nome for t in termos_alto): return 'A'

    termos_baixo = ['integral', 'aveia', 'semente', 'cru', 'folha', 'legume']
    if any(t in nome for t in termos_baixo): return 'B'

    return 'M' # Padrão

def get_detalhes_alimento(nome_exato: str) -> Dict:
    """Retorna payload completo do alimento com classificação de IG."""
    if TABELA_NUTRI.empty: return {}
    item = TABELA_NUTRI[TABELA_NUTRI['Nome'] == nome_exato]
    if item.empty: return {}
    
    dados = item.iloc[0]
    info = {
        'carbo_100g': dados['Carboidratos'],
        'fibra_100g': dados.get('Fibras', 0),
        'gordura_100g': dados.get('Gorduras', 0)
    }
    info['ig_class'] = estimar_ig(nome_exato, info['carbo_100g'], info['fibra_100g'], info['gordura_100g'])
    return info