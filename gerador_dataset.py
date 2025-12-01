#Criar dados sintéticos para treino da IA
import pandas as pd
import random
from datetime import datetime
import nutricao
import metabolismo

CONFIG = {
    'samples': 5000,
    'output': 'dataset_glicemia_treino.csv',
    'foods': [
        "Arroz, integral, cozido", "Feijão, carioca, cozido", 
        "Pão, de trigo, francês", "Banana, prata, crua",
        "Leite, de vaca, integral", "Maçã, Fuji, com casca, crua"
    ]
}

def gerar_dataset():
    dados = []
    print(f"Gerando {CONFIG['samples']} amostras...")

    for _ in range(CONFIG['samples']):
        peso = random.randint(45, 110)
        glicemia_ini = random.randint(70, 350)
        alimento = random.choice(CONFIG['foods'])
        gramas = random.randint(50, 400)
        
        tem_insulina = random.choice([True, False])
        dose = random.randint(2, 15) if tem_insulina else 0
        min_atras = random.randint(30, 240) if tem_insulina else 0
        hora_fake = (datetime.now() - pd.Timedelta(minutes=min_atras)).strftime("%H:%M")

        carbos = nutricao.get_carboidratos(alimento, gramas)
        if carbos is None: continue

        iob = metabolismo.calcular_iob(dose, hora_fake) if tem_insulina else 0.0
        
        # Ruído estocástico (5%)
        ruido = random.uniform(0.95, 1.05)
        target = metabolismo.prever_glicemia(glicemia_ini, peso, carbos, iob) * ruido

        dados.append({
            'peso': peso,
            'glicemia_inicial': glicemia_ini,
            'carbos_total': round(carbos, 1),
            'insulina_ativa': round(iob, 2),
            'target_glicemia': round(target, 0)
        })

    pd.DataFrame(dados).to_csv(CONFIG['output'], index=False)
    print(f"Dataset salvo: {CONFIG['output']}")

if __name__ == "__main__":
    gerar_dataset()