from faker import Faker
import pandas as pd
import os
import random

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

agentes = [
    "Ana Souza", "Bruno Lima", "Carla Mendes", "Diego Ferreira",
    "Eliane Costa", "Felipe Nunes", "Gisele Rocha", "Henrique Alves",
    "Isabela Martins", "João Pedro Silva", "Karina Oliveira", "Leonardo Santos",
    "Mariana Pereira", "Nelson Ribeiro", "Olivia Teixeira", "Paulo Gomes",
    "Renata Barros", "Sergio Campos",
]

os.makedirs("data", exist_ok=True)

datas = ["01052025", "02052025", "05052025"]

for data in datas:
    linhas_atendimentos = []
    for _ in range(random.randint(80, 150)):
        linhas_atendimentos.append({
            "Agente": random.choice(agentes),
            "Canal": random.choice(["WhatsApp", "Chat"]),
            "Status": random.choice(["Finalizado", "Perdido"]),
            "Duração": random.randint(1, 45),
        })
    pd.DataFrame(linhas_atendimentos).to_excel(f"data/atendimentos{data}.xlsx", index=False)

    linhas_envios = []
    for _ in range(random.randint(50, 100)):
        agente = random.choice(agentes)
        linhas_envios.append({
            "Agente": agente,
            "Mensagem": fake.sentence(),
            "Status": random.choice(["Entregue", "Lido", "Falhou"]),
        })
    pd.DataFrame(linhas_envios).to_excel(f"data/envios{data}.xlsx", index=False)

print("Dados mock gerados em /data")