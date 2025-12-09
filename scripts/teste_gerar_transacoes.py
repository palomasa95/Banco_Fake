import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import sys

# Aumenta o limite de campo para o CSV (importante para arquivos grandes)
csv.field_size_limit = sys.maxsize 

# --- CONFIGURAÇÃO DE TESTE ---
NUM_TRANSACOES = 1_000          # TESTE: Apenas mil transações
CHUNK_SIZE = 1_000             # Chunk size igual ao total para escrever tudo de uma vez
NOME_ARQUIVO_TRANSACOES = 'TRANSACOES_TESTE.csv'
ARQUIVO_CONTAS = 'banco_fake/CONTAS.csv'
LOCALE = 'pt_BR'

fake = Faker(LOCALE)
TIPOS_TRANSACAO = ['Depósito', 'Saque', 'TED', 'Pix', 'Compra Débito']

# --- FUNÇÕES DE LEITURA (INALTERADAS) ---

def ler_contas():
    """Lê todas as contas e suas datas de abertura."""
    contas = {}
    try:
        with open(ARQUIVO_CONTAS, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Pula o cabeçalho
            for row in reader:
                conta_id = int(row[0])
                data_abertura_str = row[4] # Data de abertura está na coluna 4
                contas[conta_id] = datetime.strptime(data_abertura_str, '%Y-%m-%d')
        print(f"Lidas {len(contas)} contas ativas.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de contas não encontrado em '{ARQUIVO_CONTAS}'.")
        return None
    return contas

# --- FUNÇÕES DE GERAÇÃO (INALTERADAS) ---

def gerar_destino(tipo):
    """Simula o destino ou origem da transação."""
    if tipo in ['TED', 'Pix']:
        return fake.name()
    elif tipo == 'Compra Débito':
        return random.choice(['Supermercado X', 'Farmácia Y', 'Posto Z'])
    else:
        return 'Interno' # Saque/Depósito

def gerar_transacao(conta_id, data_abertura):
    """Gera uma única linha de transação."""
    
    # 1. Definir o tipo e valor
    tipo = random.choice(TIPOS_TRANSACAO)
    
    if tipo in ['Saque', 'Compra Débito']:
        valor = round(random.uniform(10, 500), 2)
    elif tipo == 'Depósito':
        valor = round(random.uniform(50, 5000), 2)
    else: # TED, Pix
        valor = round(random.uniform(100, 10000), 2)

    # 2. Definir a Data/Hora
    data_maxima = datetime.now() - timedelta(days=7) # Transações até uma semana atrás
    
    # Garantir que a transação é posterior à abertura da conta
    data_inicio_valida = data_abertura + timedelta(days=30) # A conta precisa de 30 dias de vida para ter movimento
    
    # Garantir que o start_date < end_date
    data_inicio_faker = data_inicio_valida
    if data_inicio_valida > data_maxima:
        # Se a conta é muito nova, ajusta o início para que o intervalo seja válido (pelo menos 1 dia)
        data_inicio_faker = data_maxima - timedelta(days=1)
        
    data_hora = fake.date_time_between_dates(
        datetime_start=data_inicio_faker, 
        datetime_end=data_maxima
    ).strftime('%Y-%m-%d %H:%M:%S')

    # 3. Gerar a linha
    return [
        conta_id,
        tipo,
        valor,
        data_hora,
        gerar_destino(tipo)
    ]

# --- EXECUÇÃO PRINCIPAL ---

contas_data = ler_contas()

if contas_data:
    lista_ids = list(contas_data.keys())
    
    # O arquivo será escrito dentro de 'banco_fake/'
    caminho_saida = f"banco_fake/{NOME_ARQUIVO_TRANSACOES}"
    
    print(f"Iniciando a geração de {NUM_TRANSACOES} transações...")
    
    try:
        with open(caminho_saida, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Escreve o cabeçalho
            writer.writerow(['transacao_id', 'conta_id', 'tipo', 'valor', 'data_hora', 'destino'])
            
            dados_chunk = []
            transacao_id_counter = 1
            
            # Loop principal de geração
            for i in range(1, NUM_TRANSACOES + 1):
                
                # Seleciona uma conta ID aleatória
                conta_id = random.choice(lista_ids)
                data_abertura = contas_data[conta_id]
                
                # Gera a transação
                transacao_linha = gerar_transacao(conta_id, data_abertura)
                
                # Adiciona o ID da transação
                dados_chunk.append([transacao_id_counter] + transacao_linha)
                
                transacao_id_counter += 1
                
                # Como o CHUNK_SIZE é igual ao NUM_TRANSACOES, ele escreve tudo no final
                if i % CHUNK_SIZE == 0 or i == NUM_TRANSACOES:
                    writer.writerows(dados_chunk)
                    dados_chunk = []
                    
        print(f"\n✅ Concluído! Arquivo '{caminho_saida}' criado com {NUM_TRANSACOES} transações de teste.")

    except Exception as e:
        print(f"\nERRO FATAL DURANTE A ESCRITA: {e}")
