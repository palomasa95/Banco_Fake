import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# --- CONFIGURAÇÃO ---
NUM_CLIENTES = 12000
NOME_ARQUIVO = 'CLIENTES.csv'
LOCALE = 'pt_BR'

# Inicializa o Faker
fake = Faker(LOCALE)

# Definições de Domínios para Renda e Ocupação (para simular realidade)
OCUPACOES = [
    'CLT', 'Autônomo', 'Funcionário Público', 
    'Empresário', 'Estudante', 'Aposentado'
]

# Definir a data mínima e máxima de nascimento (18 a 75 anos)
def gerar_data_nascimento():
    hoje = datetime.now()
    min_idade = hoje - timedelta(days=365 * 75)
    max_idade = hoje - timedelta(days=365 * 18)
    return fake.date_between(start_date=min_idade, end_date=max_idade).strftime('%Y-%m-%d')

# Definir a faixa de renda com alguma variação
def gerar_renda():
    # Renda base simulando 2k a 8k, com desvio padrão
    return round(random.gauss(5000, 3000), 2)

# --- GERAÇÃO DE DADOS ---
dados_clientes = []

# Define o cabeçalho do CSV
cabecalho = [
    'cliente_id', 'nome_completo', 'data_nascimento', 
    'ocupacao', 'renda_mensal', 'cidade', 'estado', 'cpf'
]
dados_clientes.append(cabecalho)

print(f"Gerando {NUM_CLIENTES} registros...")

for i in range(1, NUM_CLIENTES + 1):
    renda = gerar_renda()
    
    # Simula distribuição realista: a maioria tem renda positiva
    if renda < 1000:
        # Pessoas com renda muito baixa (Estudantes, Aposentados com baixo benefício)
        renda = random.randint(500, 1500)
    
    # Ajusta a ocupação de forma semi-realista
    if renda > 15000:
        ocupacao = random.choice(['Empresário', 'CLT'])
    elif renda < 2000:
        ocupacao = random.choice(['Estudante', 'Aposentado'])
    else:
        ocupacao = random.choice(OCUPACOES)
        
    
    # Monta a linha de dados
    dados_clientes.append([
        i,  # cliente_id
        fake.name(),
        gerar_data_nascimento(),
        ocupacao,
        round(renda, 2),
        fake.city(),
        fake.state_abbr(),
        fake.cpf()
    ])

print(f"Geração concluída. Escrevendo no arquivo {NOME_ARQUIVO}...")

# --- EXPORTAÇÃO PARA CSV ---
try:
    with open(NOME_ARQUIVO, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(dados_clientes)
    
    print(f"Sucesso! Arquivo '{NOME_ARQUIVO}' criado com {NUM_CLIENTES} clientes.")

except Exception as e:
    print(f"Erro ao escrever no arquivo: {e}")
