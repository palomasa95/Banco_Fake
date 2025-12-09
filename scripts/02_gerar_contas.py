import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# --- CONFIGURAÇÃO ---
NOME_ARQUIVO_CONTAS = 'CONTAS.csv'
ARQUIVO_CLIENTES = 'banco_fake/clientes.csv'
LOCALE = 'pt_BR'

fake = Faker(LOCALE)
TIPOS_CONTA = ['Corrente', 'Poupança', 'Investimento', 'Empresarial']

# --- FUNÇÕES ---

def ler_clientes():
    """Lê os clientes e retorna um dicionário {id: data_nascimento}."""
    clientes = {}
    
    # Define o caminho do arquivo de clientes a partir do diretório atual (Dados/)
    caminho_clientes = ARQUIVO_CLIENTES
    
    try:
        with open(caminho_clientes, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Pula o cabeçalho
            for row in reader:
                cliente_id = int(row[0])
                data_nascimento_str = row[2] # A data de nascimento está na coluna 2
                
                # Guarda o ID e a data de nascimento para referência
                clientes[cliente_id] = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
        print(f"Lidos {len(clientes)} clientes.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de clientes não encontrado em '{caminho_clientes}'.")
        return None
    return clientes

def gerar_data_abertura(data_nascimento):
    """Gera uma data de abertura de conta que é pelo menos 18 anos após o nascimento do cliente."""
    
    # O cliente só pode abrir conta após a maioridade (18 anos)
    data_minima = data_nascimento + timedelta(days=365 * 18)
    data_maxima = datetime.now() - timedelta(days=30) # A conta não pode ter sido aberta hoje/nos últimos 30 dias
    
    # Se a data mínima for no futuro (cliente muito novo), ajusta para a data máxima.
    if data_minima > data_maxima:
        return data_maxima.strftime('%Y-%m-%d')
    
    return fake.date_between(start_date=data_minima, end_date=data_maxima).strftime('%Y-%m-%d')

def gerar_saldo(tipo_conta):
    """Gera um saldo inicial baseado no tipo de conta."""
    if tipo_conta == 'Corrente':
        # Saldo com média próxima de 3k (pode ser negativo)
        saldo = random.gauss(3000, 5000)
    elif tipo_conta == 'Poupança':
        # Saldo com média mais alta
        saldo = random.gauss(8000, 6000)
    elif tipo_conta == 'Investimento':
        # Saldo com média muito alta
        saldo = random.gauss(50000, 25000)
    else: # Empresarial/Outros
        saldo = random.gauss(15000, 10000)
    
    return round(saldo, 2)

# --- EXECUÇÃO PRINCIPAL ---

clientes_data = ler_clientes()

if clientes_data:
    dados_contas = []
    
    cabecalho = [
        'conta_id', 'cliente_id', 'tipo_conta', 
        'saldo_atual', 'data_abertura'
    ]
    dados_contas.append(cabecalho)
    
    conta_id_counter = 1
    
    print("Gerando contas...")
    
    for cliente_id, data_nascimento in clientes_data.items():
        # Cada cliente terá aleatoriamente entre 1 e 3 contas
        num_contas = random.choice([1, 1, 1, 2, 2, 3]) # Distribuição: mais clientes com 1 ou 2 contas
        
        for _ in range(num_contas):
            tipo = random.choice(TIPOS_CONTA)
            saldo = gerar_saldo(tipo)
            data_abertura = gerar_data_abertura(data_nascimento)
            
            dados_contas.append([
                conta_id_counter,
                cliente_id,
                tipo,
                saldo,
                data_abertura
            ])
            
            conta_id_counter += 1

    # --- EXPORTAÇÃO PARA CSV ---
    
    # O arquivo será escrito dentro de 'banco_fake/'
    caminho_saida = f"{ARQUIVO_CLIENTES.split('/')[0]}/{NOME_ARQUIVO_CONTAS}"
    
    # Obtém o total de linhas geradas (excluindo o cabeçalho)
    total_contas = len(dados_contas) - 1 
    
    try:
        with open(caminho_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(dados_contas)
        
        print(f"Sucesso! Arquivo '{caminho_saida}' criado com {total_contas} contas.")

    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")
