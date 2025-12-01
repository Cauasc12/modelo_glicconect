#Validar, limpar e normalizar dados para o modelo
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

FILES = {
    'input': "dataset_glicemia_treino.csv",
    'output': "dataset_processado_normalizado.csv"
}

def processar_dados():
    try:
        df = pd.read_csv(FILES['input'])
    except FileNotFoundError:
        print("Dataset de entrada não encontrado.")
        return

    # 1. Limpeza
    df.dropna(inplace=True)
    df = df[(df['target_glicemia'] >= 20) & (df['target_glicemia'] <= 600)]
    
    # 2. EDA (Visualização)
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df, x='carbos_total', y='target_glicemia', hue='insulina_ativa', alpha=0.6)
    plt.tight_layout()
    plt.show()

    # 3. Normalização (Z-Score)
    features = ['peso', 'glicemia_inicial', 'carbos_total', 'insulina_ativa']
    scaler = StandardScaler()
    
    df_norm = df.copy()
    df_norm[features] = scaler.fit_transform(df[features])

    df_norm.to_csv(FILES['output'], index=False)
    print(f"Processamento concluído: {FILES['output']}")

if __name__ == "__main__":
    processar_dados()